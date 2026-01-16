"""
Recommendation Service
=====================

Business logic for trip recommendations and scoring algorithm.
Extracted from routes.py for better separation of concerns.

This module contains:
- RecommendationConfig: Configuration class for filtering and scoring
- SCORING_WEIGHTS: Point values for different match criteria
- SCORE_THRESHOLDS: Thresholds for color coding results
- Query building functions for filtering trips
- Scoring functions for calculating match scores
- Relaxed search functions for expanded results
- Main orchestration function: get_recommendations()
"""

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_, extract
from sqlalchemy.orm import joinedload, selectinload
from typing import Dict, List, Optional, Tuple, Any
import heapq

from app.core.database import db_session
from app.models.trip import (
    TripOccurrence, TripTemplate, TripTemplateTag, TripTemplateCountry, Country, TripType
)

# Scoring weights dictionary (all float values)
# Raw point accumulation - max possible = 100
SCORING_WEIGHTS = {
    # Base score for passing hard filters
    'BASE_SCORE': 25.0,           # All trips that pass filters start here
    'RELAXED_PENALTY': -20.0,     # Penalty for relaxed/expanded results
    
    # Theme matching (user selected theme interests)
    'THEME_FULL': 25.0,           # Multiple theme matches (2+ themes)
    'THEME_PARTIAL': 12.0,        # Single theme match
    'THEME_PENALTY': -15.0,       # PENALTY: Trip has NONE of user's selected themes
    
    # Difficulty matching (user selected difficulty preference)
    'DIFFICULTY_PERFECT': 15.0,   # Exact difficulty match
    
    # Duration matching (user specified duration range)
    'DURATION_IDEAL': 12.0,       # Within specified range
    'DURATION_GOOD': 8.0,         # Within 4 days of range
    
    # Budget matching (user specified budget)
    'BUDGET_PERFECT': 12.0,       # Within budget
    'BUDGET_GOOD': 8.0,           # Within 110% of budget
    'BUDGET_ACCEPTABLE': 5.0,     # Within 120% of budget
    
    # Urgency/Status bonuses (always active - business priority)
    'STATUS_GUARANTEED': 7.0,     # Guaranteed departure bonus
    'STATUS_LAST_PLACES': 15.0,   # Last places urgency bonus
    'DEPARTING_SOON': 7.0,        # Departing within 30 days
    
    # Geography bonuses (always active when locations selected)
    'GEO_DIRECT_COUNTRY': 15.0,   # Direct country match bonus
    'GEO_CONTINENT': 5.0,         # Continent match bonus
}

# Score thresholds for color coding (used by frontend)
SCORE_THRESHOLDS = {
    'HIGH': 70,    # >= 70 = Turquoise (excellent match)
    'MID': 50,     # >= 50 = Orange (medium match)
    # < 50 = Red (low match)
}


class RecommendationConfig:
    """Configuration for the recommendation scoring algorithm
    
    Note: Trip Type is now a HARD FILTER (not scored).
    Only Theme tags are used for soft scoring.
    """
    
    # Filtering thresholds (not scoring - these are for hard filters)
    DIFFICULTY_TOLERANCE = 1        # Allow +/-1 difficulty level
    BUDGET_MAX_MULTIPLIER = 1.3     # Allow up to 30% over budget
    DURATION_GOOD_DAYS = 4          # "Good" duration within +/-4 days
    DURATION_HARD_FILTER_DAYS = 7   # HARD FILTER: Skip trips outside +/-7 days
    DEPARTING_SOON_DAYS = 30        # Bonus for trips in next 30 days
    
    # Relaxed filtering thresholds (for expanded results)
    RELAXED_DIFFICULTY_TOLERANCE = 2    # Allow +/-2 difficulty levels
    RELAXED_BUDGET_MULTIPLIER = 1.5     # Allow up to 50% over budget
    RELAXED_DURATION_DAYS = 10          # Allow +/-10 days from range
    
    # Result limits
    MAX_RESULTS = 10                # Return top 10 recommendations
    MIN_RESULTS_THRESHOLD = 5       # If results <= this, add relaxed results
    MAX_CANDIDATES_TO_SCORE = 30   # Use min-heap to keep only top 30 during scoring
    THEME_MATCH_THRESHOLD = 2       # Need 2+ themes for full points
    
    # Filtering parameters
    MIN_SCORE_THRESHOLD = 30        # Don't show results with score less than this
    MAX_YEARS_AHEAD = 1             # Show trips for current year + next N years only (1 = current + next year)
    
    # Frontend "Show More" parameters
    SHOW_MORE_INCREMENT = 10        # Number of additional results to show per "show more" click
    MAX_SHOW_MORE_CLICKS = 1        # Maximum number of times "show more" can be clicked


# ============================================
# HELPER FUNCTIONS
# ============================================

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


def build_base_query():
    """
    Build base SQLAlchemy query with optimized eager loading.
    
    Uses joinedload for many-to-one relationships and selectinload
    for one-to-many to avoid cartesian products.
    """
    return db_session.query(TripOccurrence).options(
        joinedload(TripOccurrence.template).joinedload(TripTemplate.company),
        joinedload(TripOccurrence.template).joinedload(TripTemplate.trip_type),
        joinedload(TripOccurrence.template).joinedload(TripTemplate.primary_country),
        joinedload(TripOccurrence.template).selectinload(TripTemplate.template_tags).joinedload(TripTemplateTag.tag),
        joinedload(TripOccurrence.template).selectinload(TripTemplate.template_countries).joinedload(TripTemplateCountry.country),
        joinedload(TripOccurrence.guide),
    ).join(TripTemplate).filter(TripTemplate.is_active == True)


