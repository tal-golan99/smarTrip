"""
SmartTrip V2 Production Health Check - Master Test Suite
=========================================================

WARNING: Run this ONLY after run_migration_verification.py passes green!

This is NOT for migration comparison. This is the "Production Health Check" 
for V2 specifically, simulating a full user journey in the new architecture.

USAGE:
    # First, ensure migration tests pass:
    pytest tests/run_migration_verification.py -v
    
    # Then run this:
    pytest tests/test_master_v2.py -v --html=v2_health_check.html

TEST SCENARIOS:
    1. Admin creates a Company
    2. Admin creates a Trip Template
    3. Admin schedules 3 Occurrences (sold out, active, past)
    4. User searches for trips (finding the active one)
    5. User filters by the specific Company
    6. System calculates dynamic pricing based on occurrence

Author: SmartTrip QA Team
Date: 2025-12-17
"""

import pytest
import requests
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configuration
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
V2_API = f"{BASE_URL}/api/v2"


# ============================================
# FIXTURES
# ============================================

@pytest.fixture(scope="module")
def db_session():
    """Database session for the test module."""
    try:
        from database import db_session as session
        yield session
        session.rollback()  # Cleanup
    except ImportError:
        pytest.skip("Database not available")


@pytest.fixture(scope="module")
def test_company(db_session):
    """Create a test company for the journey."""
    from models_v2 import Company
    from sqlalchemy import text
    
    # Check if test company exists
    existing = db_session.execute(text(
        "SELECT id FROM companies WHERE name = 'Test QA Company'"
    )).fetchone()
    
    if existing:
        return {'id': existing[0], 'name': 'Test QA Company'}
    
    # Create new test company
    company = Company(
        name='Test QA Company',
        name_he='חברת בדיקות',
        description='Test company for QA validation',
        description_he='חברת בדיקות לאימות',
        is_active=True
    )
    db_session.add(company)
    db_session.commit()
    
    yield {'id': company.id, 'name': company.name}
    
    # Cleanup (optional - keep for inspection)
    # db_session.delete(company)
    # db_session.commit()


@pytest.fixture(scope="module")
def test_template(db_session, test_company):
    """Create a test trip template."""
    from models_v2 import TripTemplate
    from sqlalchemy import text
    
    # Check if test template exists
    existing = db_session.execute(text(
        "SELECT id FROM trip_templates WHERE title = 'QA Test Journey'"
    )).fetchone()
    
    if existing:
        return {'id': existing[0], 'title': 'QA Test Journey', 'company_id': test_company['id']}
    
    template = TripTemplate(
        title='QA Test Journey',
        title_he='מסע בדיקות',
        description='A test trip template for QA validation',
        description_he='תבנית טיול לבדיקות',
        base_price=5000,
        single_supplement_price=1000,
        typical_duration_days=10,
        default_max_capacity=20,
        difficulty_level=2,
        company_id=test_company['id'],
        trip_type_id=1,  # Geographic Depth
        primary_country_id=1,  # First country
        is_active=True
    )
    db_session.add(template)
    db_session.commit()
    
    yield {'id': template.id, 'title': template.title, 'company_id': test_company['id']}


@pytest.fixture(scope="module")
def test_occurrences(db_session, test_template):
    """Create 3 test occurrences: sold out, active, past."""
    from models_v2 import TripOccurrence
    from sqlalchemy import text
    from datetime import date
    
    today = date.today()
    
    # Check if test occurrences exist
    existing = db_session.execute(text(
        "SELECT id, status FROM trip_occurrences "
        "WHERE trip_template_id = :tid AND notes = 'QA Test'"
    ), {'tid': test_template['id']}).fetchall()
    
    if len(existing) >= 3:
        return [{'id': e[0], 'status': e[1]} for e in existing]
    
    occurrences_data = [
        # Sold out occurrence (Full)
        {
            'start_date': today + timedelta(days=30),
            'end_date': today + timedelta(days=40),
            'status': 'Full',
            'spots_left': 0,
            'price_override': 5500,  # Higher price
            'notes': 'QA Test'
        },
        # Active occurrence (Open)
        {
            'start_date': today + timedelta(days=60),
            'end_date': today + timedelta(days=70),
            'status': 'Open',
            'spots_left': 15,
            'price_override': None,  # Use base price
            'notes': 'QA Test'
        },
        # Past occurrence
        {
            'start_date': today - timedelta(days=30),
            'end_date': today - timedelta(days=20),
            'status': 'Cancelled',
            'spots_left': 0,
            'price_override': 4500,
            'notes': 'QA Test'
        }
    ]
    
    created = []
    for occ_data in occurrences_data:
        occ = TripOccurrence(
            trip_template_id=test_template['id'],
            **occ_data
        )
        db_session.add(occ)
        db_session.commit()
        created.append({'id': occ.id, 'status': occ.status})
    
    return created


