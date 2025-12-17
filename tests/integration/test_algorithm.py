"""
SmartTrip Recommendation Algorithm Validation Script
Tests the weighted scoring algorithm with 3 specific personas

NOTE: This is an integration test requiring a running API.
Run with: python -m pytest tests/integration/test_algorithm.py -v
Or directly: python tests/integration/test_algorithm.py
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add backend to path for imports if needed
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backend'))

# API Configuration
BASE_URL = os.environ.get('API_URL', 'http://localhost:5000')
TAGS_ENDPOINT = f"{BASE_URL}/api/tags"
RECOMMENDATIONS_ENDPOINT = f"{BASE_URL}/api/recommendations"


class TagCache:
    """Cache for dynamically fetched tag IDs"""
    def __init__(self):
        self.type_tags: Dict[str, int] = {}
        self.theme_tags: Dict[str, int] = {}
        self._load_tags()
    
    def _load_tags(self):
        """Fetch all tags from API and organize by category"""
        try:
            response = requests.get(TAGS_ENDPOINT)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('success'):
                raise Exception(f"API returned error: {data.get('error')}")
            
            tags = data.get('data', [])
            
            for tag in tags:
                tag_id = tag['id']
                tag_name = tag['name']
                # After V2 migration, all tags are theme tags
                # Type info is now in trip_types endpoint
                self.theme_tags[tag_name] = tag_id
            
            print(f"[OK] Loaded {len(self.theme_tags)} THEME tags (Type info now in trip_types)\n")
            
        except Exception as e:
            print(f"[ERROR] Error loading tags: {e}")
            raise
    
    def get_type_id(self, name: str) -> Optional[int]:
        """Get TYPE tag ID by name"""
        return self.type_tags.get(name)
    
    def get_theme_id(self, name: str) -> Optional[int]:
        """Get THEME tag ID by name"""
        return self.theme_tags.get(name)
    
    def get_theme_ids(self, names: List[str]) -> List[int]:
        """Get multiple THEME tag IDs by names"""
        return [self.theme_tags[name] for name in names if name in self.theme_tags]


class Persona:
    """Represents a test persona with specific preferences"""
    def __init__(self, name: str, description: str, preferences: dict):
        self.name = name
        self.description = description
        self.preferences = preferences
    
    def get_preferences(self, tag_cache: TagCache) -> dict:
        """Build preferences dict with actual tag IDs"""
        prefs = self.preferences.copy()
        
        # Convert TYPE tag name to ID
        if 'preferred_type_name' in prefs:
            type_name = prefs.pop('preferred_type_name')
            type_id = tag_cache.get_type_id(type_name)
            if type_id:
                prefs['preferred_type_id'] = type_id
            else:
                print(f"  [WARNING] TYPE tag '{type_name}' not found")
        
        # Convert THEME tag names to IDs
        if 'preferred_theme_names' in prefs:
            theme_names = prefs.pop('preferred_theme_names')
            theme_ids = tag_cache.get_theme_ids(theme_names)
            if theme_ids:
                prefs['preferred_theme_ids'] = theme_ids
            else:
                print(f"  [WARNING] No THEME tags found for {theme_names}")
        
        return prefs


def test_persona(persona: Persona, tag_cache: TagCache):
    """Test a single persona and display results"""
    
    print("=" * 80)
    print(f"TESTING PERSONA: {persona.name}")
    print("=" * 80)
    print(f"Description: {persona.description}\n")
    
    # Get preferences with resolved tag IDs
    preferences = persona.get_preferences(tag_cache)
    
    # Display input parameters
    print("INPUT PARAMETERS:")
    print("-" * 80)
    for key, value in preferences.items():
        if key == 'preferred_type_id':
            type_name = next((name for name, id in tag_cache.type_tags.items() if id == value), 'Unknown')
            print(f"  - Style (TYPE): {type_name} (ID: {value})")
        elif key == 'preferred_theme_ids':
            theme_names = [name for name, id in tag_cache.theme_tags.items() if id in value]
            print(f"  - Interests (THEME): {', '.join(theme_names)} (IDs: {value})")
        elif key == 'selected_continents':
            print(f"  - Continents: {', '.join(value)}")
        elif key == 'budget':
            print(f"  - Maximum Budget: {value:,} ILS")
        elif key == 'min_duration':
            print(f"  - Min Duration: {value} days")
        elif key == 'max_duration':
            print(f"  - Max Duration: {value} days")
        elif key == 'difficulty':
            difficulty_names = {1: 'Easy', 2: 'Moderate', 3: 'Hard'}
            print(f"  - Difficulty: {difficulty_names.get(value, value)}")
        elif key == 'start_date':
            print(f"  - Earliest Start: {value}")
    
    print()
    
    # Make API request
    try:
        response = requests.post(
            RECOMMENDATIONS_ENDPOINT,
            json=preferences,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        data = response.json()
        
        if not data.get('success'):
            print(f"[ERROR] API Error: {data.get('error')}\n")
            return
        
        recommendations = data.get('data', [])
        total_candidates = data.get('total_candidates', 0)
        
        print(f"RESULTS: {len(recommendations)} recommendations from {total_candidates} candidates")
        print("-" * 80)
        
        if not recommendations:
            print("  [WARNING] No trips match your criteria.\n")
            print("  Possible reasons:")
            print("    - No trips in selected geography")
            print("    - Budget too low for available trips")
            print("    - Date constraints too restrictive")
            print("    - All trips fully booked")
            return
        
        # Display top 5 recommendations
        print("\nTOP 5 RECOMMENDATIONS:\n")
        
        for i, trip in enumerate(recommendations[:5], 1):
            score = trip.get('match_score', 0)
            title = trip.get('title', 'Unknown')
            title_he = trip.get('titleHe', '')
            price = trip.get('price', 0)
            status = trip.get('status', 'Unknown')
            country = trip.get('country', {}).get('name', 'Unknown')
            start_date = trip.get('startDate', 'N/A')
            end_date = trip.get('endDate', 'N/A')
            spots = trip.get('spotsLeft', 0)
            capacity = trip.get('maxCapacity', 0)
            match_details = trip.get('match_details', [])
            
            # Calculate duration
            try:
                start = datetime.fromisoformat(start_date)
                end = datetime.fromisoformat(end_date)
                duration = (end - start).days
            except:
                duration = 0
            
            # Print rank header
            print(f"Rank #{i}: [Score: {score}/100] {title}")
            print(f"         {title_he}")
            print(f"         Country: {country} | Price: {price:,.0f} ILS | Status: {status}")
            print(f"         Duration: {duration} days | Available: {spots}/{capacity} spots")
            print(f"         Dates: {start_date} to {end_date}")
            
            # Print match details (WHY this score)
            if match_details:
                print(f"         Match Reasons: {', '.join(match_details)}")
            
            print()
        
        # Analyze top result
        if recommendations:
            top_trip = recommendations[0]
            print("ANALYSIS OF TOP RECOMMENDATION:")
            print("-" * 80)
            print(f"  Title: {top_trip['title']}")
            print(f"  Score: {top_trip['match_score']}/100")
            print(f"  \nScore Breakdown (inferred from match_details):")
            
            for detail in top_trip.get('match_details', []):
                # Map match details to point values
                points = 0
                if 'Perfect Style Match' in detail:
                    points = 25
                elif 'Perfect Difficulty' in detail:
                    points = 20
                elif 'Close Difficulty' in detail:
                    points = 10
                elif 'Excellent Theme Match' in detail:
                    points = 15
                elif 'Good Theme Match' in detail:
                    points = 7
                elif 'Ideal Duration' in detail:
                    points = 15
                elif 'Good Duration' in detail:
                    points = 10
                elif 'Within Budget' in detail:
                    points = 15
                elif 'Slightly Over Budget' in detail:
                    points = 10
                elif 'Guaranteed' in detail or 'Last Places' in detail:
                    points = 10
                elif 'Departing Soon' in detail:
                    points = 5
                
                if points > 0:
                    print(f"    - {detail}: +{points} pts")
                else:
                    print(f"    - {detail}")
        
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network Error: {e}\n")
    except Exception as e:
        print(f"[ERROR] Unexpected Error: {e}\n")


def main():
    """Main test execution"""
    
    print("\n" + "=" * 80)
    print("SMARTTRIP RECOMMENDATION ALGORITHM VALIDATION")
    print("=" * 80)
    print()
    
    # Check if API is accessible
    try:
        health_response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if health_response.status_code != 200:
            print(f"[ERROR] API is not responding properly at {BASE_URL}")
            print("  Please ensure Flask backend is running: python app.py")
            return
        print(f"[OK] API is accessible at {BASE_URL}\n")
    except:
        print(f"[ERROR] Cannot connect to API at {BASE_URL}")
        print("  Please ensure Flask backend is running: python app.py")
        return
    
    # Load tags dynamically
    print("Loading tag IDs from API...")
    try:
        tag_cache = TagCache()
    except Exception as e:
        print(f"[ERROR] Failed to load tags: {e}")
        return
    
    # Calculate start date (next month)
    next_month = datetime.now().date() + timedelta(days=30)
    start_date = next_month.isoformat()
    
    # Define test personas
    personas = [
        Persona(
            name="The Classic Africa Traveler",
            description="High budget safari enthusiast seeking authentic wildlife experiences",
            preferences={
                'selected_continents': ['Africa'],
                'preferred_type_name': 'African Safari',
                'preferred_theme_names': ['Wildlife', 'Photography'],
                'budget': 20000,
                'min_duration': 10,
                'max_duration': 14,
                'difficulty': 2,
                'start_date': start_date
            }
        ),
        
        Persona(
            name="The Young Backpacker",
            description="Budget-conscious adventurer seeking challenging mountain treks",
            preferences={
                'selected_continents': ['Asia'],
                'preferred_type_name': 'Nature Hiking',
                'preferred_theme_names': ['Mountain', 'Cultural'],
                'budget': 8000,
                'min_duration': 10,
                'max_duration': 18,
                'difficulty': 3,
                'start_date': start_date
            }
        ),
        
        Persona(
            name="The Mismatch Tester",
            description="Impossible request to test algorithm's handling of mismatched criteria",
            preferences={
                'selected_continents': ['Antarctica'],
                'preferred_type_name': 'Desert',  # Wrong TYPE for Antarctica!
                'preferred_theme_names': ['Desert'],  # Wrong THEME for Antarctica!
                'budget': 5000,  # Way too low for Antarctica
                'min_duration': 7,
                'max_duration': 10,
                'difficulty': 1,  # Antarctica trips are usually difficult
                'start_date': start_date
            }
        ),
    ]
    
    # Test each persona
    for persona in personas:
        test_persona(persona, tag_cache)
        print("\n")
    
    # Final summary
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print()
    print("[EXPECTED BEHAVIOR] for Each Persona:")
    print()
    print("  1. Africa Traveler:")
    print("     - Should score highest on trips with 'African Safari' TYPE tag")
    print("     - Should favor Wildlife/Photography THEME matches")
    print("     - High budget should not penalize expensive trips")
    print()
    print("  2. Young Backpacker:")
    print("     - Should score highest on 'Nature Hiking' TYPE in Asia")
    print("     - Should favor Mountain/Cultural THEME matches")
    print("     - Low budget should prioritize cheaper trips")
    print("     - Difficulty 3 should favor harder treks")
    print()
    print("  3. Mismatch Tester:")
    print("     - Should return few/no results due to impossible criteria")
    print("     - Low scores due to TYPE/THEME mismatch with Antarctica")
    print("     - Budget too low for typical Antarctica trips")
    print()
    print("=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
