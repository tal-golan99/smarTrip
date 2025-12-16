"""
SmartTrip Events Module (Phase 1)
=================================

User feedback signal collection for personalization.

Components:
- models: SQLAlchemy models for users, sessions, events
- service: Event processing with IP extraction, validation
- api: REST endpoints for event tracking
"""

from .service import EventService, get_event_service
from .models import User, Session, Event, TripInteraction

__all__ = [
    'EventService',
    'get_event_service',
    'User',
    'Session',
    'Event',
    'TripInteraction',
]