# ============================================
# FILTERING FUNCTIONS
# ============================================

def apply_geographic_filters(
    query,
    selected_countries: List[int],
    selected_continents_enum: List[str]
):
    """Apply geographic filters (countries and continents)."""
    if not selected_countries and not selected_continents_enum:
        return query
    
    geo_filters = []
    
    if selected_countries:
        geo_filters.append(TripTemplate.primary_country_id.in_(selected_countries))
    
    if selected_continents_enum:
        query = query.join(Country, TripTemplate.primary_country_id == Country.id)
        geo_filters.append(Country.continent.in_(selected_continents_enum))
    
    if len(geo_filters) > 1:
        query = query.filter(or_(*geo_filters))
    elif geo_filters:
        query = query.filter(geo_filters[0])
    
    return query


def apply_date_filters(
    query,
    today: date,
    is_private_groups: bool,
    selected_year: Optional[str],
    selected_month: Optional[str],
    user_start_date: Optional[date],
    config: type
):
    """Apply date filters (year, month, start_date)."""
    if is_private_groups:
        return query
    
    query = query.filter(TripOccurrence.start_date >= today)
    
    # Limit to current year + next N years only (default: current + next year)
    current_year = today.year
    max_year = current_year + config.MAX_YEARS_AHEAD
    query = query.filter(extract('year', TripOccurrence.start_date) <= max_year)
    print(f"[Recommendation] Applied year filter: <= {max_year} (current year + {config.MAX_YEARS_AHEAD})", flush=True)
    
    if selected_year and selected_year != 'all':
        query = query.filter(extract('year', TripOccurrence.start_date) == int(selected_year))
        if selected_month and selected_month != 'all':
            query = query.filter(extract('month', TripOccurrence.start_date) == int(selected_month))
    
    # Legacy: If user specified a start date preference (old format)
    if user_start_date and user_start_date > today and not selected_year:
        query = query.filter(TripOccurrence.start_date >= user_start_date)
        print(f"[Recommendation] Applied user start date filter: >= {user_start_date}", flush=True)
    
    return query


def apply_status_filters(query, is_private_groups: bool):
    """Apply status filters (exclude Cancelled and Full trips)."""
    query = query.filter(TripOccurrence.status.notin_(['Cancelled', 'Full']))
    
    if not is_private_groups:
        query = query.filter(TripOccurrence.spots_left > 0)
    
    return query


def apply_difficulty_filter(query, difficulty: Optional[int], tolerance: int):
    """Apply difficulty filter with tolerance."""
    if difficulty is not None:
        query = query.filter(
            TripTemplate.difficulty_level.between(difficulty - tolerance, difficulty + tolerance)
        )
    return query


def apply_budget_filter(query, budget: Optional[float], multiplier: float):
    """Apply budget filter with multiplier."""
    if budget:
        max_price = budget * multiplier
        query = query.filter(TripOccurrence.effective_price <= max_price)
    return query


# ============================================
# SCORING FUNCTIONS
# ============================================

