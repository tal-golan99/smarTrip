#!/usr/bin/env python
"""
SmartTrip Test Suite Runner
===========================

Executes the complete test suite including:
- Backend unit tests (Database, API, Analytics, Cron, Recommender)
- E2E tests (if Playwright is configured)

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --backend    # Run backend tests only
    python run_tests.py --e2e        # Run E2E tests only
    python run_tests.py --coverage   # Run with coverage report
    python run_tests.py --quick      # Run quick subset
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def run_command(cmd, description):
    """Run a shell command and return success status."""
    print(f"[RUNNING] {description}")
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    if result.returncode == 0:
        print(f"\n[OK] {description} - PASSED\n")
    else:
        print(f"\n[FAIL] {description} - FAILED (exit code: {result.returncode})\n")
    
    return result.returncode == 0


def run_backend_tests(coverage=False, verbose=True, markers=None):
    """Run backend pytest tests."""
    print_header("BACKEND TESTS (pytest)")
    
    cmd = [sys.executable, "-m", "pytest", "tests/backend/"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=backend", "--cov-report=html", "--cov-report=term"])
    
    if markers:
        cmd.extend(["-m", markers])
    
    # Add additional pytest options
    cmd.extend([
        "--tb=short",           # Short traceback
        "-x",                   # Stop on first failure
        "--durations=10",       # Show 10 slowest tests
    ])
    
    return run_command(cmd, "Backend Tests")


def run_existing_tests(verbose=True):
    """Run event tracking tests from tests/integration/."""
    print_header("EVENT TRACKING TESTS")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/integration/test_event_tracking.py",
        "-v" if verbose else "",
        "--tb=short",
    ]
    
    # Remove empty strings
    cmd = [c for c in cmd if c]
    
    return run_command(cmd, "Event Tracking Tests")


def run_e2e_tests(verbose=True):
    """Run E2E Playwright tests."""
    print_header("E2E TESTS (Playwright)")
    
    # Check if Playwright is available
    try:
        import playwright
        print("[OK] Playwright is installed\n")
    except ImportError:
        print("[SKIP] Playwright not installed. Run: pip install playwright")
        print("       Then: playwright install\n")
        return True  # Don't fail overall suite
    
    cmd = [sys.executable, "-m", "pytest", "tests/e2e/", "-v"]
    
    return run_command(cmd, "E2E Tests")


def run_integration_tests():
    """Run integration test scripts from tests/integration/."""
    print_header("INTEGRATION TESTS (Scripts)")
    
    # Run recommendations test
    cmd1 = [sys.executable, "tests/integration/test_recommendations.py"]
    result1 = run_command(cmd1, "Recommendations Integration Test")
    
    # Run algorithm test
    cmd2 = [sys.executable, "tests/integration/test_algorithm.py"]
    result2 = run_command(cmd2, "Algorithm Integration Test")
    
    return result1 and result2


def check_api_health():
    """Verify API is running before tests."""
    print_header("API HEALTH CHECK")
    
    try:
        import requests
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] API is {data.get('status', 'unknown')}")
            print(f"     Database: {data.get('database', {})}\n")
            return True
        else:
            print(f"[WARN] API returned status {response.status_code}\n")
            return False
    except Exception as e:
        print(f"[ERROR] Cannot connect to API: {e}")
        print("        Make sure Flask is running: python backend/app.py\n")
        return False


def generate_test_report(results):
    """Generate a summary report of test results."""
    print_header("TEST SUMMARY REPORT")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    print(f"Total Test Suites: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    
    for name, result in results.items():
        status = "PASS" if result else "FAIL"
        icon = "[OK]" if result else "[X]"
        print(f"  {icon} {name}: {status}")
    
    print()
    
    if failed == 0:
        print("All tests passed!")
        return 0
    else:
        print(f"{failed} test suite(s) failed.")
        return 1


def main():
    parser = argparse.ArgumentParser(description="SmartTrip Test Suite Runner")
    parser.add_argument("--backend", action="store_true", help="Run backend tests only")
    parser.add_argument("--e2e", action="store_true", help="Run E2E tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--existing", action="store_true", help="Run existing tests only")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--quick", action="store_true", help="Run quick subset of tests")
    parser.add_argument("--skip-health", action="store_true", help="Skip API health check")
    parser.add_argument("-v", "--verbose", action="store_true", default=True, help="Verbose output")
    
    args = parser.parse_args()
    
    print_header(f"SMARTRIP TEST SUITE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Check API health first
    if not args.skip_health:
        api_healthy = check_api_health()
        if not api_healthy and not args.backend:
            print("[WARN] API not available, some tests may fail\n")
    
    # Determine which tests to run
    run_all = not any([args.backend, args.e2e, args.integration, args.existing])
    
    if run_all or args.existing:
        results["Existing Tests"] = run_existing_tests(args.verbose)
    
    if run_all or args.backend:
        results["Backend Tests"] = run_backend_tests(
            coverage=args.coverage,
            verbose=args.verbose,
            markers="db or api" if args.quick else None
        )
    
    if run_all or args.integration:
        # Only run integration tests if API is healthy
        if not args.skip_health and check_api_health():
            results["Integration Tests"] = run_integration_tests()
        else:
            print("[SKIP] Integration tests require running API\n")
    
    if run_all or args.e2e:
        results["E2E Tests"] = run_e2e_tests(args.verbose)
    
    # Generate report
    exit_code = generate_test_report(results)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
