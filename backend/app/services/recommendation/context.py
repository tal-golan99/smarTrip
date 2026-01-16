"""
Context and Preference Processing Functions
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Any

from app.core.database import db_session
from app.models.trip import TripType


def normalize_continents(continents_input: List[str]) -> List[str]:
    """
    Map continent names to database enum values.
    
    Database uses NORTH_AND_CENTRAL_AMERICA (not NORTH_AMERICA).
    """
    continent_mapping = {
        # Title Case inputs (from frontend)
        'Africa': 'AFRICA', 'Asia': 'ASIA', 'Europe': 'EUROPE',
        'North America': 'NORTH_AND_CENTRAL_AMERICA', 
        'North & Central America': 'NORTH_AND_CENTRAL_AMERICA',
        'South America': 'SOUTH_AMERICA', 'Oceania': 'OCEANIA', 'Antarctica': 'ANTARCTICA',
        # UPPERCASE inputs (from tests/direct API calls)
        'AFRICA': 'AFRICA', 'ASIA': 'ASIA', 'EUROPE': 'EUROPE',
        'NORTH_AMERICA': 'NORTH_AND_CENTRAL_AMERICA',
        'NORTH_AND_CENTRAL_AMERICA': 'NORTH_AND_CENTRAL_AMERICA',
        'SOUTH_AMERICA': 'SOUTH_AMERICA', 'OCEANIA': 'OCEANIA', 'ANTARCTICA': 'ANTARCTICA'
    }
    
    return [
        continent_mapping.get(c, c.upper().replace(' ', '_').replace('&', 'AND')) 
        for c in continents_input
    ]


def get_private_groups_type_id() -> Optional[int]:
    """Get the ID of the 'Private Groups' trip type."""
    private_groups_type = db_session.query(TripType).filter(TripType.name == 'Private Groups').first()
    return private_groups_type.id if private_groups_type else 10


def parse_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and parse all preferences from the input dict.
    
    Handles defaults, type conversions, and date parsing.
    
    Args:
        preferences: Raw preferences dict from API request
    
    Returns:
        Dict with all preference values extracted and parsed:
        - selected_countries: List[int]
        - selected_continents: List[str] (raw, not normalized)
        - preferred_type_id: Optional[int]
        - preferred_theme_ids: List[int]
        - min_duration: int (default 1)
        - max_duration: int (default 365)
        - budget: Optional[float]
        - difficulty: Optional[int]
        - year: Optional[str]
        - month: Optional[str]
        - start_date: Optional[str] (legacy support)
        - user_start_date: Optional[date] (parsed from start_date)
    """
    parsed = {
        'selected_countries': preferences.get('selected_countries', []) or [],
        'selected_continents': preferences.get('selected_continents', []) or [],
        'preferred_type_id': preferences.get('preferred_type_id'),
        'preferred_theme_ids': preferences.get('preferred_theme_ids', []) or [],
        'min_duration': preferences.get('min_duration', 1) or 1,
        'max_duration': preferences.get('max_duration', 365) or 365,
        'budget': preferences.get('budget'),
        'difficulty': preferences.get('difficulty'),
        'year': preferences.get('year'),
        'month': preferences.get('month'),
        'start_date': preferences.get('start_date'),  # Legacy support
    }
    
    # Parse start date safely (legacy support)
    user_start_date = None
    if parsed['start_date']:
        try:
            user_start_date = datetime.fromisoformat(parsed['start_date']).date()
        except (ValueError, TypeError):
            user_start_date = None
    parsed['user_start_date'] = user_start_date
    
    return parsed


def normalize_preferences(parsed_preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize preference values (continents, dates, etc.).
    
    Args:
        parsed_preferences: Dict from parse_preferences()
    
    Returns:
        Dict with normalized values:
        - selected_continents_enum: List[str] (normalized continent enum values)
        - All other fields from parsed_preferences
    """
    normalized = parsed_preferences.copy()
    
    # Normalize continents
    selected_continents_input = normalized.get('selected_continents', []) or []
    normalized['selected_continents_enum'] = normalize_continents(selected_continents_input)
    
    return normalized


def determine_search_context(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine runtime context information needed for the search algorithm.
    
    This function extracts metadata that affects how the search behaves:
    - Gets the current date (for filtering future trips, calculating "departing soon" bonuses)
    - Gets the Private Groups trip type ID from the database
    - Determines if the user is searching for Private Groups trips (which have different
      date filtering rules - they don't require specific start dates)
    
    Args:
        preferences: Normalized preferences dict (needs 'preferred_type_id')
    
    Returns:
        Dict with:
        - today: date - Current date for filtering and scoring
        - private_groups_id: int - Database ID of "Private Groups" trip type
        - is_private_groups: bool - True if user is searching for Private Groups trips
    """
    today = datetime.now().date()
    private_groups_id = get_private_groups_type_id()
    preferred_type_id = preferences.get('preferred_type_id')
    is_private_groups = (preferred_type_id == private_groups_id)
    
    return {
        'today': today,
        'private_groups_id': private_groups_id,
        'is_private_groups': is_private_groups
    }