def calculate_trip_score(
    occurrence: TripOccurrence,
    preferences: Dict[str, Any],
    weights: Dict[str, float],
    config: type,
    today: date,
    private_groups_id: int,
    format_trip_func
) -> Optional[Dict[str, Any]]:
    """
    Calculate match score for a single trip occurrence.
    
    Returns formatted trip dict with score, or None if trip should be skipped.
    """
    template = occurrence.template
    current_score = weights['BASE_SCORE']
    match_details = []
    
    trip_is_private = (template.trip_type_id == private_groups_id)
    
    # Get theme tags
    trip_theme_tags = [
        tt.tag_id for tt in template.template_tags 
        if tt.tag
    ]
    
    preferred_theme_ids = preferences.get('preferred_theme_ids', []) or []
    difficulty = preferences.get('difficulty')
    min_duration = preferences.get('min_duration', 1) or 1
    max_duration = preferences.get('max_duration', 365) or 365
    budget = preferences.get('budget')
    selected_countries = preferences.get('selected_countries', []) or []
    selected_continents_enum = preferences.get('selected_continents_enum', []) or []
    
    # Theme scoring
    if preferred_theme_ids:
        theme_matches = len(set(trip_theme_tags) & set(preferred_theme_ids))
        if theme_matches >= config.THEME_MATCH_THRESHOLD:
            current_score += weights['THEME_FULL']
            match_details.append(f"Excellent Theme Match [+{weights['THEME_FULL']:.0f}]")
        elif theme_matches == 1:
            current_score += weights['THEME_PARTIAL']
            match_details.append(f"Good Theme Match [+{weights['THEME_PARTIAL']:.0f}]")
        else:
            current_score += weights['THEME_PENALTY']
            match_details.append(f"No Theme Match [{weights['THEME_PENALTY']:.0f}]")
    
    # Difficulty scoring
    if difficulty is not None and template.difficulty_level == difficulty:
        current_score += weights['DIFFICULTY_PERFECT']
        match_details.append(f"Perfect Difficulty [+{weights['DIFFICULTY_PERFECT']:.0f}]")
    
    # Duration scoring
    if trip_is_private:
        current_score += weights['DURATION_IDEAL']
        match_details.append(f"Flexible Duration [+{weights['DURATION_IDEAL']:.0f}]")
    else:
        trip_duration = occurrence.duration_days or 0
        if min_duration <= trip_duration <= max_duration:
            current_score += weights['DURATION_IDEAL']
            match_details.append(f"Ideal Duration ({trip_duration}d) [+{weights['DURATION_IDEAL']:.0f}]")
        elif abs(trip_duration - min_duration) <= config.DURATION_GOOD_DAYS or \
             abs(trip_duration - max_duration) <= config.DURATION_GOOD_DAYS:
            current_score += weights['DURATION_GOOD']
            match_details.append(f"Good Duration ({trip_duration}d) [+{weights['DURATION_GOOD']:.0f}]")
        elif abs(trip_duration - min_duration) > config.DURATION_HARD_FILTER_DAYS and \
             abs(trip_duration - max_duration) > config.DURATION_HARD_FILTER_DAYS:
            return None  # Skip - outside hard filter
    
    # Budget scoring
    if budget:
        trip_price = float(occurrence.effective_price or 0)
        if trip_price <= budget:
            current_score += weights['BUDGET_PERFECT']
            match_details.append(f"Within Budget [+{weights['BUDGET_PERFECT']:.0f}]")
        elif trip_price <= budget * 1.1:
            current_score += weights['BUDGET_GOOD']
            match_details.append(f"Slightly Over (+10%) [+{weights['BUDGET_GOOD']:.0f}]")
        elif trip_price <= budget * 1.2:
            current_score += weights['BUDGET_ACCEPTABLE']
            match_details.append(f"Over Budget (+20%) [+{weights['BUDGET_ACCEPTABLE']:.0f}]")
    
    # Status scoring
    if occurrence.status == 'Guaranteed':
        current_score += weights['STATUS_GUARANTEED']
        match_details.append(f"Guaranteed [+{weights['STATUS_GUARANTEED']:.0f}]")
    elif occurrence.status == 'Last Places':
        current_score += weights['STATUS_LAST_PLACES']
        match_details.append(f"Last Places [+{weights['STATUS_LAST_PLACES']:.0f}]")
    
    # Departing soon
    if not trip_is_private and occurrence.start_date:
        days_until = (occurrence.start_date - today).days
        if days_until <= config.DEPARTING_SOON_DAYS:
            current_score += weights['DEPARTING_SOON']
            match_details.append(f"Soon ({days_until}d) [+{weights['DEPARTING_SOON']:.0f}]")
    
    # Geography scoring (with Antarctica special case)
    if selected_countries or selected_continents_enum:
        is_direct = selected_countries and template.primary_country_id in selected_countries
        is_continent = (
            selected_continents_enum and 
            template.primary_country and 
            template.primary_country.continent.name in selected_continents_enum
        )
        
        # Special case: Antarctica continent selection = direct country match
        is_antarctica_match = (
            selected_continents_enum and 'ANTARCTICA' in selected_continents_enum and
            template.primary_country and template.primary_country.name == 'Antarctica'
        )
        
        if is_direct or is_antarctica_match:
            current_score += weights['GEO_DIRECT_COUNTRY']
            match_details.append(f"Country Match [+{weights['GEO_DIRECT_COUNTRY']:.0f}]")
        elif is_continent:
            current_score += weights['GEO_CONTINENT']
            match_details.append(f"Continent Match [+{weights['GEO_CONTINENT']:.0f}]")
    
    # Final score (clamped 0-100)
    final_score = max(0.0, min(100.0, current_score))
    
    # Format trip data
    trip_dict = format_trip_func(occurrence, include_relations=True)
    trip_dict['_float_score'] = final_score
    trip_dict['match_score'] = int(round(final_score))
    trip_dict['match_details'] = match_details
    trip_dict['_sort_date'] = occurrence.start_date.isoformat() if occurrence.start_date else '2099-12-31'
    trip_dict['is_relaxed'] = False
    
    return trip_dict