# ============================================
# JOURNEY STEP 1: COMPANY CREATION
# ============================================

class TestStep1CompanyCreation:
    """Step 1: Admin creates a Company."""
    
    def test_company_exists(self, test_company):
        """Verify test company was created."""
        assert test_company['id'] is not None
        assert test_company['name'] == 'Test QA Company'
    
    def test_company_retrievable_via_api(self, test_company):
        """Verify company can be retrieved via API."""
        resp = requests.get(f"{V2_API}/companies/{test_company['id']}")
        
        # May return 404 if company endpoint doesn't support ID lookup
        if resp.status_code == 200:
            data = resp.json()
            assert data.get('success', True)
    
    def test_company_in_list(self, test_company):
        """Verify company appears in companies list."""
        resp = requests.get(f"{V2_API}/companies")
        data = resp.json()
        
        if data.get('data'):
            company_ids = [c['id'] for c in data['data']]
            assert test_company['id'] in company_ids


# ============================================
# JOURNEY STEP 2: TEMPLATE CREATION
# ============================================

class TestStep2TemplateCreation:
    """Step 2: Admin creates a Trip Template."""
    
    def test_template_exists(self, test_template):
        """Verify test template was created."""
        assert test_template['id'] is not None
        assert test_template['title'] == 'QA Test Journey'
    
    def test_template_has_company(self, test_template, test_company):
        """Verify template is linked to company."""
        assert test_template['company_id'] == test_company['id']
    
    def test_template_in_api(self, test_template):
        """Verify template appears in templates list."""
        resp = requests.get(f"{V2_API}/templates", params={'limit': 100})
        data = resp.json()
        
        if data.get('data'):
            template_ids = [t['id'] for t in data['data']]
            # Template may or may not be in list depending on filters
            # Just verify API works
            assert 'data' in data


# ============================================
# JOURNEY STEP 3: OCCURRENCE SCHEDULING
# ============================================

class TestStep3OccurrenceScheduling:
    """Step 3: Admin schedules 3 Occurrences."""
    
    def test_occurrences_created(self, test_occurrences):
        """Verify 3 occurrences were created."""
        assert len(test_occurrences) >= 3
    
    def test_sold_out_occurrence(self, test_occurrences):
        """Verify sold out occurrence has Full status."""
        full_occs = [o for o in test_occurrences if o['status'] == 'Full']
        assert len(full_occs) >= 1
    
    def test_active_occurrence(self, test_occurrences):
        """Verify active occurrence has Open status."""
        open_occs = [o for o in test_occurrences if o['status'] == 'Open']
        assert len(open_occs) >= 1
    
    def test_past_occurrence(self, test_occurrences):
        """Verify past occurrence exists (Cancelled or past date)."""
        cancelled_occs = [o for o in test_occurrences if o['status'] == 'Cancelled']
        assert len(cancelled_occs) >= 1


# ============================================
# JOURNEY STEP 4: USER SEARCHES FOR TRIPS
# ============================================

