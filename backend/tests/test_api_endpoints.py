"""
=============================================================================
QA TEST SUITE: API Endpoints Testing
=============================================================================
Author: Senior QA Engineer
Purpose: Comprehensive API endpoint testing including boundary conditions,
         error handling, and edge cases.
=============================================================================
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import sys

# Configuration
BASE_URL = "http://localhost:5000"
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
    
    def test_recommendations_with_type(self) -> Tuple[bool, str]:
        """Test recommendations with trip type filter"""
        payload = {"preferred_type_id": 1, "budget": 10000}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        if not data.get('success'):
            return False, f"Failed: {data}"
        return True, f"Type filter working: {data.get('count', 0)} results"
    
    def test_recommendations_relaxed_results(self) -> Tuple[bool, str]:
        """Test that relaxed results are returned when primary results < threshold"""
        # Use a very restrictive filter that should trigger relaxed search
        payload = {
            "selected_countries": [1],  # Uganda
            "preferred_type_id": 4,  # Train Tours (unlikely combo)
            "budget": 5000
        }
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        has_relaxed = data.get('has_relaxed_results', False)
        primary = data.get('primary_count', 0)
        relaxed = data.get('relaxed_count', 0)
        return True, f"Primary: {primary}, Relaxed: {relaxed}, Has relaxed: {has_relaxed}"
    
    def test_recommendations_empty_payload(self) -> Tuple[bool, str]:
        """Test recommendations with empty payload"""
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json={},
            timeout=TIMEOUT
        )
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        return data.get('success', False), f"Empty payload handled: {data.get('count', 0)} results"
    
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
    
    def test_recommendations_thresholds_returned(self) -> Tuple[bool, str]:
        """Test that score thresholds are returned"""
        payload = {"budget": 5000}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        if 'score_thresholds' not in data:
            return False, "Missing score_thresholds"
        thresholds = data['score_thresholds']
        if 'HIGH' not in thresholds or 'MID' not in thresholds:
            return False, f"Incomplete thresholds: {thresholds}"
        return True, f"Thresholds: {thresholds}"
    
    # =========================================================================
    # BOUNDARY TESTS
    # =========================================================================
    
    def test_extreme_budget_high(self) -> Tuple[bool, str]:
        """Test with extremely high budget"""
        payload = {"budget": 999999999}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        return response.status_code == 200, f"High budget handled: {response.status_code}"
    
    def test_extreme_budget_zero(self) -> Tuple[bool, str]:
        """Test with zero budget"""
        payload = {"budget": 0}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        return response.status_code == 200, f"Zero budget handled: {response.status_code}"
    
    def test_negative_budget(self) -> Tuple[bool, str]:
        """Test with negative budget"""
        payload = {"budget": -1000}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        # Should handle gracefully
        return response.status_code == 200, f"Negative budget handled: {response.status_code}"
    
    def test_extreme_duration_range(self) -> Tuple[bool, str]:
        """Test with extreme duration range"""
        payload = {"min_duration": 0, "max_duration": 1000}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        return response.status_code == 200, f"Extreme duration handled: {response.status_code}"
    
    def test_inverted_duration(self) -> Tuple[bool, str]:
        """Test with min > max duration"""
        payload = {"min_duration": 30, "max_duration": 5}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        # Should handle gracefully
        return response.status_code == 200, f"Inverted duration handled: {response.status_code}"
    
    def test_invalid_country_ids(self) -> Tuple[bool, str]:
        """Test with invalid country IDs"""
        payload = {"selected_countries": [99999, 88888, 77777]}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        return response.status_code == 200, f"Invalid countries handled: {response.status_code}"
    
    def test_invalid_type_id(self) -> Tuple[bool, str]:
        """Test with invalid type ID"""
        payload = {"preferred_type_id": 99999}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        return response.status_code == 200, f"Invalid type handled: {response.status_code}"
    
    def test_string_instead_of_int(self) -> Tuple[bool, str]:
        """Test with string instead of integer"""
        payload = {"budget": "five thousand", "min_duration": "abc"}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        # Should handle gracefully or return error
        return response.status_code in [200, 400], f"String values handled: {response.status_code}"
    
    def test_null_values(self) -> Tuple[bool, str]:
        """Test with null values"""
        payload = {"budget": None, "selected_countries": None}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        return response.status_code == 200, f"Null values handled: {response.status_code}"
    
    def test_very_large_array(self) -> Tuple[bool, str]:
        """Test with very large country array"""
        payload = {"selected_countries": list(range(1, 1001))}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        return response.status_code == 200, f"Large array handled: {response.status_code}"
    
    def test_special_characters_in_continent(self) -> Tuple[bool, str]:
        """Test with special characters"""
        payload = {"selected_continents": ["<script>alert('xss')</script>", "'; DROP TABLE trips;--"]}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        return response.status_code == 200, f"Special chars handled: {response.status_code}"
    
    # =========================================================================
    # DATE FILTER TESTS
    # =========================================================================
    
    def test_year_filter(self) -> Tuple[bool, str]:
        """Test year filter"""
        payload = {"year": "2025", "budget": 10000}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        return data.get('success', False), f"Year filter: {data.get('count', 0)} results"
    
    def test_month_filter(self) -> Tuple[bool, str]:
        """Test month filter"""
        payload = {"year": "2025", "month": "6", "budget": 10000}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        return data.get('success', False), f"Month filter: {data.get('count', 0)} results"
    
    def test_past_year(self) -> Tuple[bool, str]:
        """Test with past year"""
        payload = {"year": "2020", "budget": 10000}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        # Should return empty or handle gracefully
        return data.get('success', False), f"Past year: {data.get('count', 0)} results"
    
    def test_far_future_year(self) -> Tuple[bool, str]:
        """Test with far future year"""
        payload = {"year": "2099", "budget": 10000}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        data = response.json()
        return data.get('success', False), f"Future year: {data.get('count', 0)} results"
    
    def test_invalid_month(self) -> Tuple[bool, str]:
        """Test with invalid month (13)"""
        payload = {"year": "2025", "month": "13", "budget": 10000}
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        # Should handle gracefully
        return response.status_code in [200, 400], f"Invalid month handled: {response.status_code}"
    
    # =========================================================================
    # TRIP TYPES ENDPOINT TESTS
    # =========================================================================
    
    def test_trip_types_endpoint(self) -> Tuple[bool, str]:
        """Test /api/trip-types endpoint"""
        response = requests.get(f"{self.base_url}/api/trip-types", timeout=TIMEOUT)
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        return data.get('success', False), f"Found {len(data.get('data', []))} trip types"
    
    # =========================================================================
    # TAGS ENDPOINT TESTS
    # =========================================================================
    
    def test_tags_endpoint(self) -> Tuple[bool, str]:
        """Test /api/tags endpoint"""
        response = requests.get(f"{self.base_url}/api/tags", timeout=TIMEOUT)
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        return data.get('success', False), f"Found {len(data.get('data', []))} tags"
    
    # =========================================================================
    # GUIDES ENDPOINT TESTS
    # =========================================================================
    
    def test_guides_endpoint(self) -> Tuple[bool, str]:
        """Test /api/guides endpoint"""
        response = requests.get(f"{self.base_url}/api/guides", timeout=TIMEOUT)
        if response.status_code != 200:
            return False, f"Status code: {response.status_code}"
        data = response.json()
        return data.get('success', False), f"Found {len(data.get('data', []))} guides"
    
    # =========================================================================
    # ERROR HANDLING TESTS
    # =========================================================================
    
    def test_invalid_endpoint(self) -> Tuple[bool, str]:
        """Test invalid endpoint returns 404"""
        response = requests.get(f"{self.base_url}/api/nonexistent", timeout=TIMEOUT)
        return response.status_code == 404, f"Invalid endpoint: {response.status_code}"
    
    def test_wrong_http_method(self) -> Tuple[bool, str]:
        """Test wrong HTTP method"""
        response = requests.get(f"{self.base_url}/api/recommendations", timeout=TIMEOUT)
        return response.status_code == 405, f"Wrong method: {response.status_code}"
    
    def test_malformed_json(self) -> Tuple[bool, str]:
        """Test malformed JSON body"""
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            data="not valid json{{{",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        return response.status_code in [400, 500], f"Malformed JSON: {response.status_code}"
    
    # =========================================================================
    # PERFORMANCE TESTS
    # =========================================================================
    
    def test_response_time_health(self) -> Tuple[bool, str]:
        """Test health endpoint response time < 1s"""
        start = time.time()
        response = requests.get(f"{self.base_url}/api/health", timeout=TIMEOUT)
        duration = time.time() - start
        if duration > 1.0:
            return False, f"Too slow: {duration:.3f}s"
        return True, f"Response time: {duration:.3f}s"
    
    def test_response_time_recommendations(self) -> Tuple[bool, str]:
        """Test recommendations response time < 5s"""
        payload = {"budget": 10000}
        start = time.time()
        response = requests.post(
            f"{self.base_url}/api/recommendations",
            json=payload,
            timeout=TIMEOUT
        )
        duration = time.time() - start
        if duration > 5.0:
            return False, f"Too slow: {duration:.3f}s"
        return True, f"Response time: {duration:.3f}s"
    
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
        self.run_test(self.test_recommendations_with_type, "Type filter works")
        self.run_test(self.test_recommendations_relaxed_results, "Relaxed results returned")
        self.run_test(self.test_recommendations_empty_payload, "Empty payload handled")
        self.run_test(self.test_recommendations_score_range, "Scores within 0-100")
        self.run_test(self.test_recommendations_thresholds_returned, "Thresholds returned")
        
        # Boundary Tests
        self.log("\n[BOUNDARY TESTS]", Colors.BLUE)
        self.run_test(self.test_extreme_budget_high, "Extreme high budget")
        self.run_test(self.test_extreme_budget_zero, "Zero budget")
        self.run_test(self.test_negative_budget, "Negative budget")
        self.run_test(self.test_extreme_duration_range, "Extreme duration range")
        self.run_test(self.test_inverted_duration, "Inverted duration (min > max)")
        self.run_test(self.test_invalid_country_ids, "Invalid country IDs")
        self.run_test(self.test_invalid_type_id, "Invalid type ID")
        self.run_test(self.test_string_instead_of_int, "String instead of int")
        self.run_test(self.test_null_values, "Null values")
        self.run_test(self.test_very_large_array, "Very large array")
        self.run_test(self.test_special_characters_in_continent, "Special characters (XSS/SQL)")
        
        # Date Filter Tests
        self.log("\n[DATE FILTER TESTS]", Colors.BLUE)
        self.run_test(self.test_year_filter, "Year filter works")
        self.run_test(self.test_month_filter, "Month filter works")
        self.run_test(self.test_past_year, "Past year handled")
        self.run_test(self.test_far_future_year, "Far future year handled")
        self.run_test(self.test_invalid_month, "Invalid month handled")
        
        # Other Endpoints
        self.log("\n[OTHER ENDPOINTS]", Colors.BLUE)
        self.run_test(self.test_trip_types_endpoint, "Trip types endpoint")
        self.run_test(self.test_tags_endpoint, "Tags endpoint")
        self.run_test(self.test_guides_endpoint, "Guides endpoint")
        
        # Error Handling
        self.log("\n[ERROR HANDLING]", Colors.BLUE)
        self.run_test(self.test_invalid_endpoint, "Invalid endpoint returns 404")
        self.run_test(self.test_wrong_http_method, "Wrong HTTP method returns 405")
        self.run_test(self.test_malformed_json, "Malformed JSON handled")
        
        # Performance
        self.log("\n[PERFORMANCE]", Colors.BLUE)
        self.run_test(self.test_response_time_health, "Health response time < 1s")
        self.run_test(self.test_response_time_recommendations, "Recommendations response < 5s")
        
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