def calculate_relaxed_trip_score(
    occurrence: TripOccurrence,
    preferences: Dict[str, Any],
    weights: Dict[str, float],
    config: type,
    today: date,
    private_groups_id: int,
    format_trip_func
) -> Optional[Dict[str, Any]]:
    """
    Calculate match score for a relaxed/expanded trip occurrence.
    
    Similar to calculate_trip_score but with relaxed penalties and different trip type handling.
    """
    template = occurrence.template
    current_score = weights['BASE_SCORE'] + weights.get('RELAXED_PENALTY', -20.0)
    match_details = ["Expanded Result [-20]"]
    
    trip_is_private = (template.trip_type_id == private_groups_id)
    
    # Get theme tags
    trip_theme_tags = []
    try:
        trip_theme_tags = [tt.tag_id for tt in template.template_tags if tt.tag]
    except:
        pass
    
    preferred_theme_ids = preferences.get('preferred_theme_ids', []) or []
    preferred_type_id = preferences.get('preferred_type_id')
    difficulty = preferences.get('difficulty')
    min_duration = preferences.get('min_duration', 1) or 1
    max_duration = preferences.get('max_duration', 365) or 365
    budget = preferences.get('budget')
    selected_countries = preferences.get('selected_countries', []) or []
    selected_continents_enum = preferences.get('selected_continents_enum', []) or []
    RELAXED_DURATION_DAYS = 10
    
    # Theme scoring
    if preferred_theme_ids:
        theme_matches = len(set(trip_theme_tags) & set(preferred_theme_ids))
        if theme_matches >= config.THEME_MATCH_THRESHOLD:
            current_score += weights['THEME_FULL']
            match_details.append(f"Theme Match [+{weights['THEME_FULL']:.0f}]")
        elif theme_matches == 1:
            current_score += weights['THEME_PARTIAL']
            match_details.append(f"Theme Match [+{weights['THEME_PARTIAL']:.0f}]")
        else:
            current_score += weights['THEME_PENALTY']
    
    # Trip type penalty (for relaxed search)
    if preferred_type_id and template.trip_type_id != preferred_type_id:
        current_score -= 10.0
        match_details.append("Different Type [-10]")
    
    # Difficulty scoring
    if difficulty is not None and template.difficulty_level == difficulty:
        current_score += weights['DIFFICULTY_PERFECT']
        match_details.append(f"Perfect Difficulty [+{weights['DIFFICULTY_PERFECT']:.0f}]")
    
    # Duration scoring (relaxed tolerance)
    if trip_is_private:
        current_score += weights['DURATION_IDEAL']
    else:
        trip_duration = occurrence.duration_days or 0
        if min_duration <= trip_duration <= max_duration:
            current_score += weights['DURATION_IDEAL']
            match_details.append(f"Ideal Duration [+{weights['DURATION_IDEAL']:.0f}]")
        elif abs(trip_duration - min_duration) <= RELAXED_DURATION_DAYS or \
             abs(trip_duration - max_duration) <= RELAXED_DURATION_DAYS:
            current_score += weights['DURATION_GOOD']
            match_details.append(f"Good Duration [+{weights['DURATION_GOOD']:.0f}]")
    
    # Budget scoring
    if budget:
        trip_price = float(occurrence.effective_price or 0)
        if trip_price <= budget:
            current_score += weights['BUDGET_PERFECT']
            match_details.append(f"Within Budget [+{weights['BUDGET_PERFECT']:.0f}]")
        elif trip_price <= budget * 1.1:
            current_score += weights['BUDGET_GOOD']
        elif trip_price <= budget * 1.2:
            current_score += weights['BUDGET_ACCEPTABLE']
    
    # Status bonuses
    if occurrence.status == 'Guaranteed':
        current_score += weights['STATUS_GUARANTEED']
        match_details.append(f"Guaranteed [+{weights['STATUS_GUARANTEED']:.0f}]")
    elif occurrence.status == 'Last Places':
        current_score += weights['STATUS_LAST_PLACES']
        match_details.append(f"Last Places [+{weights['STATUS_LAST_PLACES']:.0f}]")
    
    # Departing soon bonus
    if not trip_is_private and occurrence.start_date:
        days_until_departure = (occurrence.start_date - today).days
        if days_until_departure <= config.DEPARTING_SOON_DAYS:
            current_score += weights['DEPARTING_SOON']
            match_details.append(f"Soon ({days_until_departure}d) [+{weights['DEPARTING_SOON']:.0f}]")
    
    # Geography scoring (with Antarctica special case)
    if selected_countries or selected_continents_enum:
        is_direct_match = selected_countries and template.primary_country_id in selected_countries
        is_continent_match = (
            selected_continents_enum and template.primary_country and 
            template.primary_country.continent.name in selected_continents_enum
        )
        
        # Special case: Antarctica continent selection = direct country match
        is_antarctica_match = (
            selected_continents_enum and 'ANTARCTICA' in selected_continents_enum and
            template.primary_country and template.primary_country.name == 'Antarctica'
        )
        
        if is_direct_match or is_antarctica_match:
            current_score += weights['GEO_DIRECT_COUNTRY']
            match_details.append(f"Country Match [+{weights['GEO_DIRECT_COUNTRY']:.0f}]")
        elif is_continent_match:
            current_score += weights['GEO_CONTINENT']
            match_details.append(f"Continent Match [+{weights['GEO_CONTINENT']:.0f}]")
    
    # Final score (clamped 0-100)
    final_score = max(0.0, min(100.0, current_score))
    
    try:
        trip_dict = format_trip_func(occurrence, include_relations=True)
        trip_dict['_float_score'] = final_score
        trip_dict['match_score'] = int(round(final_score))
        trip_dict['match_details'] = match_details
        trip_dict['is_relaxed'] = True
        if occurrence.start_date:
            trip_dict['_sort_date'] = occurrence.start_date.isoformat()
        else:
            trip_dict['_sort_date'] = '2099-12-31'
        return trip_dict
    except Exception as e:
        print(f"[Recommendation] Serialization error for trip {occurrence.id}: {e}", flush=True)
        return None


