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

from app.core.database import db_session
from app.models.trip import (
    TripOccurrence, TripTemplate, TripTemplateTag, Country, TripType
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
    MIN_RESULTS_THRESHOLD = 6       # If results < this, add relaxed results
    THEME_MATCH_THRESHOLD = 2       # Need 2+ themes for full points


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
    user_start_date: Optional[date]
):
    """Apply date filters (year, month, start_date)."""
    if is_private_groups:
        return query
    
    query = query.filter(TripOccurrence.start_date >= today)
    
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
    included_ids: set
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
    today = datetime.now().date()
    
    # Parse preferences
    selected_countries = preferences.get('selected_countries', []) or []
    selected_continents_input = preferences.get('selected_continents', []) or []
    preferred_type_id = preferences.get('preferred_type_id')
    preferred_theme_ids = preferences.get('preferred_theme_ids', []) or []
    min_duration = preferences.get('min_duration', 1) or 1
    max_duration = preferences.get('max_duration', 365) or 365
    budget = preferences.get('budget')
    difficulty = preferences.get('difficulty')
    selected_year = preferences.get('year')
    selected_month = preferences.get('month')
    start_date_str = preferences.get('start_date')  # Legacy support
    
    # Parse start date safely (legacy support)
    user_start_date = None
    if start_date_str:
        try:
            user_start_date = datetime.fromisoformat(start_date_str).date()
        except (ValueError, TypeError):
            user_start_date = None
    
    # Normalize continents
    selected_continents_enum = normalize_continents(selected_continents_input)
    
    # Get private groups ID
    private_groups_id = get_private_groups_type_id()
    is_private_groups = (preferred_type_id == private_groups_id)
    
    # Total trips count (exclude Cancelled and Full)
    total_trips_in_db = db_session.query(TripOccurrence).join(TripTemplate).filter(
        TripTemplate.is_active == True,
        TripOccurrence.status.notin_(['Cancelled', 'Full']),
        TripOccurrence.spots_left > 0,
        TripOccurrence.start_date >= today
    ).count()
    
    # Build primary query
    query = build_base_query()
    
    # Apply filters
    query = apply_geographic_filters(query, selected_countries, selected_continents_enum)
    
    if preferred_type_id:
        query = query.filter(TripTemplate.trip_type_id == preferred_type_id)
    
    query = apply_date_filters(query, today, is_private_groups, selected_year, selected_month, user_start_date)
    query = apply_status_filters(query, is_private_groups)
    query = apply_difficulty_filter(query, difficulty, config.DIFFICULTY_TOLERANCE)
    query = apply_budget_filter(query, budget, config.BUDGET_MAX_MULTIPLIER)
    
    # Get all candidates for scoring
    query = query.order_by(TripOccurrence.start_date.asc())
    candidates = query.all()
    
    print(f"[Recommendation] Loaded {len(candidates)} candidates for scoring", flush=True)
    
    # Score candidates
    scored_trips = []
    preferences_with_continents = {
        **preferences,
        'selected_continents_enum': selected_continents_enum
    }
    
    for occ in candidates:
        scored_trip = calculate_trip_score(
            occ,
            preferences_with_continents,
            weights,
            config,
            today,
            private_groups_id,
            format_trip_func
        )
        if scored_trip:  # None means trip was skipped
            scored_trips.append(scored_trip)
    
    # Sort by score descending, then date ascending
    scored_trips.sort(key=lambda x: (-x['_float_score'], x['_sort_date']))
    
    # Get top results
    top_trips = scored_trips[:config.MAX_RESULTS]
    
    # Track IDs already included
    included_ids = {t['id'] for t in top_trips}
    
    # RELAXED SEARCH
    relaxed_trips = []
    if len(top_trips) < config.MIN_RESULTS_THRESHOLD:
        needed = config.MAX_RESULTS - len(top_trips)
        print(f"[Recommendation RELAXED] Only {len(top_trips)} primary results. Need {needed} more relaxed results.", flush=True)
        
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
            included_ids
        )
        
        relaxed_candidates = relaxed_query.all()
        print(f"[Recommendation RELAXED] Loaded {len(relaxed_candidates)} relaxed candidates for scoring", flush=True)
        
        # Score relaxed trips
        relaxed_scored = []
        for occ in relaxed_candidates:
            scored_trip = calculate_relaxed_trip_score(
                occ,
                preferences_with_continents,
                weights,
                config,
                today,
                private_groups_id,
                format_trip_func
            )
            if scored_trip:
                relaxed_scored.append(scored_trip)
        
        # Sort relaxed trips
        relaxed_scored.sort(key=lambda x: (-x['_float_score'], x['_sort_date']))
        
        # Add needed relaxed trips
        for trip in relaxed_scored[:needed]:
            trip.pop('_sort_date', None)
            trip.pop('_float_score', None)
            relaxed_trips.append(trip)
        
        print(f"[Recommendation RELAXED] Added {len(relaxed_trips)} relaxed results", flush=True)
    
    # Clean up internal fields from top_trips
    for trip in top_trips:
        trip.pop('_sort_date', None)
        trip.pop('_float_score', None)
    
    return {
        'primary_trips': top_trips,
        'relaxed_trips': relaxed_trips,
        'total_candidates': len(candidates),
        'total_trips_in_db': total_trips_in_db
    }
