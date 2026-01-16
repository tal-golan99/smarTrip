"""
Scoring Functions for Trip Recommendations
"""

from datetime import date
from typing import Dict, List, Optional, Any
import heapq

from app.models.trip import TripOccurrence
from .constants import RecommendationConfig, SCORING_WEIGHTS


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
    # Store (-score, sort_date, trip_id, trip_dict) to use min-heap for max extraction
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
