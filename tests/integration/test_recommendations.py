"""
Test script for the Recommendation Engine
Run this to test the weighted scoring algorithm

NOTE: This is an integration test requiring a running API.
Run with: python -m pytest tests/integration/test_recommendations.py -v
Or directly: python tests/integration/test_recommendations.py
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta

# Add backend to path for imports if needed
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backend'))

# API endpoint
BASE_URL = os.environ.get('API_URL', 'http://localhost:5000')

def test_recommendation(test_name, preferences):
    """Test a recommendation request"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print(f"Preferences: {json.dumps(preferences, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/recommendations",
        json=preferences
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nSuccess: {data['success']}")
        print(f"Total Candidates: {data.get('total_candidates', 'N/A')}")
        print(f"Recommendations: {data['count']}")
        
        if data['data']:
            print(f"\nTop 3 Recommendations:")
            for i, trip in enumerate(data['data'][:3], 1):
                print(f"\n{i}. {trip['title']} ({trip['titleHe']})")
                print(f"   Score: {trip['match_score']}/100")
                print(f"   Country: {trip['country']['name']}")
                print(f"   Price: {trip['price']} ILS")
                print(f"   Dates: {trip['startDate']} to {trip['endDate']}")
                print(f"   Match Details: {', '.join(trip['match_details'])}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("="*60)
    print("SMARTTRIP RECOMMENDATION ENGINE TEST")
    print("="*60)
    
    # Get tags for testing (all tags are now theme tags after V2 migration)
    tags_response = requests.get(f"{BASE_URL}/api/tags")
    if tags_response.status_code == 200:
        tags_data = tags_response.json()
        theme_tags = tags_data['data']  # All tags are theme tags now
        
        print(f"\nAvailable THEME tags: {len(theme_tags)}")
        for tag in theme_tags[:5]:
            print(f"  - ID {tag['id']}: {tag['name']} ({tag['nameHe']})")
    
    # Get trip types for testing (these replaced TYPE tags)
    types_response = requests.get(f"{BASE_URL}/api/trip-types")
    if types_response.status_code == 200:
        types_data = types_response.json()
        print(f"\nAvailable TRIP TYPES: {types_data['count']}")
        for t in types_data['data'][:5]:
            print(f"  - ID {t['id']}: {t['name']} ({t['nameHe']})")
    
    # Get countries for testing
    countries_response = requests.get(f"{BASE_URL}/api/countries")
    if countries_response.status_code == 200:
        countries_data = countries_response.json()
        print(f"\nTotal countries: {countries_data['count']}")
    
    # Calculate dates
    today = datetime.now().date()
    next_month = today + timedelta(days=30)
    
    # Test 1: Complete preferences
    test_recommendation(
        "Complete Preferences - Asia Cultural Trip",
        {
            "selected_continents": ["Asia"],
            "preferred_type_id": 1,  # Geographic Depth
            "preferred_theme_ids": [3, 4],  # Cultural, Historical
            "min_duration": 10,
            "max_duration": 16,
            "budget": 10000,
            "difficulty": 2,
            "start_date": next_month.isoformat()
        }
    )
    
    # Test 2: Budget-focused
    test_recommendation(
        "Budget-Friendly European Trip",
        {
            "selected_continents": ["Europe"],
            "preferred_type_id": 9,  # Boutique Tours
            "preferred_theme_ids": [4, 5],  # Historical, Food & Wine
            "min_duration": 7,
            "max_duration": 10,
            "budget": 6000,
            "difficulty": 1,
            "start_date": next_month.isoformat()
        }
    )
    
    # Test 3: Adventure seeker
    test_recommendation(
        "Extreme Adventure - Mountain Trekking",
        {
            "preferred_type_id": 7,  # Nature Hiking
            "preferred_theme_ids": [1, 7],  # Extreme, Mountain
            "min_duration": 12,
            "max_duration": 20,
            "difficulty": 3,
            "start_date": next_month.isoformat()
        }
    )
    
    # Test 4: Minimal preferences
    test_recommendation(
        "Flexible Preferences - Any Trip",
        {
            "min_duration": 7,
            "max_duration": 14,
            "budget": 15000,
            "start_date": today.isoformat()
        }
    )
    
    print(f"\n{'='*60}")
    print("TESTS COMPLETED")
    print(f"{'='*60}\n")
