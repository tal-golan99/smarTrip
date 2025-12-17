"""
=============================================================================
QA TEST SUITE: API Endpoints Testing
=============================================================================
Author: Senior QA Engineer
Purpose: Comprehensive API endpoint testing including boundary conditions,
         error handling, and edge cases.

NOTE: Moved from backend/tests/ during cleanup.
Run with: python tests/integration/test_api_endpoints.py
=============================================================================
"""

import requests
import json
import time
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

# Add backend to path for imports if needed
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backend'))

# Configuration
BASE_URL = os.environ.get('API_URL', 'http://localhost:5000')
TIMEOUT = 30

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestResult:
    """Store individual test results"""
    def __init__(self, name: str, passed: bool, details: str = "", duration: float = 0):
        self.name = name
        self.passed = passed
        self.details = details
        self.duration = duration

class APITestSuite:
    """Comprehensive API Testing Suite"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.start_time = None
        
    def log(self, message: str, color: str = ""):
        """Print colored log message"""
        print(f"{color}{message}{Colors.END}")
    
    def run_test(self, test_func, test_name: str) -> TestResult:
        """Run a single test and record result"""
        start = time.time()
        try:
            passed, details = test_func()
            duration = time.time() - start
            result = TestResult(test_name, passed, details, duration)
        except Exception as e:
            duration = time.time() - start
            result = TestResult(test_name, False, f"Exception: {str(e)}", duration)
        
        self.results.append(result)
        status = f"{Colors.GREEN}PASS{Colors.END}" if result.passed else f"{Colors.RED}FAIL{Colors.END}"
        self.log(f"  [{status}] {test_name} ({duration:.3f}s)")
        if not result.passed:
            self.log(f"       Details: {result.details}", Colors.YELLOW)
        return result
    
    # =========================================================================
    # HEALTH CHECK TESTS
    # =========================================================================
    
    def test_health_endpoint(self) -> Tuple[bool, str]:
        """Test /api/health endpoint"""
        response = requests.get(f"{self.base_url}/api/health", timeout=TIMEOUT)
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        if data.get('status') != 'healthy':
            return False, f"Status not healthy: {data}"
        return True, "Health check passed"
    
    def test_health_database_info(self) -> Tuple[bool, str]:
        """Test that health endpoint returns database info"""
        response = requests.get(f"{self.base_url}/api/health", timeout=TIMEOUT)
        data = response.json()
        if 'database' not in data:
            return False, "Missing database info"
        db_info = data['database']
        required_fields = ['trips', 'countries', 'guides', 'tags']
        for field in required_fields:
            if field not in db_info:
                return False, f"Missing field: {field}"
        return True, f"Database info complete: {db_info}"
    
    # =========================================================================
    # COUNTRIES ENDPOINT TESTS
    # =========================================================================
    
    def test_countries_endpoint(self) -> Tuple[bool, str]:
        """Test /api/countries endpoint"""
        response = requests.get(f"{self.base_url}/api/countries", timeout=TIMEOUT)
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        if not data.get('success'):
            return False, "Success flag is False"
        if 'data' not in data:
            return False, "Missing data field"
        return True, f"Found {len(data['data'])} countries"
    
    def test_countries_structure(self) -> Tuple[bool, str]:
        """Test country data structure"""
        response = requests.get(f"{self.base_url}/api/countries", timeout=TIMEOUT)
        data = response.json()
        if not data['data']:
            return False, "No countries in response"
        country = data['data'][0]
        required_fields = ['id', 'name', 'continent']
        for field in required_fields:
            if field not in country:
                return False, f"Missing field: {field}"
        return True, f"Country structure valid: {list(country.keys())}"
    
    # =========================================================================
    # TRIPS ENDPOINT TESTS
    # =========================================================================
    
    def test_trips_endpoint(self) -> Tuple[bool, str]:
        """Test /api/trips endpoint"""
        response = requests.get(f"{self.base_url}/api/trips", timeout=TIMEOUT)
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        if not data.get('success'):
            return False, "Success flag is False"
        return True, f"Found {len(data.get('data', []))} trips"
    
    def test_trips_pagination(self) -> Tuple[bool, str]:
        """Test trips pagination"""
        response = requests.get(f"{self.base_url}/api/trips?limit=5", timeout=TIMEOUT)
        data = response.json()
        if len(data.get('data', [])) > 5:
            return False, f"Pagination failed: got {len(data['data'])} items"
        return True, f"Pagination working: {len(data.get('data', []))} items"
    
    def test_single_trip(self) -> Tuple[bool, str]:
        """Test /api/trips/<id> endpoint"""
        # First get a valid trip ID
        response = requests.get(f"{self.base_url}/api/trips?limit=1", timeout=TIMEOUT)
        data = response.json()
        if not data.get('data'):
            return False, "No trips available"
        trip_id = data['data'][0]['id']
        
        # Now get single trip
        response = requests.get(f"{self.base_url}/api/trips/{trip_id}", timeout=TIMEOUT)
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        return True, f"Trip {trip_id} retrieved successfully"
    
    def test_invalid_trip_id(self) -> Tuple[bool, str]:
        """Test /api/trips with invalid ID"""
        response = requests.get(f"{self.base_url}/api/trips/999999", timeout=TIMEOUT)
        if response.status_code == 404:
            return True, "Correctly returns 404 for invalid ID"
        return False, f"Expected 404, got {response.status_code}"
    
    def test_negative_trip_id(self) -> Tuple[bool, str]:
        """Test /api/trips with negative ID"""
        response = requests.get(f"{self.base_url}/api/trips/-1", timeout=TIMEOUT)
        if response.status_code in [400, 404]:
            return True, f"Correctly handles negative ID: {response.status_code}"
        return False, f"Expected 400/404, got {response.status_code}"
    
    # =========================================================================
    # RECOMMENDATIONS ENDPOINT TESTS
    # =========================================================================
    
    def test_recommendations_basic(self) -> Tuple[bool, str]:
        """Test basic recommendations endpoint"""
        payload = {"min_duration": 5, "max_duration": 20, "budget": 5000}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        if not data.get('success'):
            return False, f"Success flag is False: {data}"
        return True, f"Found {data.get('count', 0)} recommendations"
    
    def test_recommendations_with_countries(self) -> Tuple[bool, str]:
        """Test recommendations with country filter"""
        payload = {"selected_countries": [1, 2, 3], "budget": 10000}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        if not data.get('success'):
            return False, f"Failed: {data}"
        return True, f"Country filter working: {data.get('count', 0)} results"
    
    def test_recommendations_score_range(self) -> Tuple[bool, str]:
        """Test that all scores are within 0-100 range"""
        payload = {"budget": 20000}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        for trip in data.get('data', []):
            score = trip.get('match_score', 0)
            if score < 0 or score > 100:
                return False, f"Score out of range: {score}"
        return True, "All scores within 0-100 range"
    
    # =========================================================================
    # OTHER ENDPOINTS
    # =========================================================================
    
    def test_trip_types_endpoint(self) -> Tuple[bool, str]:
        """Test /api/trip-types endpoint"""
        response = requests.get(f"{self.base_url}/api/trip-types", timeout=TIMEOUT)
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        return data.get('success', False), f"Found {len(data.get('data', []))} trip types"
    
    def test_tags_endpoint(self) -> Tuple[bool, str]:
        """Test /api/tags endpoint"""
        response = requests.get(f"{self.base_url}/api/tags", timeout=TIMEOUT)
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        return data.get('success', False), f"Found {len(data.get('data', []))} tags"
    
    def test_guides_endpoint(self) -> Tuple[bool, str]:
        """Test /api/guides endpoint"""
        response = requests.get(f"{self.base_url}/api/guides", timeout=TIMEOUT)
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        return data.get('success', False), f"Found {len(data.get('data', []))} guides"
    
    # =========================================================================
    # RUN ALL TESTS
    # =========================================================================
    
    def run_all_tests(self):
        """Run all API tests"""
        self.start_time = time.time()
        self.log("\n" + "="*70, Colors.CYAN)
        self.log("  API ENDPOINT TEST SUITE", Colors.BOLD)
        self.log("="*70, Colors.CYAN)
        
        # Health Tests
        self.log("\n[HEALTH CHECKS]", Colors.BLUE)
        self.run_test(self.test_health_endpoint, "Health endpoint returns 200")
        self.run_test(self.test_health_database_info, "Health includes database info")
        
        # Countries Tests
        self.log("\n[COUNTRIES ENDPOINT]", Colors.BLUE)
        self.run_test(self.test_countries_endpoint, "Countries endpoint returns data")
        self.run_test(self.test_countries_structure, "Countries have correct structure")
        
        # Trips Tests
        self.log("\n[TRIPS ENDPOINT]", Colors.BLUE)
        self.run_test(self.test_trips_endpoint, "Trips endpoint returns data")
        self.run_test(self.test_trips_pagination, "Trips pagination works")
        self.run_test(self.test_single_trip, "Single trip retrieval works")
        self.run_test(self.test_invalid_trip_id, "Invalid trip ID returns 404")
        self.run_test(self.test_negative_trip_id, "Negative trip ID handled")
        
        # Recommendations Tests
        self.log("\n[RECOMMENDATIONS ENDPOINT]", Colors.BLUE)
        self.run_test(self.test_recommendations_basic, "Basic recommendations work")
        self.run_test(self.test_recommendations_with_countries, "Country filter works")
        self.run_test(self.test_recommendations_score_range, "Scores within 0-100")
        
        # Other Endpoints
        self.log("\n[OTHER ENDPOINTS]", Colors.BLUE)
        self.run_test(self.test_trip_types_endpoint, "Trip types endpoint")
        self.run_test(self.test_tags_endpoint, "Tags endpoint")
        self.run_test(self.test_guides_endpoint, "Guides endpoint")
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        total_duration = time.time() - self.start_time
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)
        
        self.log("\n" + "="*70, Colors.CYAN)
        self.log("  TEST SUMMARY", Colors.BOLD)
        self.log("="*70, Colors.CYAN)
        self.log(f"\n  Total Tests: {total}")
        self.log(f"  {Colors.GREEN}Passed: {passed}{Colors.END}")
        self.log(f"  {Colors.RED}Failed: {failed}{Colors.END}")
        self.log(f"  Pass Rate: {(passed/total*100):.1f}%")
        self.log(f"  Duration: {total_duration:.2f}s")
        
        if failed > 0:
            self.log(f"\n  {Colors.RED}FAILED TESTS:{Colors.END}")
            for r in self.results:
                if not r.passed:
                    self.log(f"    - {r.name}: {r.details}", Colors.YELLOW)
        
        self.log("\n" + "="*70 + "\n", Colors.CYAN)
        return passed, failed


if __name__ == "__main__":
    suite = APITestSuite()
    suite.run_all_tests()
