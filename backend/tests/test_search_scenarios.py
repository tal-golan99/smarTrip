"""
=============================================================================
QA TEST SUITE: 200+ Search Scenarios
=============================================================================
Author: Senior QA Engineer
Purpose: Comprehensive testing of search/recommendation scenarios covering
         all combinations of filters, edge cases, and real-world usage patterns.
=============================================================================
"""

import requests
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Tuple
from itertools import product
import sys

# Configuration
BASE_URL = "http://localhost:5000"
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

class ScenarioResult:
    def __init__(self, scenario_id: int, name: str, payload: Dict, 
                 status_code: int, success: bool, count: int, 
                 primary_count: int, relaxed_count: int,
                 top_score: int, duration: float, notes: str = ""):
        self.scenario_id = scenario_id
        self.name = name
        self.payload = payload
        self.status_code = status_code
        self.success = success
        self.count = count
        self.primary_count = primary_count
        self.relaxed_count = relaxed_count
        self.top_score = top_score
        self.duration = duration
        self.notes = notes

class SearchScenarioTester:
    """Test 200+ search scenarios"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results: List[ScenarioResult] = []
        self.scenarios: List[Dict] = []
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
    
    def generate_scenarios(self):
        """Generate 200+ test scenarios"""
        self.log("\n[GENERATING SCENARIOS]", Colors.CYAN)
        scenarios = []
        scenario_id = 1
        
        countries = self.metadata.get('countries', list(range(1, 50)))[:50]
        types = self.metadata.get('types', list(range(1, 11)))
        tags = self.metadata.get('tags', list(range(1, 15)))
        continents = self.metadata.get('continents', ['Africa', 'Asia', 'Europe'])
        
        # =====================================================================
        # CATEGORY 1: Single Filter Tests (20 scenarios)
        # =====================================================================
        self.log("  Category 1: Single Filter Tests", Colors.BLUE)
        
        # Budget only variations
        for budget in [1000, 3000, 5000, 7500, 10000, 15000, 20000, 50000]:
            scenarios.append({
                'id': scenario_id,
                'name': f"Budget only: ${budget}",
                'payload': {'budget': budget}
            })
            scenario_id += 1
        
        # Duration only
        for min_d, max_d in [(3, 7), (5, 10), (7, 14), (10, 20), (14, 30)]:
            scenarios.append({
                'id': scenario_id,
                'name': f"Duration only: {min_d}-{max_d} days",
                'payload': {'min_duration': min_d, 'max_duration': max_d}
            })
            scenario_id += 1
        
        # Type only
        for type_id in types[:5]:
            scenarios.append({
                'id': scenario_id,
                'name': f"Type only: {type_id}",
                'payload': {'preferred_type_id': type_id}
            })
            scenario_id += 1
        
        # Difficulty only
        for diff in [1, 2, 3, 4, 5]:
            scenarios.append({
                'id': scenario_id,
                'name': f"Difficulty only: {diff}",
                'payload': {'difficulty': diff}
            })
            scenario_id += 1
        
        # =====================================================================
        # CATEGORY 2: Country/Continent Tests (30 scenarios)
        # =====================================================================
        self.log("  Category 2: Geography Tests", Colors.BLUE)
        
        # Single country
        for country_id in countries[:15]:
            scenarios.append({
                'id': scenario_id,
                'name': f"Single country: {country_id}",
                'payload': {'selected_countries': [country_id], 'budget': 20000}
            })
            scenario_id += 1
        
        # Multiple countries
        for i in range(5):
            selected = random.sample(countries, min(3, len(countries)))
            scenarios.append({
                'id': scenario_id,
                'name': f"Multiple countries: {selected}",
                'payload': {'selected_countries': selected, 'budget': 20000}
            })
            scenario_id += 1
        
        # Single continent
        for continent in continents[:6]:
            scenarios.append({
                'id': scenario_id,
                'name': f"Continent: {continent}",
                'payload': {'selected_continents': [continent], 'budget': 20000}
            })
            scenario_id += 1
        
        # Multiple continents
        for i in range(4):
            selected = random.sample(continents, min(2, len(continents)))
            scenarios.append({
                'id': scenario_id,
                'name': f"Multi-continent: {selected}",
                'payload': {'selected_continents': selected, 'budget': 20000}
            })
            scenario_id += 1
        
        # =====================================================================
        # CATEGORY 3: Date Filter Tests (25 scenarios)
        # =====================================================================
        self.log("  Category 3: Date Filter Tests", Colors.BLUE)
        
        # Year only
        for year in ['2025', '2026', '2027']:
            scenarios.append({
                'id': scenario_id,
                'name': f"Year: {year}",
                'payload': {'year': year, 'budget': 15000}
            })
            scenario_id += 1
        
        # Year + Month combinations
        for year in ['2025', '2026']:
            for month in ['1', '3', '6', '9', '12']:
                scenarios.append({
                    'id': scenario_id,
                    'name': f"Date: {year}-{month}",
                    'payload': {'year': year, 'month': month, 'budget': 15000}
                })
                scenario_id += 1
        
        # Edge case dates
        scenarios.append({
            'id': scenario_id,
            'name': "Past year: 2020",
            'payload': {'year': '2020', 'budget': 15000}
        })
        scenario_id += 1
        
        scenarios.append({
            'id': scenario_id,
            'name': "Far future: 2030",
            'payload': {'year': '2030', 'budget': 15000}
        })
        scenario_id += 1
        
        scenarios.append({
            'id': scenario_id,
            'name': "Year all",
            'payload': {'year': 'all', 'budget': 15000}
        })
        scenario_id += 1
        
        # =====================================================================
        # CATEGORY 4: Combined Filters (40 scenarios)
        # =====================================================================
        self.log("  Category 4: Combined Filters", Colors.BLUE)
        
        # Budget + Duration
        for budget in [3000, 5000, 10000, 20000]:
            for min_d, max_d in [(5, 10), (7, 14), (10, 21)]:
                scenarios.append({
                    'id': scenario_id,
                    'name': f"Budget ${budget} + Duration {min_d}-{max_d}d",
                    'payload': {'budget': budget, 'min_duration': min_d, 'max_duration': max_d}
                })
                scenario_id += 1
        
        # Country + Type
        for country_id in countries[:5]:
            for type_id in types[:3]:
                scenarios.append({
                    'id': scenario_id,
                    'name': f"Country {country_id} + Type {type_id}",
                    'payload': {'selected_countries': [country_id], 'preferred_type_id': type_id, 'budget': 20000}
                })
                scenario_id += 1
        
        # Type + Budget + Duration
        for type_id in types[:4]:
            scenarios.append({
                'id': scenario_id,
                'name': f"Type {type_id} + Budget + Duration",
                'payload': {
                    'preferred_type_id': type_id,
                    'budget': 8000,
                    'min_duration': 7,
                    'max_duration': 14
                }
            })
            scenario_id += 1
        
        # =====================================================================
        # CATEGORY 5: Theme/Tag Tests (20 scenarios)
        # =====================================================================
        self.log("  Category 5: Theme Tests", Colors.BLUE)
        
        # Single theme
        for tag_id in tags[:10]:
            scenarios.append({
                'id': scenario_id,
                'name': f"Theme: {tag_id}",
                'payload': {'preferred_theme_ids': [tag_id], 'budget': 15000}
            })
            scenario_id += 1
        
        # Multiple themes
        for i in range(5):
            selected = random.sample(tags, min(3, len(tags)))
            scenarios.append({
                'id': scenario_id,
                'name': f"Multi-theme: {selected}",
                'payload': {'preferred_theme_ids': selected, 'budget': 15000}
            })
            scenario_id += 1
        
        # Theme + Country
        for i in range(5):
            scenarios.append({
                'id': scenario_id,
                'name': f"Theme + Country combo {i+1}",
                'payload': {
                    'preferred_theme_ids': [random.choice(tags)],
                    'selected_countries': [random.choice(countries)],
                    'budget': 15000
                }
            })
            scenario_id += 1
        
        # =====================================================================
        # CATEGORY 6: Complex Multi-Filter Scenarios (25 scenarios)
        # =====================================================================
        self.log("  Category 6: Complex Multi-Filter", Colors.BLUE)
        
        for i in range(25):
            payload = {'budget': random.choice([3000, 5000, 8000, 10000, 15000])}
            
            # Randomly add filters
            if random.random() > 0.5:
                payload['selected_countries'] = random.sample(countries, random.randint(1, 3))
            if random.random() > 0.5:
                payload['preferred_type_id'] = random.choice(types)
            if random.random() > 0.5:
                payload['min_duration'] = random.randint(3, 10)
                payload['max_duration'] = payload['min_duration'] + random.randint(5, 15)
            if random.random() > 0.5:
                payload['difficulty'] = random.randint(1, 5)
            if random.random() > 0.5:
                payload['preferred_theme_ids'] = random.sample(tags, random.randint(1, 3))
            if random.random() > 0.3:
                payload['year'] = random.choice(['2025', '2026'])
                if random.random() > 0.5:
                    payload['month'] = str(random.randint(1, 12))
            
            scenarios.append({
                'id': scenario_id,
                'name': f"Complex scenario {i+1}",
                'payload': payload
            })
            scenario_id += 1
        
        # =====================================================================
        # CATEGORY 7: Boundary/Edge Cases (30 scenarios)
        # =====================================================================
        self.log("  Category 7: Boundary Cases", Colors.BLUE)
        
        # Extreme values
        extreme_cases = [
            {'name': "Min budget $100", 'payload': {'budget': 100}},
            {'name': "Max budget $1M", 'payload': {'budget': 1000000}},
            {'name': "Zero budget", 'payload': {'budget': 0}},
            {'name': "Min duration 1 day", 'payload': {'min_duration': 1, 'max_duration': 3}},
            {'name': "Max duration 365 days", 'payload': {'min_duration': 300, 'max_duration': 365}},
            {'name': "Duration 0-0", 'payload': {'min_duration': 0, 'max_duration': 0}},
            {'name': "Duration 1-1", 'payload': {'min_duration': 1, 'max_duration': 1}},
            {'name': "Inverted duration", 'payload': {'min_duration': 20, 'max_duration': 5}},
            {'name': "All countries", 'payload': {'selected_countries': countries[:30]}},
            {'name': "All types (first)", 'payload': {'preferred_type_id': types[0] if types else 1}},
            {'name': "All themes", 'payload': {'preferred_theme_ids': tags}},
            {'name': "Difficulty 0", 'payload': {'difficulty': 0}},
            {'name': "Difficulty 10", 'payload': {'difficulty': 10}},
            {'name': "Empty countries array", 'payload': {'selected_countries': []}},
            {'name': "Empty themes array", 'payload': {'preferred_theme_ids': []}},
            {'name': "Invalid country ID", 'payload': {'selected_countries': [999999]}},
            {'name': "Negative country ID", 'payload': {'selected_countries': [-1]}},
            {'name': "Float budget", 'payload': {'budget': 5000.50}},
            {'name': "String budget", 'payload': {'budget': "5000"}},
            {'name': "Month without year", 'payload': {'month': '6', 'budget': 10000}},
            {'name': "Month 0", 'payload': {'year': '2025', 'month': '0'}},
            {'name': "Month 13", 'payload': {'year': '2025', 'month': '13'}},
            {'name': "Null values", 'payload': {'budget': None, 'min_duration': None}},
            {'name': "Mixed valid/invalid countries", 'payload': {'selected_countries': [1, 999999, 2]}},
            {'name': "Decimal difficulty", 'payload': {'difficulty': 2.5}},
            {'name': "Negative budget", 'payload': {'budget': -5000}},
            {'name': "Very long duration", 'payload': {'min_duration': 1, 'max_duration': 10000}},
            {'name': "Unicode in continent", 'payload': {'selected_continents': ['']}},
            {'name': "Special chars", 'payload': {'selected_continents': ["<script>alert(1)</script>"]}},
            {'name': "SQL injection attempt", 'payload': {'selected_continents': ["'; DROP TABLE trips;--"]}},
        ]
        
        for case in extreme_cases:
            case['id'] = scenario_id
            scenarios.append(case)
            scenario_id += 1
        
        # =====================================================================
        # CATEGORY 8: Real-World User Scenarios (30 scenarios)
        # =====================================================================
        self.log("  Category 8: Real-World Scenarios", Colors.BLUE)
        
        real_world = [
            {'name': "Budget traveler Europe", 'payload': {'selected_continents': ['Europe'], 'budget': 3000, 'min_duration': 5, 'max_duration': 10}},
            {'name': "Luxury Africa safari", 'payload': {'selected_continents': ['Africa'], 'budget': 25000, 'min_duration': 10, 'max_duration': 21}},
            {'name': "Family trip Asia", 'payload': {'selected_continents': ['Asia'], 'budget': 8000, 'difficulty': 1, 'min_duration': 7, 'max_duration': 14}},
            {'name': "Adventure South America", 'payload': {'selected_continents': ['South America'], 'budget': 6000, 'difficulty': 4}},
            {'name': "Short weekend getaway", 'payload': {'budget': 2000, 'min_duration': 2, 'max_duration': 4}},
            {'name': "Long sabbatical trip", 'payload': {'budget': 15000, 'min_duration': 30, 'max_duration': 60}},
            {'name': "Honeymoon tropical", 'payload': {'budget': 12000, 'min_duration': 10, 'max_duration': 14}},
            {'name': "Solo backpacker", 'payload': {'budget': 2500, 'difficulty': 3, 'min_duration': 14, 'max_duration': 30}},
            {'name': "Senior easy trip", 'payload': {'budget': 7000, 'difficulty': 1, 'min_duration': 7, 'max_duration': 10}},
            {'name': "Summer 2025 vacation", 'payload': {'year': '2025', 'month': '7', 'budget': 8000}},
            {'name': "Winter 2025 escape", 'payload': {'year': '2025', 'month': '12', 'budget': 6000}},
            {'name': "Spring break 2026", 'payload': {'year': '2026', 'month': '3', 'budget': 4000, 'min_duration': 5, 'max_duration': 10}},
            {'name': "New Year 2026 trip", 'payload': {'year': '2025', 'month': '12', 'budget': 10000}},
            {'name': "Multi-country Europe tour", 'payload': {'selected_continents': ['Europe'], 'budget': 10000, 'min_duration': 14, 'max_duration': 21}},
            {'name': "Quick business + leisure", 'payload': {'budget': 5000, 'min_duration': 3, 'max_duration': 5}},
            {'name': "Photography expedition", 'payload': {'budget': 8000, 'min_duration': 10, 'max_duration': 18}},
            {'name': "Culinary tour", 'payload': {'budget': 6000, 'min_duration': 7, 'max_duration': 12}},
            {'name': "Historical sites tour", 'payload': {'selected_continents': ['Europe'], 'budget': 7000}},
            {'name': "Beach vacation", 'payload': {'budget': 4000, 'min_duration': 5, 'max_duration': 10}},
            {'name': "Mountain expedition", 'payload': {'difficulty': 4, 'budget': 5000}},
            {'name': "Wildlife safari", 'payload': {'selected_continents': ['Africa'], 'budget': 12000}},
            {'name': "Cultural immersion", 'payload': {'selected_continents': ['Asia'], 'budget': 5000, 'min_duration': 14, 'max_duration': 21}},
            {'name': "Luxury cruise alternative", 'payload': {'budget': 20000, 'min_duration': 7, 'max_duration': 14}},
            {'name': "Eco-tourism", 'payload': {'budget': 4000, 'difficulty': 2}},
            {'name': "Festival trip", 'payload': {'year': '2025', 'budget': 5000}},
            {'name': "Off-season travel", 'payload': {'year': '2025', 'month': '2', 'budget': 3000}},
            {'name': "Peak season luxury", 'payload': {'year': '2025', 'month': '8', 'budget': 15000}},
            {'name': "Gap year trip", 'payload': {'budget': 10000, 'min_duration': 60, 'max_duration': 90}},
            {'name': "Retirement celebration", 'payload': {'budget': 18000, 'difficulty': 1, 'min_duration': 14, 'max_duration': 21}},
            {'name': "Anniversary trip", 'payload': {'budget': 8000, 'min_duration': 5, 'max_duration': 10}},
        ]
        
        for case in real_world:
            case['id'] = scenario_id
            scenarios.append(case)
            scenario_id += 1
        
        # =====================================================================
        # CATEGORY 9: Relaxed Search Trigger Scenarios (10 scenarios)
        # =====================================================================
        self.log("  Category 9: Relaxed Search Triggers", Colors.BLUE)
        
        # Scenarios designed to trigger relaxed search (few/no primary results)
        relaxed_triggers = [
            {'name': "Rare country + type combo", 'payload': {'selected_countries': [1], 'preferred_type_id': 4, 'budget': 5000}},
            {'name': "Very restrictive all filters", 'payload': {'selected_countries': [1], 'preferred_type_id': 1, 'budget': 1000, 'difficulty': 5, 'min_duration': 3, 'max_duration': 5}},
            {'name': "Specific month + country", 'payload': {'selected_countries': [2], 'year': '2026', 'month': '2', 'budget': 10000}},
            {'name': "Low budget + long duration", 'payload': {'budget': 1500, 'min_duration': 20, 'max_duration': 30}},
            {'name': "High difficulty + luxury", 'payload': {'difficulty': 5, 'budget': 25000}},
            {'name': "Multiple rare themes", 'payload': {'preferred_theme_ids': [1, 5, 9], 'budget': 10000}},
            {'name': "Rare continent + type", 'payload': {'selected_continents': ['Antarctica'], 'preferred_type_id': 1}},
            {'name': "Very short + specific type", 'payload': {'preferred_type_id': 3, 'min_duration': 1, 'max_duration': 3}},
            {'name': "Far future + specific", 'payload': {'year': '2027', 'month': '11', 'selected_countries': [5]}},
            {'name': "Maximum restrictions", 'payload': {
                'selected_countries': [1],
                'preferred_type_id': 2,
                'preferred_theme_ids': [1],
                'difficulty': 3,
                'budget': 5000,
                'min_duration': 10,
                'max_duration': 12,
                'year': '2026',
                'month': '5'
            }},
        ]
        
        for case in relaxed_triggers:
            case['id'] = scenario_id
            scenarios.append(case)
            scenario_id += 1
        
        self.scenarios = scenarios
        self.log(f"\n  Total scenarios generated: {len(scenarios)}", Colors.GREEN)
    
    def run_scenario(self, scenario: Dict) -> ScenarioResult:
        """Run a single search scenario"""
        start = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/recommendations",
                json=scenario['payload'],
                timeout=TIMEOUT
            )
            duration = time.time() - start
            
            if response.status_code != 200:
                return ScenarioResult(
                    scenario['id'], scenario['name'], scenario['payload'],
                    response.status_code, False, 0, 0, 0, 0, duration,
                    f"HTTP {response.status_code}"
                )
            
            data = response.json()
            success = data.get('success', False)
            count = data.get('count', 0)
            primary_count = data.get('primary_count', count)
            relaxed_count = data.get('relaxed_count', 0)
            
            # Get top score
            top_score = 0
            if data.get('data') and len(data['data']) > 0:
                top_score = data['data'][0].get('match_score', 0)
            
            # Check for anomalies
            notes = []
            if count == 0:
                notes.append("No results")
            if top_score > 100 or top_score < 0:
                notes.append(f"Invalid score: {top_score}")
            if relaxed_count > 0:
                notes.append(f"Relaxed search triggered")
            if duration > 3.0:
                notes.append(f"Slow: {duration:.2f}s")
            
            return ScenarioResult(
                scenario['id'], scenario['name'], scenario['payload'],
                response.status_code, success, count, primary_count, relaxed_count,
                top_score, duration, "; ".join(notes)
            )
            
        except Exception as e:
            duration = time.time() - start
            return ScenarioResult(
                scenario['id'], scenario['name'], scenario['payload'],
                0, False, 0, 0, 0, 0, duration, f"Exception: {str(e)}"
            )
    
    def run_all_scenarios(self):
        """Run all search scenarios"""
        self.fetch_metadata()
        self.generate_scenarios()
        
        self.log("\n" + "="*70, Colors.CYAN)
        self.log("  RUNNING 200+ SEARCH SCENARIOS", Colors.BOLD)
        self.log("="*70, Colors.CYAN)
        
        total = len(self.scenarios)
        for i, scenario in enumerate(self.scenarios):
            result = self.run_scenario(scenario)
            self.results.append(result)
            
            # Progress indicator
            status = f"{Colors.GREEN}OK{Colors.END}" if result.success else f"{Colors.RED}FAIL{Colors.END}"
            progress = f"[{i+1}/{total}]"
            score_info = f"Score:{result.top_score}" if result.success else ""
            count_info = f"P:{result.primary_count}/R:{result.relaxed_count}" if result.success else ""
            
            print(f"  {progress} [{status}] {scenario['name'][:40]:40} | {count_info:15} | {score_info:10} | {result.duration:.2f}s")
            
            if result.notes and not result.success:
                print(f"          Notes: {result.notes}")
        
        self.print_report()
    
    def print_report(self):
        """Print comprehensive test report"""
        self.log("\n" + "="*70, Colors.CYAN)
        self.log("  COMPREHENSIVE TEST REPORT", Colors.BOLD)
        self.log("="*70, Colors.CYAN)
        
        # Overall Statistics
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)
        
        self.log(f"\n{Colors.BOLD}OVERALL STATISTICS:{Colors.END}")
        self.log(f"  Total Scenarios: {total}")
        self.log(f"  {Colors.GREEN}Passed: {passed}{Colors.END}")
        self.log(f"  {Colors.RED}Failed: {failed}{Colors.END}")
        self.log(f"  Pass Rate: {(passed/total*100):.1f}%")
        
        # Performance Statistics
        durations = [r.duration for r in self.results]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        slow_requests = sum(1 for d in durations if d > 2.0)
        
        self.log(f"\n{Colors.BOLD}PERFORMANCE:{Colors.END}")
        self.log(f"  Average Response Time: {avg_duration:.3f}s")
        self.log(f"  Fastest: {min_duration:.3f}s")
        self.log(f"  Slowest: {max_duration:.3f}s")
        self.log(f"  Slow Requests (>2s): {slow_requests}")
        
        # Score Distribution
        scores = [r.top_score for r in self.results if r.success and r.count > 0]
        if scores:
            avg_score = sum(scores) / len(scores)
            high_scores = sum(1 for s in scores if s >= 70)
            mid_scores = sum(1 for s in scores if 50 <= s < 70)
            low_scores = sum(1 for s in scores if s < 50)
            
            self.log(f"\n{Colors.BOLD}SCORE DISTRIBUTION:{Colors.END}")
            self.log(f"  Average Top Score: {avg_score:.1f}")
            self.log(f"  High (>=70): {high_scores} ({high_scores/len(scores)*100:.1f}%)")
            self.log(f"  Medium (50-69): {mid_scores} ({mid_scores/len(scores)*100:.1f}%)")
            self.log(f"  Low (<50): {low_scores} ({low_scores/len(scores)*100:.1f}%)")
        
        # Results Analysis
        no_results = sum(1 for r in self.results if r.success and r.count == 0)
        relaxed_triggered = sum(1 for r in self.results if r.relaxed_count > 0)
        full_results = sum(1 for r in self.results if r.count >= 10)
        
        self.log(f"\n{Colors.BOLD}RESULTS ANALYSIS:{Colors.END}")
        self.log(f"  Zero Results: {no_results}")
        self.log(f"  Relaxed Search Triggered: {relaxed_triggered}")
        self.log(f"  Full Results (10+): {full_results}")
        
        # Failed Scenarios
        if failed > 0:
            self.log(f"\n{Colors.RED}{Colors.BOLD}FAILED SCENARIOS:{Colors.END}")
            for r in self.results:
                if not r.success:
                    self.log(f"  [{r.scenario_id}] {r.name}: {r.notes}", Colors.YELLOW)
        
        # Anomalies
        anomalies = [r for r in self.results if r.notes and r.success]
        if anomalies:
            self.log(f"\n{Colors.YELLOW}{Colors.BOLD}ANOMALIES/NOTES:{Colors.END}")
            for r in anomalies[:20]:  # Limit to 20
                self.log(f"  [{r.scenario_id}] {r.name}: {r.notes}")
            if len(anomalies) > 20:
                self.log(f"  ... and {len(anomalies) - 20} more")
        
        # Recommendations
        self.log(f"\n{Colors.MAGENTA}{Colors.BOLD}RECOMMENDATIONS FOR IMPROVEMENT:{Colors.END}")
        
        recommendations = []
        
        if no_results > total * 0.1:
            recommendations.append("HIGH: Too many zero-result scenarios. Consider relaxing hard filters or improving relaxed search.")
        
        if slow_requests > total * 0.05:
            recommendations.append("MEDIUM: Multiple slow requests detected. Consider database query optimization.")
        
        if avg_score < 50:
            recommendations.append("MEDIUM: Average scores are low. Review base score and bonus weights.")
        
        if relaxed_triggered < no_results:
            recommendations.append("HIGH: Relaxed search should trigger more often to avoid zero results.")
        
        if failed > 0:
            recommendations.append(f"CRITICAL: {failed} scenarios failed. Fix error handling for edge cases.")
        
        if not recommendations:
            recommendations.append("All metrics look healthy! Continue monitoring.")
        
        for i, rec in enumerate(recommendations, 1):
            self.log(f"  {i}. {rec}")
        
        self.log("\n" + "="*70, Colors.CYAN)
        self.log("  END OF REPORT", Colors.BOLD)
        self.log("="*70 + "\n", Colors.CYAN)


if __name__ == "__main__":
    tester = SearchScenarioTester()
    tester.run_all_scenarios()