def build_relaxed_query(
    today: date,
    is_private_groups: bool,
    selected_countries: List[int],
    selected_continents_enum: List[str],
    selected_year: Optional[str],
    selected_month: Optional[str],
    difficulty: Optional[int],
    budget: Optional[float],
    included_ids: set,
    config: type
):
    """
    Build relaxed search query with expanded filters.
    
    Relaxed search expands:
    - Geography: Same continent if specific countries selected
    - Trip type: No filter (all types allowed with penalty)
    - Date: 2 months before/after selected date
    - Difficulty: +/-2 levels instead of +/-1
    - Budget: 50% over instead of 30%
    """
    relaxed_query = build_base_query()
    
    # Status filter (same - no Full or Cancelled)
    if is_private_groups:
        relaxed_query = relaxed_query.filter(TripOccurrence.status.notin_(['Cancelled', 'Full']))
    else:
        relaxed_query = relaxed_query.filter(
            TripOccurrence.status.notin_(['Cancelled', 'Full']),
            TripOccurrence.spots_left > 0
        )
    
    # RELAXED GEOGRAPHY: Expand to same continent if user selected specific countries
    if selected_countries or selected_continents_enum:
        geo_filters = []
        
        if selected_countries:
            # Get continents of selected countries for expansion
            selected_country_objs = db_session.query(Country).filter(Country.id.in_(selected_countries)).all()
            expanded_continents = set()
            for c in selected_country_objs:
                if c.continent:
                    continent_enum_name = c.continent.name if hasattr(c.continent, 'name') else str(c.continent)
                    expanded_continents.add(continent_enum_name)
            
            # Join Country table for continent filtering
            relaxed_query = relaxed_query.join(Country, TripTemplate.primary_country_id == Country.id)
            
            # Include BOTH: original selected countries AND all countries from same continents
            country_filter = TripTemplate.primary_country_id.in_(selected_countries)
            if expanded_continents:
                continent_filter = Country.continent.in_(list(expanded_continents))
                geo_filters.append(or_(country_filter, continent_filter))
                print(f"[Recommendation RELAXED] Expanded geography: selected countries {selected_countries} OR continents {expanded_continents}", flush=True)
            else:
                geo_filters.append(country_filter)
        
        if selected_continents_enum:
            if not selected_countries:  # Only join if not already joined
                relaxed_query = relaxed_query.join(Country, TripTemplate.primary_country_id == Country.id)
            geo_filters.append(Country.continent.in_(selected_continents_enum))
        
        if len(geo_filters) > 1:
            relaxed_query = relaxed_query.filter(or_(*geo_filters))
        elif geo_filters:
            relaxed_query = relaxed_query.filter(geo_filters[0])
    
    # RELAXED: Do NOT filter by trip type (allow all types with penalty)
    print(f"[Recommendation RELAXED] Not filtering by trip type (will apply penalty for different types)", flush=True)
    
    # RELAXED DATE FILTER: Expand by 2 months before and after
    if not is_private_groups:
        relaxed_query = relaxed_query.filter(TripOccurrence.start_date >= today)
        
        # Limit to current year + next N years only (same as primary search)
        current_year = today.year
        max_year = current_year + config.MAX_YEARS_AHEAD
        relaxed_query = relaxed_query.filter(extract('year', TripOccurrence.start_date) <= max_year)
        print(f"[Recommendation RELAXED] Applied year filter: <= {max_year} (current year + {config.MAX_YEARS_AHEAD})", flush=True)
        
        if selected_year and selected_year != 'all':
            try:
                year_int = int(selected_year)
                
                if selected_month and selected_month != 'all':
                    # User selected specific month: expand by 2 months before and after
                    month_int = int(selected_month)
                    center_date = datetime(year_int, month_int, 1).date()
                    
                    # 2 months before
                    start_range = max(center_date - relativedelta(months=2), today)
                    # 2 months after (end of that month)
                    end_range = center_date + relativedelta(months=3) - timedelta(days=1)
                    
                    relaxed_query = relaxed_query.filter(
                        TripOccurrence.start_date.between(start_range, end_range)
                    )
                    print(f"[Recommendation RELAXED] Expanded date range: {start_range} to {end_range}", flush=True)
                else:
                    # User selected only year: expand by 2 months before and after the year
                    year_start = datetime(year_int, 1, 1).date()
                    year_end = datetime(year_int, 12, 31).date()
                    
                    start_range = max(year_start - relativedelta(months=2), today)
                    end_range = year_end + relativedelta(months=2)
                    
                    relaxed_query = relaxed_query.filter(
                        TripOccurrence.start_date.between(start_range, end_range)
                    )
                    print(f"[Recommendation RELAXED] Expanded year {year_int} to: {start_range} to {end_range}", flush=True)
            except (ValueError, TypeError):
                pass  # Fall back to just >= today
    
    # RELAXED: Difficulty (+/-2 levels instead of +/-1)
    if difficulty is not None:
        relaxed_query = apply_difficulty_filter(relaxed_query, difficulty, RecommendationConfig.RELAXED_DIFFICULTY_TOLERANCE)
        print(f"[Recommendation RELAXED] Difficulty filter: {difficulty} +/-{RecommendationConfig.RELAXED_DIFFICULTY_TOLERANCE}", flush=True)
    
    # RELAXED: Budget (50% over budget instead of 30%)
    if budget:
        relaxed_query = apply_budget_filter(relaxed_query, budget, RecommendationConfig.RELAXED_BUDGET_MULTIPLIER)
        print(f"[Recommendation RELAXED] Budget filter: max ${budget * RecommendationConfig.RELAXED_BUDGET_MULTIPLIER}", flush=True)
    
    # Exclude already included trips
    relaxed_query = relaxed_query.filter(~TripOccurrence.id.in_(included_ids))
    
    # Order by start_date
    relaxed_query = relaxed_query.order_by(TripOccurrence.start_date.asc())
    
    return relaxed_query


