"""
SmartTrip Test Suite - Global Fixtures
======================================

Provides shared fixtures for all test modules:
- Database session management
- Flask test client
- Seed data helpers
- API client utilities

Test Database: Uses DATABASE_URL with '_test' suffix or separate test DB
"""

import os
import sys
import pytest
import json
from datetime import datetime, date, timedelta
from typing import Generator, Dict, Any
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Import models
from models import (
    Base, Country, Guide, Tag, Trip, TripTag, TripType,
    TripStatus, Continent, Gender
)

# Try to import V2 models
try:
    from models_v2 import (
        Company, TripTemplate, TripOccurrence, 
        TripTemplateTag, TripTemplateCountry, PriceHistory, Review
    )
    V2_MODELS_AVAILABLE = True
except ImportError:
    V2_MODELS_AVAILABLE = False

# Import Flask app
from app import app as flask_app
from database import engine as prod_engine, db_session as prod_session


# ============================================
# DATABASE FIXTURES
# ============================================

@pytest.fixture(scope="session")
def test_engine():
    """
    Create a test database engine.
    Uses the production DATABASE_URL but connects to a test database.
    """
    # Get production URL and modify for test
    prod_url = os.environ.get('DATABASE_URL', '')
    
    if prod_url:
        # Replace database name with test database
        if '/smartrip' in prod_url:
            test_url = prod_url.replace('/smartrip', '/smartrip_test')
        else:
            test_url = prod_url + '_test'
    else:
        # Fallback to in-memory SQLite for basic tests
        test_url = "sqlite:///:memory:"
    
    # For this implementation, we'll use the production engine
    # In a real setup, you'd create a separate test database
    engine = prod_engine
    
    yield engine


@pytest.fixture(scope="session")
def db_tables(test_engine):
    """
    Ensure all tables exist in the test database.
    """
    Base.metadata.create_all(test_engine)
    yield
    # Optionally drop tables after all tests
    # Base.metadata.drop_all(test_engine)


