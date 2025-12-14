"""
=============================================================================
QA TEST SUITE: Main Test Runner
=============================================================================
Author: Senior QA Engineer
Purpose: Run all QA tests and generate comprehensive report
=============================================================================
"""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_api_endpoints import APITestSuite
from tests.test_search_scenarios import SearchScenarioTester

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

def main():
    start_time = time.time()
    
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}  TRIP RECOMMENDATIONS - COMPREHENSIVE QA TEST SUITE{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"\n  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Python: {sys.version.split()[0]}")
    
    # =========================================================================
    # PHASE 1: API Endpoint Tests
    # =========================================================================
    print(f"\n{Colors.MAGENTA}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}  PHASE 1: API ENDPOINT TESTS{Colors.END}")
    print(f"{Colors.MAGENTA}{'='*70}{Colors.END}")
    
    api_suite = APITestSuite()
    api_suite.run_all_tests()
    api_passed, api_failed = sum(1 for r in api_suite.results if r.passed), sum(1 for r in api_suite.results if not r.passed)
    
    # =========================================================================
    # PHASE 2: Search Scenario Tests (200+)
    # =========================================================================
    print(f"\n{Colors.MAGENTA}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}  PHASE 2: SEARCH SCENARIO TESTS (200+){Colors.END}")
    print(f"{Colors.MAGENTA}{'='*70}{Colors.END}")
    
    scenario_tester = SearchScenarioTester()
    scenario_tester.run_all_scenarios()
    scenario_passed = sum(1 for r in scenario_tester.results if r.success)
    scenario_failed = sum(1 for r in scenario_tester.results if not r.success)
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    total_time = time.time() - start_time
    total_tests = len(api_suite.results) + len(scenario_tester.results)
    total_passed = api_passed + scenario_passed
    total_failed = api_failed + scenario_failed
    
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}  FINAL SUMMARY{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"\n  API Tests: {api_passed}/{len(api_suite.results)} passed")
    print(f"  Search Scenarios: {scenario_passed}/{len(scenario_tester.results)} passed")
    print(f"  {'='*40}")
    print(f"  {Colors.BOLD}TOTAL: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.1f}%){Colors.END}")
    print(f"  Total Duration: {total_time:.2f}s")
    
    if total_failed == 0:
        print(f"\n  {Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED!{Colors.END}")
    else:
        print(f"\n  {Colors.RED}{Colors.BOLD}{total_failed} TESTS FAILED{Colors.END}")
    
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