# ============================================
# PREFERENCE PROCESSING FUNCTIONS
# ============================================

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


# ============================================
# QUERY BUILDING FUNCTIONS
# ============================================

def build_primary_query(
    preferences: Dict[str, Any],
    context: Dict[str, Any],
    config: type
):
    """
    Build the primary filtered query based on preferences.
    
    Applies all filters in sequence:
    - Geographic filters (countries, continents)
    - Trip type filter
    - Date filters (year, month, start_date)
    - Status filters (exclude Cancelled, Full)
    - Difficulty filter
    - Budget filter
    
    Args:
        preferences: Normalized preferences dict
        context: Search context dict (from determine_search_context)
        config: RecommendationConfig class
    
    Returns:
        SQLAlchemy query object ready for execution
    """
    today = context['today']
    is_private_groups = context['is_private_groups']
    selected_countries = preferences['selected_countries']
    selected_continents_enum = preferences['selected_continents_enum']
    preferred_type_id = preferences['preferred_type_id']
    selected_year = preferences['year']
    selected_month = preferences['month']
    user_start_date = preferences['user_start_date']
    difficulty = preferences['difficulty']
    budget = preferences['budget']
    
    # Build base query
    query = build_base_query()
    
    # Apply filters
    query = apply_geographic_filters(query, selected_countries, selected_continents_enum)
    
    if preferred_type_id:
        query = query.filter(TripTemplate.trip_type_id == preferred_type_id)
    
    query = apply_date_filters(query, today, is_private_groups, selected_year, selected_month, user_start_date, config)
    query = apply_status_filters(query, is_private_groups)
    query = apply_difficulty_filter(query, difficulty, config.DIFFICULTY_TOLERANCE)
    query = apply_budget_filter(query, budget, config.BUDGET_MAX_MULTIPLIER)
    
    # Order by start_date
    query = query.order_by(TripOccurrence.start_date.asc())
    
    return query


def get_total_trips_count(today: date) -> int:
    """
    Get total count of available trips in database.
    
    Counts all active trips that are:
    - Not cancelled
    - Not full
    - Have spots available
    - Start date >= today
    
    Args:
        today: Current date for filtering
    
    Returns:
        Integer count of available trips
    """
    return db_session.query(TripOccurrence).join(TripTemplate).filter(
        TripTemplate.is_active == True,
        TripOccurrence.status.notin_(['Cancelled', 'Full']),
        TripOccurrence.spots_left > 0,
        TripOccurrence.start_date >= today
    ).count()


# ============================================
# SCORING & RANKING FUNCTIONS
# ============================================

def score_candidates(
    candidates: List[TripOccurrence],
    preferences: Dict[str, Any],
    context: Dict[str, Any],
    weights: Dict[str, float],
    config: type,
    format_trip_func
) -> List[Dict[str, Any]]:
    """
    Score candidate trips using a min-heap to keep only top N results.
    
    Uses a min-heap optimization to keep only the top MAX_CANDIDATES_TO_SCORE
    trips during scoring, avoiding the need to score all candidates when we
    only need a small subset. This significantly improves performance when
    there are many candidates.
    
    The heap stores (score, date, trip_dict) tuples where:
    - score: float score (lower is worse, kept at top of min-heap)
    - date: sort date string for tiebreaking
    - trip_dict: the scored trip dictionary
    
    Args:
        candidates: List of TripOccurrence objects to score
        preferences: Normalized preferences dict
        context: Search context dict
        weights: SCORING_WEIGHTS dict
        config: RecommendationConfig class
        format_trip_func: Function to format TripOccurrence as dict
    
    Returns:
        List of scored trip dicts (up to MAX_CANDIDATES_TO_SCORE, sorted by score descending)
    """
    today = context['today']
    private_groups_id = context['private_groups_id']
    max_candidates = config.MAX_CANDIDATES_TO_SCORE
    
    # Min-heap to keep only top N trips
    # Store (-score, sort_date, trip_dict) to use min-heap for max extraction
    # Negated score: higher scores become smaller values (so they stay in heap)
    # sort_date: earlier dates come first when scores are equal (ISO strings compare correctly)
    heap = []
    
    for occ in candidates:
        scored_trip = calculate_trip_score(
            occ,
            preferences,
            weights,
            config,
            today,
            private_groups_id,
            format_trip_func
        )
        
        if not scored_trip:  # Skip if None (filtered out)
            continue
        
        score = scored_trip['_float_score']
        sort_date = scored_trip['_sort_date']
        trip_id = scored_trip.get('id', 0)  # Use trip ID as tiebreaker to avoid dict comparison
        
        # Use negated score so min-heap keeps highest scores
        # Tuple: (-score, sort_date, trip_id, trip_dict)
        # When scores equal, earlier dates (smaller strings) come first
        # trip_id ensures we never compare dictionaries (all IDs are unique)
        heap_item = (-score, sort_date, trip_id, scored_trip)
        
        if len(heap) < max_candidates:
            # Heap not full yet, just add it
            heapq.heappush(heap, heap_item)
        else:
            # Heap is full, check if this trip is better than the worst one
            # Worst item has smallest -score (i.e., highest score), so we compare with heap[0]
            worst_item = heap[0]
            worst_negated_score = worst_item[0]
            if -score < worst_negated_score:  # score > worst_score (since both negated)
                # Replace worst trip with this better one
                heapq.heapreplace(heap, heap_item)
    
    # Extract top results from min-heap
    # Min-heap with negated scores: smallest negated_score = highest original_score
    # To get highest scores first, we need the smallest negated scores
    # Use nsmallest to get the smallest values (which are the highest original scores)
    top_items = heapq.nsmallest(max_candidates, heap)
    
    # Extract trip dicts and sort by original score descending, then date ascending
    # Format: (negated_score, sort_date, trip_id, trip_dict)
    scored_trips = [trip for _, _, _, trip in top_items]
    # Sort by original score (negate the negated score) descending, then date ascending
    scored_trips.sort(key=lambda x: (-x['_float_score'], x['_sort_date']))
    
    return scored_trips


