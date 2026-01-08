"""
Event Tracking API Endpoints (Phase 1)
======================================

REST endpoints for user event tracking.

Endpoints:
- POST /api/events - Track single event
- POST /api/events/batch - Track multiple events
- GET /api/events/types - List valid event types
- POST /api/user/identify - Link anonymous to registered user
- POST /api/session/start - Initialize session with device info
"""

import os
from flask import Blueprint, request, jsonify
from .service import (
    get_event_service, 
    get_real_ip, 
    VALID_EVENT_TYPES, 
    VALID_SOURCES,
    EVENT_CATEGORIES
)

# Import auth helper (optional - won't break if not available)
try:
    from auth_supabase import get_current_user
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    def get_current_user():
        return None

# Create Blueprint
events_bp = Blueprint('events', __name__, url_prefix='/api')


# ============================================
# SESSION MANAGEMENT
# ============================================

@events_bp.route('/session/start', methods=['POST'])
def start_session():
    """
    Initialize or resume a session with device info.
    
    device_type comes from frontend (based on window.innerWidth),
    NOT from user-agent parsing.
    
    Request body:
    {
        "session_id": "uuid",
        "anonymous_id": "uuid",
        "device_type": "mobile" | "tablet" | "desktop",
        "referrer": "https://google.com/..."
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        
        # Validate required fields
        if not data.get('session_id'):
            return jsonify({'success': False, 'error': 'session_id required'}), 400
        if not data.get('anonymous_id'):
            return jsonify({'success': False, 'error': 'anonymous_id required'}), 400
        
        service = get_event_service()
        
        # Get authenticated user from JWT (if available)
        auth_user = None
        if AUTH_AVAILABLE:
            auth_user = get_current_user()
        
        # Get or create user (prioritize authenticated user)
        user = service.get_or_create_user(
            anonymous_id=data['anonymous_id'],
            email=auth_user.get('email') if auth_user else data.get('email'),
            supabase_user_id=auth_user.get('id') if auth_user else None
        )
        
        # Get real IP (handles load balancers)
        client_ip = get_real_ip(request)
        
        # Create/get session with device_type from frontend
        session = service.get_or_create_session(
            session_id=data['session_id'],
            anonymous_id=data['anonymous_id'],
            user_id=user.id,
            device_type=data.get('device_type'),  # From frontend
            referrer=data.get('referrer'),  # From frontend (document.referrer)
            user_agent=request.headers.get('User-Agent'),
            ip_address=client_ip
        )
        
        return jsonify({
            'success': True,
            'user_id': user.id,
            'session_id': str(session.session_id),
            'is_new_session': session.search_count == 0 and session.click_count == 0
        }), 200
    
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        
        # Log detailed error for debugging
        print(f"[EVENTS] Session start error: {error_type}: {error_msg}", flush=True)
        import traceback
        traceback.print_exc()  # Print full stack trace to logs
        
        # Return error details (helpful for debugging, but sanitized)
        # In production, you might want to hide internal errors
        return jsonify({
            'success': False,
            'error': error_msg if 'FLASK_ENV' in os.environ and os.environ['FLASK_ENV'] == 'development' else 'Session initialization failed',
            'type': error_type
        }), 500


# ============================================
# EVENT TRACKING
# ============================================

@events_bp.route('/events', methods=['POST'])
def track_event():
    """
    Track a single user event.
    
    Request body:
    {
        "event_type": "click_trip",
        "session_id": "uuid",
        "anonymous_id": "uuid",
        "trip_id": 123,                           // optional
        "source": "search_results",               // required for clicks
        "recommendation_request_id": "uuid",      // links to Phase 0
        "metadata": {                             // flexible data
            "duration_seconds": 45,               // for dwell time
            "filter_name": "budget",              // for filter events
            "old_value": 5000,
            "new_value": null
        },
        "position": 3,                            // position in results
        "score": 75.5,                            // match_score at time
        "client_timestamp": "2025-01-01T12:00:00Z",
        "page_url": "/search/results",
        "referrer": "https://google.com"
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        
        service = get_event_service()
        
        # Validate event data
        is_valid, error = service.validate_event(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error}), 400
        
        # Require source for click events
        if data['event_type'] == 'click_trip' and not data.get('source'):
            return jsonify({
                'success': False, 
                'error': 'source is required for click_trip events'
            }), 400
        
        # Get authenticated user from JWT (if available)
        auth_user = None
        if AUTH_AVAILABLE:
            auth_user = get_current_user()
        
        # Resolve user (prioritize authenticated user)
        user = service.get_or_create_user(
            anonymous_id=data['anonymous_id'],
            email=auth_user.get('email') if auth_user else data.get('email'),
            supabase_user_id=auth_user.get('id') if auth_user else None
        )
        
        # Track the event
        event = service.track_event(
            event_type=data['event_type'],
            session_id=data['session_id'],
            anonymous_id=data['anonymous_id'],
            user_id=user.id,
            trip_id=data.get('trip_id'),
            recommendation_request_id=data.get('recommendation_request_id'),
            source=data.get('source'),
            metadata=data.get('metadata'),
            position=data.get('position'),
            score=data.get('score'),
            client_timestamp=data.get('client_timestamp'),
            page_url=data.get('page_url'),
            referrer=data.get('referrer')
        )
        
        return jsonify({
            'success': True,
            'event_id': event.id
        }), 201
    
    except Exception as e:
        print(f"[EVENTS] Track event error: {e}", flush=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@events_bp.route('/events/batch', methods=['POST'])
def track_events_batch():
    """
    Track multiple events in a batch.
    
    More efficient for accumulated events (e.g., impressions).
    Maximum 100 events per batch.
    
    Request body:
    {
        "events": [
            { event1 },
            { event2 },
            ...
        ]
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        events = data.get('events', [])
        
        if not events:
            return jsonify({'success': False, 'error': 'No events provided'}), 400
        
        if len(events) > 100:
            return jsonify({
                'success': False, 
                'error': 'Maximum 100 events per batch'
            }), 400
        
        service = get_event_service()
        
        # Get authenticated user from JWT (if available)
        auth_user = None
        if AUTH_AVAILABLE:
            auth_user = get_current_user()
        
        # Resolve users for all unique anonymous_ids first
        anonymous_ids = set(e.get('anonymous_id') for e in events if e.get('anonymous_id'))
        user_map = {}
        for anon_id in anonymous_ids:
            user = service.get_or_create_user(
                anonymous_id=anon_id,
                email=auth_user.get('email') if auth_user else None,
                supabase_user_id=auth_user.get('id') if auth_user else None
            )
            user_map[anon_id] = user.id
        
        # Add user_id to each event
        for event in events:
            if event.get('anonymous_id') in user_map:
                event['user_id'] = user_map[event['anonymous_id']]
        
        # Process batch
        result = service.track_batch(events)
        
        return jsonify({
            'success': True,
            'processed': result['processed'],
            'total': result['total'],
            'errors': result['errors'] if result['errors'] else None
        }), 201
    
    except Exception as e:
        print(f"[EVENTS] Batch tracking error: {e}", flush=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# USER IDENTIFICATION
# ============================================

@events_bp.route('/user/identify', methods=['POST'])
def identify_user():
    """
    Identify/register a user (link anonymous to registered).
    
    Called when user provides email or logs in.
    
    Request body:
    {
        "anonymous_id": "uuid",
        "email": "user@example.com",
        "name": "Optional Name"
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        
        if not data.get('anonymous_id'):
            return jsonify({'success': False, 'error': 'anonymous_id required'}), 400
        
        service = get_event_service()
        user = service.get_or_create_user(
            anonymous_id=data['anonymous_id'],
            email=data.get('email')
        )
        
        return jsonify({
            'success': True,
            'user_id': user.id,
            'is_registered': user.is_registered
        }), 200
    
    except Exception as e:
        print(f"[EVENTS] User identify error: {e}", flush=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# UTILITY ENDPOINTS
# ============================================

@events_bp.route('/events/types', methods=['GET'])
def get_event_types():
    """
    Get list of valid event types and their categories.
    
    Useful for frontend validation.
    """
    return jsonify({
        'success': True,
        'event_types': list(VALID_EVENT_TYPES),
        'categories': EVENT_CATEGORIES,
        'valid_sources': list(VALID_SOURCES)
    }), 200