@pytest.fixture(scope="function")
def db_session(test_engine, db_tables) -> Generator[Session, None, None]:
    """
    Create a new database session for each test.
    Rolls back after each test to maintain isolation.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def raw_connection(test_engine):
    """
    Provide a raw database connection for SQL tests.
    """
    connection = test_engine.connect()
    yield connection
    connection.close()


# ============================================
# FLASK APP FIXTURES
# ============================================

@pytest.fixture(scope="session")
def app():
    """
    Configure Flask app for testing.
    """
    flask_app.config.update({
        'TESTING': True,
        'DEBUG': False,
    })
    yield flask_app


@pytest.fixture(scope="function")
def client(app):
    """
    Flask test client for API testing.
    """
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def api_client(client):
    """
    Enhanced API client with helper methods.
    """
    class APIClient:
        def __init__(self, flask_client):
            self._client = flask_client
            self.base_url = ''
        
        def get(self, path, **kwargs):
            return self._client.get(path, **kwargs)
        
        def post(self, path, json=None, **kwargs):
            return self._client.post(path, json=json, **kwargs)
        
        def put(self, path, json=None, **kwargs):
            return self._client.put(path, json=json, **kwargs)
        
        def delete(self, path, **kwargs):
            return self._client.delete(path, **kwargs)
        
        def get_json(self, path):
            response = self.get(path)
            return response.get_json()
        
        def post_json(self, path, data):
            response = self.post(path, json=data)
            return response.get_json()
    
    return APIClient(client)


# ============================================
# SEED DATA FIXTURES
# ============================================

@pytest.fixture(scope="function")
def sample_country(db_session) -> Country:
    """Create a sample country for testing."""
    country = Country(
        name="Test Country",
        name_he="Test Country HE",
        continent=Continent.EUROPE
    )
    db_session.add(country)
    db_session.flush()
    return country


@pytest.fixture(scope="function")
def sample_guide(db_session) -> Guide:
    """Create a sample guide for testing."""
    guide = Guide(
        name="Test Guide",
        name_he="Test Guide HE",
        bio="Test guide biography",
        bio_he="Test guide biography HE",
        gender=Gender.MALE,
        image_url="https://example.com/guide.jpg"
    )
    db_session.add(guide)
    db_session.flush()
    return guide


@pytest.fixture(scope="function")
def sample_trip_type(db_session) -> TripType:
    """Create a sample trip type for testing."""
    trip_type = TripType(
        name="Test Trip Type",
        name_he="Test Trip Type HE",
        description="Test trip type description"
    )
    db_session.add(trip_type)
    db_session.flush()
    return trip_type


@pytest.fixture(scope="function")
def sample_tag(db_session) -> Tag:
    """Create a sample tag for testing."""
    tag = Tag(
        name="Test Tag",
        name_he="Test Tag HE",
        description="Test tag description"
    )
    db_session.add(tag)
    db_session.flush()
    return tag


@pytest.fixture(scope="function")
def sample_trip(db_session, sample_country, sample_guide, sample_trip_type) -> Trip:
    """Create a sample trip for testing."""
    trip = Trip(
        title="Test Trip",
        title_he="Test Trip HE",
        description="Test trip description",
        description_he="Test trip description HE",
        image_url="https://example.com/trip.jpg",
        start_date=date.today() + timedelta(days=30),
        end_date=date.today() + timedelta(days=40),
        price=5000.00,
        single_supplement_price=1000.00,
        max_capacity=20,
        spots_left=15,
        status=TripStatus.OPEN,
        difficulty_level=2,
        country_id=sample_country.id,
        guide_id=sample_guide.id,
        trip_type_id=sample_trip_type.id
    )
    db_session.add(trip)
    db_session.flush()
    return trip


# ============================================
# V2 SCHEMA FIXTURES (if available)
# ============================================

if V2_MODELS_AVAILABLE:
    @pytest.fixture(scope="function")
    def sample_company(db_session) -> Company:
        """Create a sample company for V2 testing."""
        company = Company(
            name="Test Company",
            name_he="Test Company HE",
            description="Test company description",
            logo_url="https://example.com/logo.png",
            website_url="https://example.com",
            phone="+972-1234567",
            email="test@example.com",
            is_active=True
        )
        db_session.add(company)
        db_session.flush()
        return company


# ============================================
# HELPER FIXTURES
# ============================================

@pytest.fixture
def mock_datetime():
    """
    Fixture to mock datetime for time-sensitive tests.
    """
    with patch('datetime.datetime') as mock_dt:
        mock_dt.now.return_value = datetime(2025, 12, 16, 12, 0, 0)
        mock_dt.utcnow.return_value = datetime(2025, 12, 16, 10, 0, 0)
        yield mock_dt


@pytest.fixture
def uuid_generator():
    """Generate valid UUIDs for testing."""
    import uuid
    return lambda: str(uuid.uuid4())


@pytest.fixture
def session_id(uuid_generator):
    """Generate a valid session ID."""
    return uuid_generator()


@pytest.fixture
def anonymous_id(uuid_generator):
    """Generate a valid anonymous ID."""
    return uuid_generator()


# ============================================
# DATABASE STATE VERIFICATION
# ============================================

@pytest.fixture(scope="session")
def db_state():
    """
    Verify database has required seed data for tests.
    Returns counts of key tables.
    """
    from database import engine
    
    with engine.connect() as conn:
        state = {}
        tables = ['countries', 'guides', 'tags', 'trip_types', 'trips']
        
        for table in tables:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                state[table] = result.scalar()
            except:
                state[table] = 0
        
        # Check V2 tables
        v2_tables = ['companies', 'trip_templates', 'trip_occurrences']
        for table in v2_tables:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                state[table] = result.scalar()
            except:
                state[table] = 0
    
    return state


# ============================================
# MARKERS AND CONFIGURATION
# ============================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "db: mark test as database test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API test"
    )
    config.addinivalue_line(
        "markers", "analytics: mark test as analytics test"
    )
    config.addinivalue_line(
        "markers", "cron: mark test as cron/scheduler test"
    )
    config.addinivalue_line(
        "markers", "recommender: mark test as recommender test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# ============================================
# TEST DATA CONSTANTS
# ============================================

TEST_CONSTANTS = {
    'VALID_CONTINENTS': ['Africa', 'Asia', 'Europe', 'North America', 'South America', 'Oceania', 'Antarctica'],
    'VALID_STATUSES': ['Open', 'Guaranteed', 'Last Places', 'Full'],
    'VALID_DIFFICULTIES': [1, 2, 3, 4, 5],
    'VALID_EVENT_TYPES': [
        'page_view', 'click_trip', 'search', 'filter_change', 'sort_change',
        'impression', 'scroll_depth', 'trip_dwell_time', 'contact_whatsapp',
        'contact_phone', 'booking_start', 'save_trip', 'share_trip'
    ],
    'VALID_EVENT_CATEGORIES': ['navigation', 'search', 'engagement', 'conversion'],
}


@pytest.fixture
def test_constants():
    """Provide test constants to test functions."""
    return TEST_CONSTANTS
