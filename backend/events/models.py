"""
SQLAlchemy Models for User Tracking (Phase 1)
==============================================

Defines ORM models for:
- User: Anonymous and registered user tracking
- Session: Browser session management
- Event: User interaction events
- TripInteraction: Aggregated trip popularity metrics
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, 
    DECIMAL, BigInteger, Text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# Import Base from the main database module
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base


class User(Base):
    """
    User model supporting anonymous and registered users.
    
    Anonymous users are created on first visit via localStorage UUID.
    Can be upgraded to registered when user provides email.
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    
    # Identity - anonymous_id comes from frontend localStorage
    anonymous_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=True)
    
    # Profile (optional, for registered users)
    name = Column(String(100), nullable=True)
    name_he = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    # Note: preferred_language column removed per schema changes
    
    # Activity tracking
    first_seen_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_seen_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    total_sessions = Column(Integer, default=1)
    total_searches = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    
    # Status
    is_registered = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = relationship('Session', back_populates='user', lazy='dynamic')
    events = relationship('Event', back_populates='user', lazy='dynamic')
    
    def to_dict(self):
        """Serialize user for API response."""
        return {
            'id': self.id,
            'anonymous_id': str(self.anonymous_id),
            'email': self.email,
            'is_registered': self.is_registered,
            'total_sessions': self.total_sessions,
            'total_searches': self.total_searches,
            'total_clicks': self.total_clicks,
            'first_seen_at': self.first_seen_at.isoformat() if self.first_seen_at else None,
            'last_seen_at': self.last_seen_at.isoformat() if self.last_seen_at else None,
        }


class Session(Base):
    """
    Browser session model.
    
    Sessions expire after 30 minutes of inactivity.
    device_type is sent from frontend (not parsed from user-agent).
    """
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    
    # Identity
    session_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    anonymous_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Timing
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Device/context - device_type from frontend, not user-agent parsing
    user_agent = Column(Text, nullable=True)
    ip_address = Column(INET, nullable=True)
    referrer = Column(Text, nullable=True)
    device_type = Column(String(20), nullable=True)  # 'mobile', 'tablet', 'desktop'
    
    # Activity counters (updated in real-time)
    search_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    save_count = Column(Integer, default=0)
    contact_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='sessions')
    # Note: No direct relationship to Event - linked via session_id UUID, not FK
    
    def to_dict(self):
        """Serialize session for API response."""
        return {
            'id': self.id,
            'session_id': str(self.session_id),
            'user_id': self.user_id,
            'device_type': self.device_type,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'search_count': self.search_count,
            'click_count': self.click_count,
        }


class EventCategory(Base):
    """Event category for 3NF normalization."""
    __tablename__ = 'event_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    event_types = relationship('EventType', back_populates='category')


class EventType(Base):
    """Event type for 3NF normalization."""
    __tablename__ = 'event_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey('event_categories.id'), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    category = relationship('EventCategory', back_populates='event_types')
    events = relationship('Event', back_populates='event_type_rel')


class Event(Base):
    """
    User interaction event model.
    
    Tracks all user interactions with flexible metadata JSONB field.
    Supports: duration_seconds, filter_name, old_value, new_value, etc.
    
    source field for click attribution:
    - 'search_results': Primary search results
    - 'relaxed_results': Expanded/relaxed results (Phase 0)
    - 'homepage': Homepage recommendations
    """
    __tablename__ = 'events'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Identity
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    anonymous_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Event classification - FK to event_types (3NF normalized)
    event_type_id = Column(Integer, ForeignKey('event_types.id'), nullable=False)
    
    # Context
    trip_id = Column(Integer, nullable=True)  # No FK to avoid dependency issues
    recommendation_request_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Source for click attribution
    source = Column(String(50), nullable=True)
    
    # Flexible event data (JSONB)
    # Stores: duration_seconds, filter_name, old_value, new_value, etc.
    # Note: Named 'event_data' because 'metadata' is reserved by SQLAlchemy
    event_data = Column(JSONB, default=dict)
    
    # Position context (for ML position bias correction)
    position_in_results = Column(Integer, nullable=True)
    score_at_time = Column(DECIMAL(5, 2), nullable=True)
    
    # Timing
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    client_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Page context
    page_url = Column(Text, nullable=True)
    referrer = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='events')
    event_type_rel = relationship('EventType', back_populates='events')
    # Note: No direct relationship to Session - linked via session_id UUID, not FK
    
    def to_dict(self):
        """Serialize event for API response."""
        return {
            'id': self.id,
            'event_type_id': self.event_type_id,
            'event_type': self.event_type_rel.name if self.event_type_rel else None,
            'event_category': self.event_type_rel.category.name if self.event_type_rel and self.event_type_rel.category else None,
            'trip_id': self.trip_id,
            'source': self.source,
            'metadata': self.event_data,  # Return as 'metadata' for API consistency
            'position': self.position_in_results,
            'score': float(self.score_at_time) if self.score_at_time else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


class TripInteraction(Base):
    """
    Aggregated trip interaction metrics.
    
    Updated in real-time on events, with daily batch job for accuracy.
    Powers Phase 2 popularity ranking.
    """
    __tablename__ = 'trip_interactions'
    
    id = Column(Integer, primary_key=True)
    trip_id = Column(Integer, unique=True, nullable=False)
    
    # Impression metrics
    impression_count = Column(Integer, default=0)
    unique_viewers = Column(Integer, default=0)
    
    # Engagement metrics
    click_count = Column(Integer, default=0)
    unique_clickers = Column(Integer, default=0)
    total_dwell_time_seconds = Column(Integer, default=0)
    avg_dwell_time_seconds = Column(Integer, default=0)
    
    # Conversion metrics
    save_count = Column(Integer, default=0)
    whatsapp_contact_count = Column(Integer, default=0)
    phone_contact_count = Column(Integer, default=0)
    booking_start_count = Column(Integer, default=0)
    
    # Computed rates (updated by background job)
    click_through_rate = Column(DECIMAL(5, 4), nullable=True)
    save_rate = Column(DECIMAL(5, 4), nullable=True)
    contact_rate = Column(DECIMAL(5, 4), nullable=True)
    
    # Time-based (for trending/freshness)
    impressions_7d = Column(Integer, default=0)
    clicks_7d = Column(Integer, default=0)
    last_clicked_at = Column(DateTime(timezone=True), nullable=True)
    
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Serialize trip interaction metrics."""
        return {
            'trip_id': self.trip_id,
            'impressions': self.impression_count,
            'clicks': self.click_count,
            'saves': self.save_count,
            'ctr': float(self.click_through_rate) if self.click_through_rate else 0,
            'last_clicked': self.last_clicked_at.isoformat() if self.last_clicked_at else None,
        }