def rank_and_select_top(
    scored_trips: List[Dict[str, Any]],
    max_results: int,
    config: type
) -> Tuple[List[Dict[str, Any]], set]:
    """
    Filter trips by score threshold and select top results.
    
    Since score_candidates returns pre-ranked results (sorted by score descending,
    date ascending), this function only needs to:
    1. Filter out trips below MIN_SCORE_THRESHOLD
    2. Slice to get top max_results (already in correct order)
    
    Args:
        scored_trips: List of scored trip dicts (already sorted by score_candidates)
        max_results: Maximum number of results to return
        config: RecommendationConfig class with MIN_SCORE_THRESHOLD
    
    Returns:
        Tuple of:
        - top_trips: List of top scored trips (up to max_results)
        - included_ids: Set of trip IDs already included
    """
    # Filter out trips with score below threshold
    # Results are already sorted, so filtering maintains order
    filtered_trips = [
        trip for trip in scored_trips 
        if trip['_float_score'] >= config.MIN_SCORE_THRESHOLD
    ]
    
    if len(filtered_trips) < len(scored_trips):
        print(f"[Recommendation] Filtered out {len(scored_trips) - len(filtered_trips)} trips with score < {config.MIN_SCORE_THRESHOLD}", flush=True)
    
    # Get top results (already sorted, just slice)
    top_trips = filtered_trips[:max_results]
    
    # Track IDs already included
    included_ids = {t['id'] for t in top_trips}
    
    return top_trips, included_ids


# ============================================
# RELAXED SEARCH FUNCTIONS
# ============================================

def should_use_relaxed_search(
    top_trips: List[Dict[str, Any]],
    min_threshold: int,
    max_results: int
) -> Tuple[bool, int]:
    """
    Determine if relaxed search should be executed.
    
    Relaxed search is used when we don't have enough primary results.
    This expands the search criteria to find more matching trips.
    
    Args:
        top_trips: List of top scored trips from primary search
        min_threshold: Minimum number of results needed (MIN_RESULTS_THRESHOLD)
        max_results: Maximum number of results desired (MAX_RESULTS)
    
    Returns:
        Tuple of:
        - should_relax: bool - True if relaxed search should be executed
        - needed_count: int - How many more trips are needed to reach max_results (0 if should_relax is False)
    """
    if len(top_trips) <= min_threshold:
        needed = max_results - len(top_trips)
        return True, needed
    return False, 0


def execute_relaxed_search(
    preferences: Dict[str, Any],
    context: Dict[str, Any],
    included_ids: set,
    needed_count: int,
    weights: Dict[str, float],
    config: type,
    format_trip_func
) -> List[Dict[str, Any]]:
    """
    Execute relaxed search to find additional trips.
    
    Relaxed search expands the search criteria:
    - Geography: Same continent if specific countries selected
    - Trip type: No filter (all types allowed with penalty)
    - Date: 2 months before/after selected date
    - Difficulty: +/-2 levels instead of +/-1
    - Budget: 50% over instead of 30%
    
    Args:
        preferences: Normalized preferences dict
        context: Search context dict
        included_ids: Set of trip IDs already included in primary results
        needed_count: Number of additional trips needed
        weights: SCORING_WEIGHTS dict
        config: RecommendationConfig class
        format_trip_func: Function to format TripOccurrence as dict
    
    Returns:
        List of relaxed trip results (with internal fields cleaned)
    """
    today = context['today']
    is_private_groups = context['is_private_groups']
    private_groups_id = context['private_groups_id']
    selected_countries = preferences['selected_countries']
    selected_continents_enum = preferences['selected_continents_enum']
    selected_year = preferences['year']
    selected_month = preferences['month']
    difficulty = preferences['difficulty']
    budget = preferences['budget']
    
    print(f"[Recommendation RELAXED] Only {len(included_ids)} primary results. Need {needed_count} more relaxed results.", flush=True)
    
    # Build relaxed query
    relaxed_query = build_relaxed_query(
        today,
        is_private_groups,
        selected_countries,
        selected_continents_enum,
        selected_year,
        selected_month,
        difficulty,
        budget,
        included_ids,
        config
    )
    
    relaxed_candidates = relaxed_query.all()
    print(f"[Recommendation RELAXED] Loaded {len(relaxed_candidates)} relaxed candidates for scoring", flush=True)
    
    # Score relaxed trips using min-heap (only keep top needed_count + buffer)
    # We need at least needed_count, but keep a few extra in case some are filtered
    max_relaxed = min(needed_count + 10, config.MAX_CANDIDATES_TO_SCORE)
    heap = []
    
    for occ in relaxed_candidates:
        scored_trip = calculate_relaxed_trip_score(
            occ,
            preferences,
            weights,
            config,
            today,
            private_groups_id,
            format_trip_func
        )
        
        if not scored_trip:
            continue
        
        score = scored_trip['_float_score']
        sort_date = scored_trip['_sort_date']
        trip_id = scored_trip.get('id', 0)  # Use trip ID as tiebreaker to avoid dict comparison
        
        # Use negated score for consistent tie-breaking (same as score_candidates)
        # Tuple: (-score, sort_date, trip_id, trip_dict)
        # trip_id ensures we never compare dictionaries (all IDs are unique)
        heap_item = (-score, sort_date, trip_id, scored_trip)
        
        if len(heap) < max_relaxed:
            heapq.heappush(heap, heap_item)
        else:
            worst_item = heap[0]
            worst_negated_score = worst_item[0]
            if -score < worst_negated_score:  # score > worst_score
                heapq.heapreplace(heap, heap_item)
    
    # Extract top results from min-heap (same logic as score_candidates)
    top_items = heapq.nsmallest(needed_count, heap)
    
    # Extract trip dicts and sort by original score descending, then date ascending
    # Format: (negated_score, sort_date, trip_id, trip_dict)
    relaxed_scored = [trip for _, _, _, trip in top_items]
    # Sort by original score (negate the negated score) descending, then date ascending
    relaxed_scored.sort(key=lambda x: (-x['_float_score'], x['_sort_date']))
    
    # Clean up internal fields
    relaxed_trips = []
    for trip in relaxed_scored:
        trip.pop('_sort_date', None)
        trip.pop('_float_score', None)
        relaxed_trips.append(trip)
    
    print(f"[Recommendation RELAXED] Added {len(relaxed_trips)} relaxed results", flush=True)
    
    return relaxed_trips


