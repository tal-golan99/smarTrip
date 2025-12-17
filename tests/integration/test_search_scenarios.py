"""
=============================================================================
QA TEST SUITE: Search Scenarios (Subset)
=============================================================================
Author: Senior QA Engineer
Purpose: Testing common search/recommendation scenarios.

NOTE: Moved from backend/tests/ during cleanup.
This is a simplified version. Full 200+ scenario suite available separately.
Run with: python tests/integration/test_search_scenarios.py
=============================================================================
"""

import requests
import json
import time
import random
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
from itertools import product

# Add backend to path for imports if needed
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backend'))

# Configuration
BASE_URL = os.environ.get('API_URL', 'http://localhost:5000')
TIMEOUT = 30

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'


class SearchScenarioTester:
    """Test common search scenarios"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results: List[Dict] = []
        self.metadata = {}
        
    def log(self, message: str, color: str = ""):
        print(f"{color}{message}{Colors.END}")
    
    def fetch_metadata(self):
        """Fetch available countries, types, tags for realistic scenarios"""
        self.log("\n[FETCHING METADATA]", Colors.CYAN)
        
        # Countries
        try:
            resp = requests.get(f"{self.base_url}/api/countries", timeout=TIMEOUT)
            data = resp.json()
            self.metadata['countries'] = [c['id'] for c in data.get('data', [])]
            self.metadata['continents'] = list(set(c.get('continent') for c in data.get('data', []) if c.get('continent')))
            self.log(f"  Countries: {len(self.metadata['countries'])}")
            self.log(f"  Continents: {self.metadata['continents']}")
        except Exception as e:
            self.metadata['countries'] = list(range(1, 101))
            self.metadata['continents'] = ['Africa', 'Asia', 'Europe', 'North & Central America', 'South America', 'Oceania']
            self.log(f"  Using default country/continent data", Colors.YELLOW)
        
        # Trip Types
        try:
            resp = requests.get(f"{self.base_url}/api/trip-types", timeout=TIMEOUT)
            data = resp.json()
            self.metadata['types'] = [t['id'] for t in data.get('data', [])]
            self.log(f"  Trip Types: {self.metadata['types']}")
        except:
            self.metadata['types'] = list(range(1, 11))
        
        # Tags
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=TIMEOUT)
            data = resp.json()
            self.metadata['tags'] = [t['id'] for t in data.get('data', [])]
            self.log(f"  Tags: {len(self.metadata['tags'])}")
        except:
            self.metadata['tags'] = list(range(1, 20))
    
    def run_scenario(self, name: str, payload: Dict) -> Dict:
        """Run a single search scenario"""
        start = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/recommendations",
                json=payload,
                timeout=TIMEOUT
            )
            duration = time.time() - start
            
            result = {
                'name': name,
                'payload': payload,
                'status_code': response.status_code,
                'success': False,
                'count': 0,
                'duration': duration,
                'notes': ''
            }
            
            if response.status_code == 200:
                data = response.json()
                result['success'] = data.get('success', False)
                result['count'] = data.get('count', 0)
                result['primary_count'] = data.get('primary_count', 0)
                result['relaxed_count'] = data.get('relaxed_count', 0)
                if data.get('data') and len(data['data']) > 0:
                    result['top_score'] = data['data'][0].get('match_score', 0)
            else:
                result['notes'] = f"HTTP {response.status_code}"
            
            return result
            
        except Exception as e:
            duration = time.time() - start
            return {
                'name': name,
                'payload': payload,
                'status_code': 0,
                'success': False,
                'count': 0,
                'duration': duration,
                'notes': f"Exception: {str(e)}"
            }
    
    def run_common_scenarios(self):
        """Run common search scenarios"""
        self.fetch_metadata()
        
        self.log("\n" + "="*70, Colors.CYAN)
        self.log("  RUNNING COMMON SEARCH SCENARIOS", Colors.BOLD)
        self.log("="*70, Colors.CYAN)
        
        scenarios = [
            # Budget scenarios
            ("Budget $3000", {"budget": 3000}),
            ("Budget $5000", {"budget": 5000}),
            ("Budget $10000", {"budget": 10000}),
            ("Budget $20000", {"budget": 20000}),
            
            # Duration scenarios
            ("Short trip 5-7 days", {"min_duration": 5, "max_duration": 7, "budget": 10000}),
            ("Medium trip 10-14 days", {"min_duration": 10, "max_duration": 14, "budget": 10000}),
            ("Long trip 20-30 days", {"min_duration": 20, "max_duration": 30, "budget": 20000}),
            
            # Continent scenarios
            ("Europe trip", {"selected_continents": ["Europe"], "budget": 10000}),
            ("Asia trip", {"selected_continents": ["Asia"], "budget": 10000}),
            ("Africa trip", {"selected_continents": ["Africa"], "budget": 15000}),
            
            # Difficulty scenarios
            ("Easy trip (1)", {"difficulty": 1, "budget": 10000}),
            ("Moderate trip (2)", {"difficulty": 2, "budget": 10000}),
            ("Hard trip (3)", {"difficulty": 3, "budget": 10000}),
            
            # Combined scenarios
            ("Budget Europe easy", {"selected_continents": ["Europe"], "budget": 5000, "difficulty": 1}),
            ("Luxury Africa safari", {"selected_continents": ["Africa"], "budget": 25000, "min_duration": 10, "max_duration": 14}),
            ("Adventure Asia trek", {"selected_continents": ["Asia"], "budget": 8000, "difficulty": 3}),
            
            # Year/Month scenarios
            ("Year 2025", {"year": "2025", "budget": 10000}),
            ("Summer 2025", {"year": "2025", "month": "7", "budget": 10000}),
            
            # Empty/minimal
            ("No filters", {}),
            ("Just budget", {"budget": 15000}),
        ]
        
        for name, payload in scenarios:
            result = self.run_scenario(name, payload)
            self.results.append(result)
            
            status = f"{Colors.GREEN}OK{Colors.END}" if result['success'] else f"{Colors.RED}FAIL{Colors.END}"
            count_info = f"Count: {result.get('count', 0)}"
            score_info = f"Top: {result.get('top_score', 'N/A')}" if result.get('top_score') else ""
            
            print(f"  [{status}] {name:35} | {count_info:15} | {score_info:10} | {result['duration']:.2f}s")
            
            if result.get('notes') and not result['success']:
                print(f"          Notes: {result['notes']}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "="*70, Colors.CYAN)
        self.log("  SUMMARY", Colors.BOLD)
        self.log("="*70, Colors.CYAN)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['success'])
        failed = total - passed
        
        self.log(f"\n  Total Scenarios: {total}")
        self.log(f"  {Colors.GREEN}Passed: {passed}{Colors.END}")
        self.log(f"  {Colors.RED}Failed: {failed}{Colors.END}")
        self.log(f"  Pass Rate: {(passed/total*100):.1f}%")
        
        # Performance
        durations = [r['duration'] for r in self.results]
        self.log(f"\n  Avg Response Time: {sum(durations)/len(durations):.3f}s")
        self.log(f"  Max Response Time: {max(durations):.3f}s")
        
        self.log("\n" + "="*70 + "\n", Colors.CYAN)


if __name__ == "__main__":
    tester = SearchScenarioTester()
    tester.run_common_scenarios()
