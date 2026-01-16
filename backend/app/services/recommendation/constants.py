"""
Constants and Configuration for Recommendation System
"""

# Scoring weights dictionary (all float values)
# Raw point accumulation - max possible = 100
SCORING_WEIGHTS = {
    # Base score for passing hard filters
    'BASE_SCORE': 30.0,           # All trips that pass filters start here
    'RELAXED_PENALTY': -15.0,     # Penalty for relaxed/expanded results
    
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
    MAX_RESULTS = 30                # Return top 30 recommendations
    MIN_RESULTS_THRESHOLD = 5       # If results <= this, add relaxed results
    MAX_CANDIDATES_TO_SCORE = 30   # Use min-heap to keep only top 30 during scoring
    THEME_MATCH_THRESHOLD = 2       # Need 2+ themes for full points
    
    # Filtering parameters
    MIN_SCORE_THRESHOLD = 30        # Don't show results with score less than this (change this value to adjust threshold)
    MAX_YEARS_AHEAD = 1             # Show trips for current year + next N years only (1 = current + next year)
    
    # Frontend "Show More" parameters
    SHOW_MORE_INCREMENT = 10        # Number of additional results to show per "show more" click
    MAX_SHOW_MORE_CLICKS = 1        # Maximum number of times "show more" can be clicked