# ============================================
# RESULT FORMATTING FUNCTIONS
# ============================================

def format_results(
    primary_trips: List[Dict[str, Any]],
    relaxed_trips: List[Dict[str, Any]],
    total_candidates: int,
    total_trips_in_db: int
) -> Dict[str, Any]:
    """
    Clean up internal fields and format final response.
    
    Removes internal sorting/scoring fields (_sort_date, _float_score) from
    primary trips before returning the final response.
    
    Args:
        primary_trips: List of top scored trips (may contain internal fields)
        relaxed_trips: List of relaxed trips (already cleaned)
        total_candidates: Number of candidates that were scored
        total_trips_in_db: Total available trips in database
    
    Returns:
        Formatted response dict with:
        - primary_trips: List[Dict] - Top matching trips (cleaned)
        - relaxed_trips: List[Dict] - Expanded results if needed
        - total_candidates: int
        - total_trips_in_db: int
    """
    # Clean up internal fields from primary trips
    for trip in primary_trips:
        trip.pop('_sort_date', None)
        trip.pop('_float_score', None)
    
    return {
        'primary_trips': primary_trips,
        'relaxed_trips': relaxed_trips,
        'total_candidates': total_candidates,
        'total_trips_in_db': total_trips_in_db
    }


# ============================================
# MAIN ORCHESTRATION FUNCTION
# ============================================

def get_recommendations(
    preferences: Dict[str, Any],
    format_trip_func
) -> Dict[str, Any]:
    """
    Main recommendation algorithm orchestration function.
    
    Args:
        preferences: User preferences dict with:
            - selected_countries: List[int]
            - selected_continents: List[str] (will be normalized)
            - preferred_type_id: Optional[int]
            - preferred_theme_ids: List[int]
            - min_duration: int
            - max_duration: int
            - budget: Optional[float]
            - difficulty: Optional[int]
            - year: Optional[str]
            - month: Optional[str]
            - start_date: Optional[str] (legacy support)
        format_trip_func: Function to format TripOccurrence as trip dict
    
    Returns:
        Dict with:
            - primary_trips: List[Dict] - Top matching trips
            - relaxed_trips: List[Dict] - Expanded results if needed
            - total_candidates: int
            - total_trips_in_db: int
    """
    config = RecommendationConfig
    weights = SCORING_WEIGHTS
    
    # Step 1: Parse and normalize preferences
    parsed = parse_preferences(preferences)
    normalized = normalize_preferences(parsed)
    context = determine_search_context(normalized)
    
    # Step 2: Build query and get candidates
    query = build_primary_query(normalized, context, config)
    candidates = query.all()
    total_trips_in_db = get_total_trips_count(context['today'])
    
    print(f"[Recommendation] Loaded {len(candidates)} candidates for scoring", flush=True)
    
    # Step 3: Score and rank candidates
    scored_trips = score_candidates(
        candidates, normalized, context, weights, config, format_trip_func
    )
    top_trips, included_ids = rank_and_select_top(scored_trips, config.MAX_RESULTS, config)
    
    # Step 4: Relaxed search if needed
    should_relax, needed_count = should_use_relaxed_search(
        top_trips, config.MIN_RESULTS_THRESHOLD, config.MAX_RESULTS
    )
    relaxed_trips = []
    if should_relax:
        relaxed_trips = execute_relaxed_search(
            normalized, context, included_ids, needed_count,
            weights, config, format_trip_func
        )
    
    # Step 5: Format and return results
    return format_results(
        top_trips, relaxed_trips, len(candidates), total_trips_in_db
    )
