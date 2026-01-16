"""
Main Recommendation Engine
"""

from typing import Dict, List, Tuple, Any

from .constants import RecommendationConfig, SCORING_WEIGHTS
from .context import parse_preferences, normalize_preferences, determine_search_context
from .filters import build_primary_query, get_total_trips_count
from .scoring import score_candidates
from .relaxed_search import should_use_relaxed_search, execute_relaxed_search


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
        total_candidates: Number of candidates that matched search filters (scored)
        total_trips_in_db: Total available trips in database (for reference)
    
    Returns:
        Formatted response dict with:
        - primary_trips: List[Dict] - Top matching trips (cleaned)
        - relaxed_trips: List[Dict] - Expanded results if needed
        - total_candidates: int - Total trips that matched search filters
        - total_trips_in_db: int - Total available trips in DB (all trips, not filtered)
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
