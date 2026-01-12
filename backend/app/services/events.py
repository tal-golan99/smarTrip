"""
Event Service (Phase 1)
=======================

Handles event tracking with:
- Real IP extraction (supports Vercel/Render load balancers)
- Device type from frontend (not user-agent parsing)
- User/session resolution
- Event validation and storage
- Trip interaction updates
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from uuid import UUID
import uuid

from app.core.database import SessionLocal
from app.models.events import User, Session, Event, TripInteraction, EventType


# ============================================
# EVENT TYPE CONFIGURATION
# ============================================

# Event type to category mapping
EVENT_CATEGORIES = {
    # Navigation events
    'page_view': 'navigation',
    
    # Search events
    'search_submit': 'search',
    'results_view': 'search',
    'filter_change': 'search',
    'filter_removed': 'search',  # NEW: When user clears a filter
    'sort_change': 'search',
    
    # Engagement events
    'impression': 'engagement',
    'click_trip': 'engagement',
    'trip_view': 'engagement',
    'trip_dwell_time': 'engagement',  # NEW: Time spent on trip page
    'scroll_depth': 'engagement',
    
    # Conversion events
    'save_trip': 'conversion',
    'unsave_trip': 'conversion',
    'contact_whatsapp': 'conversion',
    'contact_phone': 'conversion',
    'booking_start': 'conversion',
    'share_trip': 'conversion',
}

# Valid event types
VALID_EVENT_TYPES = set(EVENT_CATEGORIES.keys())

# Valid source values for click attribution
VALID_SOURCES = {'search_results', 'relaxed_results', 'homepage', 'similar', 'saved'}


# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_real_ip(request) -> Optional[str]:
    """
    Extract real client IP address, handling load balancers.
    
    Supports Vercel, Render, Cloudflare, and other reverse proxies
    that set X-Forwarded-For header.
    
    Args:
        request: Flask request object
        
    Returns:
        Client IP address or None (validated for PostgreSQL INET type)
    """
    ip_str = None
    
    # Check X-Forwarded-For first (set by load balancers)
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs: "client, proxy1, proxy2"
        # The first one is the original client
        ip_str = forwarded_for.split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        # Fallback headers used by various proxies
        ip_str = request.headers.get('X-Real-IP').strip()
    elif request.headers.get('CF-Connecting-IP'):
        # CF-Connecting-IP for Cloudflare
        ip_str = request.headers.get('CF-Connecting-IP').strip()
    else:
        # Final fallback to remote_addr
        ip_str = request.remote_addr
    
    # Validate IP for PostgreSQL INET type
    return _validate_ip(ip_str)


def _validate_ip(ip_str: Optional[str]) -> Optional[str]:
    """
    Validate IP address for PostgreSQL INET type.
    
    INET type is strict and rejects:
    - Empty strings
    - Invalid formats
    - Hostnames
    
    Args:
        ip_str: IP address string to validate
        
    Returns:
        Valid IP string or None (for nullable column)
    """
    if not ip_str or not isinstance(ip_str, str):
        return None
    
    ip_str = ip_str.strip()
    if not ip_str:
        return None
    
    # Basic IPv4 validation (PostgreSQL will do stricter validation)
    import re
    # IPv4 pattern: 4 groups of 1-3 digits separated by dots
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    
    if re.match(ipv4_pattern, ip_str):
        # Additional check: each octet should be 0-255
        try:
            parts = ip_str.split('.')
            if all(0 <= int(part) <= 255 for part in parts):
                return ip_str
        except ValueError:
            pass
    
    # IPv6 validation (basic check)
    if ':' in ip_str:
        # Basic IPv6 format check (PostgreSQL will validate fully)
        # Allow compressed format (::) and expanded format
        if re.match(r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$', ip_str) or '::' in ip_str:
            return ip_str
    
    # Invalid IP format - return None (column is nullable)
    return None


def classify_search(preferences: Dict[str, Any]) -> str:
    """
    Classify a search as 'exploration' or 'focused_search'.
    
    Args:
        preferences: Search preferences from API request
        
    Returns:
        'exploration' if minimal filters, 'focused_search' otherwise
    """
    if not preferences:
        return 'exploration'
    
    # Count meaningful filters (non-default values)
    filter_count = 0
    
    # Check for specific selections
    if preferences.get('selected_countries'):
        filter_count += 1
    if preferences.get('selected_continents'):
        filter_count += 1
    if preferences.get('preferred_type_id'):
        filter_count += 1
    if preferences.get('preferred_theme_ids'):
        filter_count += 1
    if preferences.get('budget'):
        filter_count += 1
    if preferences.get('difficulty'):
        filter_count += 1
    
    # Check for non-default duration
    min_dur = preferences.get('min_duration', 1)
    max_dur = preferences.get('max_duration', 365)
    if min_dur != 1 or max_dur != 365:
        filter_count += 1
    
    # Check for date filters
    if preferences.get('year') and preferences.get('year') != 'all':
        filter_count += 1
    if preferences.get('month') and preferences.get('month') != 'all':
        filter_count += 1
    
    # 2 or more filters = focused search
    return 'focused_search' if filter_count >= 2 else 'exploration'


# ============================================
# EVENT SERVICE CLASS
# ============================================

class EventService:
    """
    Handles event tracking, user resolution, and session management.
    
    Key features:
    - Anonymous user creation on first visit
    - Session management with 30-minute timeout
    - Event validation and categorization
    - Real-time trip interaction updates
    """
    
    def __init__(self):
        """Initialize the event service."""
        self._session_timeout = timedelta(minutes=30)
    
    # ----------------------------------------
    # User Management
    # ----------------------------------------
    
    def get_or_create_user(
        self,
        anonymous_id: str,
        email: Optional[str] = None,
        supabase_user_id: Optional[str] = None
    ) -> User:
        """
        Get existing user or create new anonymous/registered user.
        
        Args:
            anonymous_id: Client-generated UUID from localStorage
            email: Optional email if user is registered
            supabase_user_id: Optional Supabase user ID (from JWT 'sub' claim)
            
        Returns:
            User object (detached from DB session)
        """
        db = SessionLocal()
        try:
            # Convert string to UUID
            anon_uuid = UUID(anonymous_id) if isinstance(anonymous_id, str) else anonymous_id
            
            # Priority 1: Find by Supabase user ID (if authenticated)
            if supabase_user_id:
                try:
                    supabase_uuid = UUID(supabase_user_id) if isinstance(supabase_user_id, str) else supabase_user_id
                    # Note: We'll store Supabase user ID in email field for now
                    # In a production system, you might add a separate supabase_user_id column
                    # For now, we use email as the unique identifier for registered users
                    if email:
                        user = db.query(User).filter(User.email == email).first()
                        if user:
                            # Link anonymous_id if different
                            if user.anonymous_id != anon_uuid:
                                user.anonymous_id = anon_uuid
                            user.is_registered = True
                            user.last_seen_at = datetime.utcnow()
                            db.commit()
                            db.refresh(user)
                            db.expunge(user)
                            return user
                except (ValueError, TypeError):
                    pass  # Invalid UUID format, continue with other methods
            
            # Priority 2: Try to find by anonymous_id
            user = db.query(User).filter(User.anonymous_id == anon_uuid).first()
            
            if user:
                # If we have Supabase auth info, upgrade this user
                if supabase_user_id and email:
                    user.email = email
                    user.is_registered = True
                user.last_seen_at = datetime.utcnow()
                db.commit()
                db.refresh(user)
                db.expunge(user)
                return user
            
            # Priority 3: Try to find by email if provided
            if email:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    # Link anonymous_id if different
                    if user.anonymous_id != anon_uuid:
                        user.anonymous_id = anon_uuid
                    user.is_registered = True
                    user.last_seen_at = datetime.utcnow()
                    db.commit()
                    db.refresh(user)
                    db.expunge(user)
                    return user
            
            # Create new user (anonymous or registered)
            user = User(
                anonymous_id=anon_uuid,
                email=email,
                is_registered=(email is not None and supabase_user_id is not None)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            db.expunge(user)
            return user
            
        finally:
            db.close()
    
    # ----------------------------------------
    # Session Management
    # ----------------------------------------
    
    def get_or_create_session(
        self,
        session_id: str,
        anonymous_id: str,
        user_id: Optional[int] = None,
        device_type: Optional[str] = None,  # From frontend, NOT parsed
        referrer: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Session:
        """
        Get existing session or create new one.
        
        Args:
            session_id: Browser session UUID
            anonymous_id: User anonymous UUID
            user_id: Database user ID (optional)
            device_type: From frontend (mobile/tablet/desktop)
            referrer: Document referrer from frontend
            user_agent: Browser user agent (for logging only)
            ip_address: Client IP (already extracted via get_real_ip)
            
        Returns:
            Session object (detached from DB session)
        """
        db = SessionLocal()
        try:
            sess_uuid = UUID(session_id) if isinstance(session_id, str) else session_id
            anon_uuid = UUID(anonymous_id) if isinstance(anonymous_id, str) else anonymous_id
            
            session = db.query(Session).filter(Session.session_id == sess_uuid).first()
            
            if session:
                # Check if session is still active
                if session.ended_at is None:
                    # Expunge to detach from session but keep attributes
                    db.expunge(session)
                    return session
            
            # Create new session with device_type from frontend
            session = Session(
                session_id=sess_uuid,
                user_id=user_id,
                anonymous_id=anon_uuid,
                device_type=device_type,  # From frontend, not parsed
                referrer=referrer,
                user_agent=user_agent,
                ip_address=ip_address
            )
            db.add(session)
            db.commit()
            
            # Update user's session count
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    user.total_sessions += 1
                    db.commit()
            
            # Refresh session to get current state after all commits
            db.refresh(session)
            
            # Expunge to detach from session but keep attributes
            db.expunge(session)
            return session
            
        finally:
            db.close()
    
    # ----------------------------------------
    # Event Validation
    # ----------------------------------------
    
    def validate_event(self, event_data: Dict[str, Any]) -> tuple:
        """
        Validate incoming event data.
        
        Args:
            event_data: Raw event data from API
            
        Returns:
            (is_valid, error_message)
        """
        # Required fields
        required = ['event_type', 'session_id', 'anonymous_id']
        for field in required:
            if field not in event_data or not event_data[field]:
                return False, f"Missing required field: {field}"
        
        # Validate event type
        event_type = event_data.get('event_type')
        if event_type not in VALID_EVENT_TYPES:
            return False, f"Invalid event type: {event_type}. Valid types: {VALID_EVENT_TYPES}"
        
        # Validate UUIDs
        try:
            UUID(str(event_data['session_id']))
            UUID(str(event_data['anonymous_id']))
        except (ValueError, TypeError):
            return False, "Invalid UUID format for session_id or anonymous_id"
        
        # Validate source if present
        source = event_data.get('source')
        if source and source not in VALID_SOURCES:
            return False, f"Invalid source: {source}. Valid sources: {VALID_SOURCES}"
        
        # Validate trip_id if present
        trip_id = event_data.get('trip_id')
        if trip_id is not None:
            if not isinstance(trip_id, int) or trip_id < 1:
                return False, "Invalid trip_id: must be positive integer"
        
        return True, None
    
    # ----------------------------------------
    # Event Tracking
    # ----------------------------------------
    
    def track_event(
        self,
        event_type: str,
        session_id: str,
        anonymous_id: str,
        user_id: Optional[int] = None,
        trip_id: Optional[int] = None,
        recommendation_request_id: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        position: Optional[int] = None,
        score: Optional[float] = None,
        client_timestamp: Optional[str] = None,
        page_url: Optional[str] = None,
        referrer: Optional[str] = None
    ) -> Event:
        """
        Record a tracking event.
        
        Args:
            event_type: Type of event (from VALID_EVENT_TYPES)
            session_id: Browser session UUID
            anonymous_id: User anonymous UUID
            user_id: Database user ID (optional)
            trip_id: Related trip ID (optional)
            recommendation_request_id: Links to Phase 0 logging
            source: Click source (search_results/relaxed_results/homepage)
            metadata: Flexible data (duration_seconds, filter_name, etc.)
            position: Position in results (for impressions/clicks)
            score: Match score at time of event
            client_timestamp: Timestamp from frontend
            page_url: Current page URL
            referrer: Document referrer
            
        Returns:
            Created Event object
        """
        db = SessionLocal()
        try:
            # Get event category (for counters and interactions, not for DB storage)
            category = EVENT_CATEGORIES.get(event_type, 'unknown')
            
            # Look up event_type_id from event_types table
            event_type_obj = db.query(EventType).filter(EventType.name == event_type).first()
            if not event_type_obj:
                # Fallback to page_view (id=1) if event type not found
                print(f"[WARNING] Event type not found: {event_type}, using page_view")
                event_type_id = 1
            else:
                event_type_id = event_type_obj.id
            
            # Parse client timestamp
            parsed_client_ts = None
            if client_timestamp:
                try:
                    # Handle ISO format with Z or +00:00
                    ts = client_timestamp.replace('Z', '+00:00')
                    parsed_client_ts = datetime.fromisoformat(ts)
                except (ValueError, TypeError):
                    pass
            
            # Convert UUIDs
            sess_uuid = UUID(session_id) if isinstance(session_id, str) else session_id
            anon_uuid = UUID(anonymous_id) if isinstance(anonymous_id, str) else anonymous_id
            rec_uuid = None
            if recommendation_request_id:
                try:
                    rec_uuid = UUID(recommendation_request_id) if isinstance(recommendation_request_id, str) else recommendation_request_id
                except (ValueError, TypeError):
                    pass
            
            # Create event with event_type_id (3NF schema)
            event = Event(
                user_id=user_id,
                session_id=sess_uuid,
                anonymous_id=anon_uuid,
                event_type_id=event_type_id,
                trip_id=trip_id,
                recommendation_request_id=rec_uuid,
                source=source,
                event_data=metadata or {},  # Note: Column is 'event_data', API uses 'metadata'
                position_in_results=position,
                score_at_time=score,
                client_timestamp=parsed_client_ts,
                page_url=page_url,
                referrer=referrer
            )
            
            db.add(event)
            db.commit()
            
            # Update session counters
            self._update_session_counters(db, sess_uuid, event_type)
            
            # Update user counters
            if user_id:
                self._update_user_counters(db, user_id, event_type)
            
            # Update trip interactions for engagement/conversion events
            if trip_id and category in ('engagement', 'conversion'):
                self._update_trip_interactions(db, trip_id, event_type, anon_uuid, metadata)
            
            # Refresh event to get all attributes after all commits
            db.refresh(event)
            
            # Expunge to detach from session but keep attributes
            db.expunge(event)
            return event
            
        finally:
            db.close()
    
    def _update_session_counters(self, db, session_id: UUID, event_type: str):
        """Update session activity counters."""
        session = db.query(Session).filter(Session.session_id == session_id).first()
        
        if session:
            if event_type == 'search_submit':
                session.search_count += 1
            elif event_type == 'click_trip':
                session.click_count += 1
            elif event_type == 'save_trip':
                session.save_count += 1
            elif event_type in ('contact_whatsapp', 'contact_phone'):
                session.contact_count += 1
            
            db.commit()
    
    def _update_user_counters(self, db, user_id: int, event_type: str):
        """Update user activity counters."""
        user = db.query(User).filter(User.id == user_id).first()
        
        if user:
            if event_type == 'search_submit':
                user.total_searches += 1
            elif event_type == 'click_trip':
                user.total_clicks += 1
            
            user.last_seen_at = datetime.utcnow()
            db.commit()
    
    def _update_trip_interactions(
        self,
        db,
        trip_id: int,
        event_type: str,
        anonymous_id: UUID,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Update trip interaction metrics in real-time.
        
        Note: Daily batch job will recalculate for accuracy.
        """
        # Get or create trip_interactions record
        interaction = db.query(TripInteraction).filter(
            TripInteraction.trip_id == trip_id
        ).first()
        
        if not interaction:
            interaction = TripInteraction(trip_id=trip_id)
            db.add(interaction)
            db.flush()
        
        # Update counters based on event type
        if event_type == 'impression':
            interaction.impression_count += 1
        elif event_type == 'click_trip':
            interaction.click_count += 1
            interaction.last_clicked_at = datetime.utcnow()
        elif event_type == 'trip_dwell_time':
            # Add dwell time from metadata
            duration = (metadata or {}).get('duration_seconds', 0)
            if duration > 0:
                interaction.total_dwell_time_seconds += duration
                # Update average
                if interaction.click_count > 0:
                    interaction.avg_dwell_time_seconds = (
                        interaction.total_dwell_time_seconds // interaction.click_count
                    )
        elif event_type == 'save_trip':
            interaction.save_count += 1
        elif event_type == 'contact_whatsapp':
            interaction.whatsapp_contact_count += 1
        elif event_type == 'contact_phone':
            interaction.phone_contact_count += 1
        elif event_type == 'booking_start':
            interaction.booking_start_count += 1
        
        # Recompute rates (simple version - batch job more accurate)
        if interaction.impression_count > 0:
            interaction.click_through_rate = (
                interaction.click_count / interaction.impression_count
            )
        if interaction.click_count > 0:
            interaction.save_rate = interaction.save_count / interaction.click_count
            total_contacts = interaction.whatsapp_contact_count + interaction.phone_contact_count
            interaction.contact_rate = total_contacts / interaction.click_count
        
        db.commit()
    
    # ----------------------------------------
    # Batch Event Tracking
    # ----------------------------------------
    
    def track_batch(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Track multiple events in a batch.
        
        Args:
            events: List of event data dicts
            
        Returns:
            Summary with processed count and errors
        """
        processed = 0
        errors = []
        
        for i, event_data in enumerate(events):
            is_valid, error = self.validate_event(event_data)
            if not is_valid:
                errors.append({'index': i, 'error': error})
                continue
            
            try:
                self.track_event(
                    event_type=event_data['event_type'],
                    session_id=event_data['session_id'],
                    anonymous_id=event_data['anonymous_id'],
                    user_id=event_data.get('user_id'),
                    trip_id=event_data.get('trip_id'),
                    recommendation_request_id=event_data.get('recommendation_request_id'),
                    source=event_data.get('source'),
                    metadata=event_data.get('metadata'),
                    position=event_data.get('position'),
                    score=event_data.get('score'),
                    client_timestamp=event_data.get('client_timestamp'),
                    page_url=event_data.get('page_url'),
                    referrer=event_data.get('referrer')
                )
                processed += 1
            except Exception as e:
                errors.append({'index': i, 'error': str(e)})
        
        return {
            'processed': processed,
            'total': len(events),
            'errors': errors
        }


# ============================================
# SINGLETON INSTANCE
# ============================================

_event_service = None

def get_event_service() -> EventService:
    """Get singleton event service instance."""
    global _event_service
    if _event_service is None:
        _event_service = EventService()
    return _event_service
