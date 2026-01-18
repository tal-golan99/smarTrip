"""
Relaxed Search Functions for Expanded Results
"""

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import or_, extract
from typing import Dict, List, Optional, Tuple, Any

from app.core.database import db_session
from app.models.trip import TripTemplate, TripOccurrence, Country
from .constants import RecommendationConfig
from .filters import build_base_query, apply_difficulty_filter, apply_budget_filter
from .scoring import calculate_relaxed_trip_score, _score_with_min_heap


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
        
        # Handle year and month filters (can be independent)
        if selected_year and selected_year != 'all':
            try:
                year_int = int(selected_year)
                
                if selected_month and selected_month != 'all':
                    # User selected both year AND month: expand by 2 months before and after
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
        elif selected_month and selected_month != 'all':
            # User selected ONLY month (no year): filter by month across all valid years
            # For relaxed search, expand by 2 months before and after
            try:
                month_int = int(selected_month)
                
                # Create date ranges for the selected month +/- 2 months in current and next years
                # This will match trips in the target month window across multiple years
                target_months = []
                for offset in [-2, -1, 0, 1, 2]:
                    target_month = (month_int + offset - 1) % 12 + 1  # Convert to 1-12 range
                    target_months.append(target_month)
                
                relaxed_query = relaxed_query.filter(
                    extract('month', TripOccurrence.start_date).in_(target_months)
                )
                print(f"[Recommendation RELAXED] Month-only filter: months {target_months} (expanded from {month_int})", flush=True)
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
    
    # Score relaxed trips using shared min-heap algorithm
    # We need at least needed_count, but keep a few extra in case some are filtered
    max_relaxed = min(needed_count + 10, config.MAX_CANDIDATES_TO_SCORE)
    
    # Create a scoring function closure
    def score_func(occ: TripOccurrence):
        return calculate_relaxed_trip_score(
            occ, preferences, weights, config, today, private_groups_id, format_trip_func
        )
    
    # Use shared min-heap algorithm (same as primary search)
    relaxed_scored = _score_with_min_heap(relaxed_candidates, score_func, max_relaxed, needed_count)
    
    # Filter out trips with score below MIN_SCORE_THRESHOLD (same as primary search)
    filtered_relaxed = [
        trip for trip in relaxed_scored
        if trip['_float_score'] >= config.MIN_SCORE_THRESHOLD
    ]
    
    if len(filtered_relaxed) < len(relaxed_scored):
        print(f"[Recommendation RELAXED] Filtered out {len(relaxed_scored) - len(filtered_relaxed)} relaxed trips with score < {config.MIN_SCORE_THRESHOLD}", flush=True)
    
    # Clean up internal fields
    relaxed_trips = []
    for trip in filtered_relaxed:
        trip.pop('_sort_date', None)
        trip.pop('_float_score', None)
        relaxed_trips.append(trip)
    
    print(f"[Recommendation RELAXED] Added {len(relaxed_trips)} relaxed results", flush=True)
    
    return relaxed_trips
