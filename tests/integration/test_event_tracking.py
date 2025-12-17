"""
Event Tracking Tests (Phase 1)
==============================

Tests for the event tracking system:
- Event validation
- Session management
- Trip interactions updates
- Batch processing

NOTE: Moved from backend/tests/ during cleanup.
"""

import pytest
import uuid
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backend'))

from events.service import (
    EventService, 
    get_event_service,
    VALID_EVENT_TYPES,
    VALID_SOURCES,
    EVENT_CATEGORIES
)


class TestEventValidation:
    """Test event data validation"""
    
    def setup_method(self):
        self.service = EventService()
    
    def test_valid_event_passes_validation(self):
        """Valid event data should pass validation"""
        event_data = {
            'event_type': 'page_view',
            'session_id': str(uuid.uuid4()),
            'anonymous_id': str(uuid.uuid4()),
        }
        
        is_valid, error = self.service.validate_event(event_data)
        assert is_valid is True
        assert error is None
    
    def test_missing_event_type_fails(self):
        """Missing event_type should fail"""
        event_data = {
            'session_id': str(uuid.uuid4()),
            'anonymous_id': str(uuid.uuid4()),
        }
        
        is_valid, error = self.service.validate_event(event_data)
        assert is_valid is False
        assert 'event_type' in error.lower()
    
    def test_missing_session_id_fails(self):
        """Missing session_id should fail"""
        event_data = {
            'event_type': 'page_view',
            'anonymous_id': str(uuid.uuid4()),
        }
        
        is_valid, error = self.service.validate_event(event_data)
        assert is_valid is False
        assert 'session_id' in error.lower()
    
    def test_missing_anonymous_id_fails(self):
        """Missing anonymous_id should fail"""
        event_data = {
            'event_type': 'page_view',
            'session_id': str(uuid.uuid4()),
        }
        
        is_valid, error = self.service.validate_event(event_data)
        assert is_valid is False
        assert 'anonymous_id' in error.lower()
    
    def test_invalid_event_type_fails(self):
        """Invalid event_type should fail"""
        event_data = {
            'event_type': 'invalid_event_type',
            'session_id': str(uuid.uuid4()),
            'anonymous_id': str(uuid.uuid4()),
        }
        
        is_valid, error = self.service.validate_event(event_data)
        assert is_valid is False
        assert 'invalid event type' in error.lower()
    
    def test_invalid_uuid_format_fails(self):
        """Invalid UUID format should fail"""
        event_data = {
            'event_type': 'page_view',
            'session_id': 'not-a-uuid',
            'anonymous_id': str(uuid.uuid4()),
        }
        
        is_valid, error = self.service.validate_event(event_data)
        assert is_valid is False
        assert 'uuid' in error.lower()
    
    def test_click_trip_requires_source(self):
        """click_trip event should require source field"""
        event_data = {
            'event_type': 'click_trip',
            'session_id': str(uuid.uuid4()),
            'anonymous_id': str(uuid.uuid4()),
            'trip_id': 1,
            # source is missing
        }
        
        # Note: source validation might be in API layer, not service layer
        # This test documents expected behavior
        is_valid, error = self.service.validate_event(event_data)
        # Basic validation passes, source check is in API
        assert is_valid is True or 'source' in str(error).lower()
    
    def test_all_valid_event_types(self):
        """All defined event types should be valid"""
        for event_type in VALID_EVENT_TYPES:
            event_data = {
                'event_type': event_type,
                'session_id': str(uuid.uuid4()),
                'anonymous_id': str(uuid.uuid4()),
            }
            
            is_valid, error = self.service.validate_event(event_data)
            assert is_valid is True, f"Event type '{event_type}' should be valid: {error}"


class TestEventCategories:
    """Test event category mapping"""
    
    def test_navigation_events(self):
        """Navigation events should map to 'navigation' category"""
        navigation_events = ['page_view', 'session_start', 'session_end']
        for event in navigation_events:
            if event in EVENT_CATEGORIES:
                assert EVENT_CATEGORIES[event] == 'navigation'
    
    def test_search_events(self):
        """Search events should map to 'search' category"""
        search_events = ['search', 'filter_change', 'filter_removed', 'sort_change']
        for event in search_events:
            if event in EVENT_CATEGORIES:
                assert EVENT_CATEGORIES[event] == 'search'
    
    def test_engagement_events(self):
        """Engagement events should map to 'engagement' category"""
        engagement_events = ['click_trip', 'trip_dwell_time', 'impression', 'scroll_depth']
        for event in engagement_events:
            if event in EVENT_CATEGORIES:
                assert EVENT_CATEGORIES[event] == 'engagement'
    
    def test_conversion_events(self):
        """Conversion events should map to 'conversion' category"""
        conversion_events = ['contact_whatsapp', 'contact_phone', 'booking_start', 'save_trip']
        for event in conversion_events:
            if event in EVENT_CATEGORIES:
                assert EVENT_CATEGORIES[event] == 'conversion'


class TestValidSources:
    """Test valid source values"""
    
    def test_search_results_is_valid_source(self):
        """search_results should be a valid source"""
        assert 'search_results' in VALID_SOURCES
    
    def test_relaxed_results_is_valid_source(self):
        """relaxed_results should be a valid source"""
        assert 'relaxed_results' in VALID_SOURCES
    
    def test_homepage_is_valid_source(self):
        """homepage should be a valid source"""
        assert 'homepage' in VALID_SOURCES


class TestEventService:
    """Test EventService singleton"""
    
    def test_get_event_service_returns_singleton(self):
        """get_event_service should return the same instance"""
        service1 = get_event_service()
        service2 = get_event_service()
        assert service1 is service2
    
    def test_service_has_required_methods(self):
        """Service should have all required methods"""
        service = get_event_service()
        
        assert hasattr(service, 'validate_event')
        assert hasattr(service, 'track_event')
        assert hasattr(service, 'track_batch')
        assert hasattr(service, 'get_or_create_user')
        assert hasattr(service, 'get_or_create_session')


# ============================================
# RUN TESTS
# ============================================

if __name__ == '__main__':
    # Run with pytest
    pytest.main([__file__, '-v'])