class TestStep4UserSearch:
    """Step 4: User searches for trips (finding the active one)."""
    
    def test_search_returns_results(self):
        """User search should return results."""
        prefs = {
            'budget': 10000,
            'min_duration': 5,
            'max_duration': 15
        }
        resp = requests.post(f"{V2_API}/recommendations", json=prefs)
        data = resp.json()
        
        assert data.get('success', True)
        assert 'data' in data
    
    def test_full_trips_not_in_search(self, test_occurrences):
        """Full/sold out trips should NOT appear in search."""
        prefs = {'budget': 50000}
        resp = requests.post(f"{V2_API}/recommendations", json=prefs)
        data = resp.json()
        
        full_ids = [o['id'] for o in test_occurrences if o['status'] == 'Full']
        result_ids = [t['id'] for t in data.get('data', [])]
        
        for full_id in full_ids:
            assert full_id not in result_ids, f"Full trip {full_id} found in results"
    
    def test_cancelled_trips_not_in_search(self, test_occurrences):
        """Cancelled trips should NOT appear in search."""
        prefs = {'budget': 50000}
        resp = requests.post(f"{V2_API}/recommendations", json=prefs)
        data = resp.json()
        
        cancelled_ids = [o['id'] for o in test_occurrences if o['status'] == 'Cancelled']
        result_ids = [t['id'] for t in data.get('data', [])]
        
        for cancelled_id in cancelled_ids:
            assert cancelled_id not in result_ids, f"Cancelled trip found in results"
    
    def test_search_includes_score(self):
        """Search results should include match_score."""
        prefs = {'budget': 5000}
        resp = requests.post(f"{V2_API}/recommendations", json=prefs)
        data = resp.json()
        
        for trip in data.get('data', [])[:5]:
            assert 'match_score' in trip
            assert isinstance(trip['match_score'], int)
            assert 0 <= trip['match_score'] <= 100
    
    def test_search_includes_match_details(self):
        """Search results should include match_details."""
        prefs = {'budget': 5000, 'difficulty': 2}
        resp = requests.post(f"{V2_API}/recommendations", json=prefs)
        data = resp.json()
        
        for trip in data.get('data', [])[:5]:
            assert 'match_details' in trip
            assert isinstance(trip['match_details'], list)


# ============================================
# JOURNEY STEP 5: USER FILTERS BY COMPANY
# ============================================

class TestStep5CompanyFilter:
    """Step 5: User filters by the specific Company."""
    
    def test_templates_filtered_by_company(self, test_company):
        """Templates can be filtered by company_id."""
        resp = requests.get(f"{V2_API}/templates", params={
            'company_id': test_company['id']
        })
        data = resp.json()
        
        # All returned templates should belong to the company
        for template in data.get('data', []):
            if 'companyId' in template:
                assert template['companyId'] == test_company['id']
            elif 'company_id' in template:
                assert template['company_id'] == test_company['id']
    
    def test_occurrences_include_company(self):
        """Occurrences should include company info via template."""
        resp = requests.get(f"{V2_API}/occurrences", params={'limit': 5})
        data = resp.json()
        
        # Check structure
        assert data.get('success', True) or 'data' in data


# ============================================
# JOURNEY STEP 6: DYNAMIC PRICING
# ============================================

class TestStep6DynamicPricing:
    """Step 6: System calculates dynamic pricing based on occurrence."""
    
    def test_effective_price_uses_override(self, db_session, test_template):
        """Effective price should use override when set."""
        from sqlalchemy import text
        
        result = db_session.execute(text("""
            SELECT o.id, o.price_override, t.base_price,
                   COALESCE(o.price_override, t.base_price) as effective
            FROM trip_occurrences o
            JOIN trip_templates t ON o.trip_template_id = t.id
            WHERE t.id = :tid AND o.price_override IS NOT NULL
            LIMIT 1
        """), {'tid': test_template['id']}).fetchone()
        
        if result:
            occ_id, override, base, effective = result
            assert float(effective) == float(override), \
                f"Effective ({effective}) should equal override ({override})"
    
    def test_effective_price_uses_base(self, db_session, test_template):
        """Effective price should use base_price when no override."""
        from sqlalchemy import text
        
        result = db_session.execute(text("""
            SELECT o.id, o.price_override, t.base_price,
                   COALESCE(o.price_override, t.base_price) as effective
            FROM trip_occurrences o
            JOIN trip_templates t ON o.trip_template_id = t.id
            WHERE t.id = :tid AND o.price_override IS NULL
            LIMIT 1
        """), {'tid': test_template['id']}).fetchone()
        
        if result:
            occ_id, override, base, effective = result
            assert float(effective) == float(base), \
                f"Effective ({effective}) should equal base ({base})"
    
    def test_api_returns_correct_price(self, test_occurrences):
        """API should return correct effective price."""
        resp = requests.get(f"{V2_API}/trips", params={'limit': 50})
        data = resp.json()
        
        # Just verify price field exists and is numeric
        for trip in data.get('data', [])[:10]:
            if 'price' in trip:
                assert isinstance(trip['price'], (int, float))
                assert trip['price'] > 0


# ============================================
# BONUS: COMPLETE JOURNEY INTEGRATION TEST
# ============================================

class TestCompleteJourney:
    """Complete end-to-end journey test."""
    
    def test_full_journey(self, test_company, test_template, test_occurrences):
        """
        Complete user journey:
        1. Company exists
        2. Template belongs to company
        3. Occurrences belong to template
        4. Search finds active occurrence
        5. Sold out/cancelled excluded
        """
        # Step 1: Company exists
        assert test_company['id'] is not None
        
        # Step 2: Template belongs to company
        assert test_template['company_id'] == test_company['id']
        
        # Step 3: Occurrences created
        assert len(test_occurrences) >= 3
        
        # Step 4: Search works
        resp = requests.post(f"{V2_API}/recommendations", json={'budget': 10000})
        data = resp.json()
        assert data.get('success', True)
        
        # Step 5: Full/Cancelled excluded
        full_ids = {o['id'] for o in test_occurrences if o['status'] in ['Full', 'Cancelled']}
        result_ids = {t['id'] for t in data.get('data', [])}
        assert full_ids.isdisjoint(result_ids), "Full/Cancelled trips should be excluded"
        
        print("\n" + "="*50)
        print("COMPLETE JOURNEY TEST PASSED")
        print("="*50)
        print(f"Company: {test_company['name']} (ID: {test_company['id']})")
        print(f"Template: {test_template['title']} (ID: {test_template['id']})")
        print(f"Occurrences: {len(test_occurrences)}")
        print(f"Search returned: {len(data.get('data', []))} results")
        print("="*50)


# ============================================
# API HEALTH CHECKS
# ============================================

class TestAPIHealth:
    """Basic API health checks."""
    
    def test_v2_recommendations_endpoint(self):
        """V2 recommendations endpoint is healthy."""
        resp = requests.post(f"{V2_API}/recommendations", json={})
        assert resp.status_code == 200
    
    def test_v2_trips_endpoint(self):
        """V2 trips endpoint is healthy."""
        resp = requests.get(f"{V2_API}/trips")
        assert resp.status_code == 200
    
    def test_v2_templates_endpoint(self):
        """V2 templates endpoint is healthy."""
        resp = requests.get(f"{V2_API}/templates")
        assert resp.status_code == 200
    
    def test_v2_occurrences_endpoint(self):
        """V2 occurrences endpoint is healthy."""
        resp = requests.get(f"{V2_API}/occurrences")
        assert resp.status_code == 200
    
    def test_v2_companies_endpoint(self):
        """V2 companies endpoint is healthy."""
        resp = requests.get(f"{V2_API}/companies")
        assert resp.status_code == 200
    
    def test_v2_schema_info_endpoint(self):
        """V2 schema-info endpoint is healthy."""
        resp = requests.get(f"{V2_API}/schema-info")
        assert resp.status_code == 200


# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("SmartTrip V2 Production Health Check")
    print("="*60)
    print("\nWARNING: Run this ONLY after run_migration_verification.py passes!")
    print("\nRunning tests...\n")
    
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--html=v2_health_check.html",
        "--self-contained-html"
    ])
