# Recommendation Service Package

**Modular recommendation engine for trip matching and scoring**

This package implements a sophisticated recommendation algorithm that matches users with trip recommendations based on their preferences, using a min-heap optimized scoring system.

---

## Package Structure

```
recommendation/
├── __init__.py          # Package exports (get_recommendations, constants)
├── constants.py         # Configuration and scoring weights
├── context.py           # Preference processing and search context
├── filters.py           # Query building and database filtering
├── scoring.py           # Trip scoring functions (min-heap optimized)
├── relaxed_search.py    # Expanded search for additional results
├── engine.py            # Main orchestration engine
└── README.md            # This file
```

---

## Module Responsibilities

### `constants.py`
**Purpose:** Centralized configuration and scoring weights

**Exports:**
- `SCORING_WEIGHTS` - Dictionary of point values for match criteria
- `SCORE_THRESHOLDS` - Thresholds for frontend color coding (HIGH: 70, MID: 50)
- `RecommendationConfig` - Configuration class with filtering thresholds and result limits

**Key Configuration Values:**
- `MAX_RESULTS = 10` - Return top 10 recommendations
- `MIN_RESULTS_THRESHOLD = 5` - Trigger relaxed search if ≤5 results
- `MAX_CANDIDATES_TO_SCORE = 30` - Min-heap limit for performance
- `MIN_SCORE_THRESHOLD = 30` - Filter out trips below this score
- `MAX_YEARS_AHEAD = 1` - Show current year + next year only

---

### `context.py`
**Purpose:** Process and normalize user preferences, determine search context

**Functions:**
- `normalize_continents(continents_input)` - Map continent names to DB enum values
- `get_private_groups_type_id()` - Get Private Groups trip type ID from database
- `parse_preferences(preferences)` - Extract and parse all preferences from input
- `normalize_preferences(parsed_preferences)` - Normalize values (continents, dates)
- `determine_search_context(preferences)` - Get runtime context (today, flags, IDs)

**Returns Context Dict:**
```python
{
    'today': date,
    'private_groups_id': int,
    'is_private_groups': bool
}
```

---

### `filters.py`
**Purpose:** Build SQLAlchemy queries with optimized filtering

**Functions:**
- `build_base_query()` - Base query with eager loading
- `apply_geographic_filters(query, countries, continents)` - Country/continent filters
- `apply_date_filters(query, today, is_private, year, month, start_date, config)` - Date filtering
- `apply_status_filters(query, is_private_groups)` - Exclude Cancelled/Full trips
- `apply_difficulty_filter(query, difficulty, tolerance)` - Difficulty range filter
- `apply_budget_filter(query, budget, multiplier)` - Budget ceiling filter
- `build_primary_query(preferences, context, config)` - Build complete filtered query
- `get_total_trips_count(today)` - Get count of available trips in DB

**Optimizations:**
- Uses `joinedload` and `selectinload` to avoid N+1 queries
- Filters applied in optimal order

---

### `scoring.py`
**Purpose:** Calculate match scores for trips using min-heap optimization

**Functions:**
- `calculate_trip_score(occurrence, preferences, weights, config, ...)` - Score single trip
- `calculate_relaxed_trip_score(...)` - Score trip with relaxed penalties
- `score_candidates(candidates, preferences, context, weights, config, ...)` - **Min-heap optimized scoring**

**Min-Heap Implementation:**
- Uses `heapq` to keep only top 30 candidates during scoring
- Time complexity: O(N log K) where N = candidates, K = 30
- Heap stores: `(-score, sort_date, trip_id, trip_dict)`
- Extracts using `heapq.nsmallest()` then sorts for final ordering

**Scoring Factors:**
- Base score (25 points)
- Theme matching (full: +25, partial: +12, none: -15)
- Difficulty matching (+15)
- Duration matching (ideal: +12, good: +8)
- Budget matching (perfect: +12, good: +8, acceptable: +5)
- Status bonuses (guaranteed: +7, last places: +15)
- Departing soon bonus (+7)
- Geography bonuses (direct country: +15, continent: +5)

---

### `relaxed_search.py`
**Purpose:** Execute expanded search when primary results are insufficient

**Functions:**
- `build_relaxed_query(...)` - Build query with expanded filters
- `should_use_relaxed_search(top_trips, min_threshold, max_results)` - Decision logic
- `execute_relaxed_search(...)` - **Min-heap optimized relaxed scoring**

**Relaxed Search Expansions:**
- Geography: Same continent if specific countries selected
- Trip type: No filter (all types allowed with penalty)
- Date: 2 months before/after selected date
- Difficulty: ±2 levels instead of ±1
- Budget: 50% over instead of 30%

**Min-Heap Implementation:**
- Same pattern as `score_candidates()` for consistency
- Keeps `needed_count + 10` (max 30) candidates in heap

---

### `engine.py`
**Purpose:** Main orchestration and result formatting

**Functions:**
- `get_recommendations(preferences, format_trip_func)` - **Main entry point**
- `rank_and_select_top(scored_trips, max_results, config)` - Filter by threshold and select top
- `format_results(primary_trips, relaxed_trips, total_candidates, total_trips_in_db)` - Clean and format response

**Algorithm Flow:**
1. Parse and normalize preferences
2. Build filtered query and get candidates
3. Score candidates (min-heap keeps top 30)
4. Rank and filter by score threshold
5. Execute relaxed search if needed (≤5 results)
6. Format and return results

---

## Usage

### Basic Usage
```python
from app.services.recommendation import get_recommendations

preferences = {
    'selected_countries': [1, 5, 10],
    'selected_continents': ['Europe', 'Asia'],
    'preferred_type_id': 1,
    'preferred_theme_ids': [3, 7, 12],
    'min_duration': 7,
    'max_duration': 21,
    'budget': 5000.0,
    'difficulty': 3,
    'year': '2026',
    'month': '06'
}

def format_trip_func(occurrence, include_relations=False):
    # Your trip formatting function
    return occurrence.to_dict(include_relations=include_relations)

result = get_recommendations(preferences, format_trip_func)
# Returns: {
#     'primary_trips': [...],    # Top 10 matching trips
#     'relaxed_trips': [...],    # Additional trips if needed
#     'total_candidates': 150,   # Number of candidates scored
#     'total_trips_in_db': 542   # Total available trips
# }
```

### Importing Constants
```python
from app.services.recommendation.constants import (
    SCORING_WEIGHTS,
    SCORE_THRESHOLDS,
    RecommendationConfig
)

# Access configuration
max_results = RecommendationConfig.MAX_RESULTS  # 10
min_threshold = RecommendationConfig.MIN_SCORE_THRESHOLD  # 30

# Access scoring weights
theme_full_points = SCORING_WEIGHTS['THEME_FULL']  # 25.0
```

### Advanced: Using Individual Modules
```python
from app.services.recommendation.context import (
    parse_preferences,
    normalize_preferences,
    determine_search_context
)
from app.services.recommendation.filters import build_primary_query
from app.services.recommendation.scoring import score_candidates

# Build your own custom recommendation flow
parsed = parse_preferences(user_input)
normalized = normalize_preferences(parsed)
context = determine_search_context(normalized)
query = build_primary_query(normalized, context, RecommendationConfig)
candidates = query.all()
scored = score_candidates(candidates, normalized, context, ...)
```

---

## Performance Optimizations

### Min-Heap Algorithm
The scoring system uses a min-heap to limit the number of trips scored and kept in memory:

- **Before:** Score all candidates (could be 1000+), sort all, take top 10
  - Time: O(N log N) where N = all candidates
  - Memory: Stores all scored trips

- **After:** Keep only top 30 in min-heap during scoring, extract and sort
  - Time: O(N log K) where K = 30 (MAX_CANDIDATES_TO_SCORE)
  - Memory: Only stores 30 trips in heap

**Performance Gain:** ~97% reduction when N = 1000 (from 10,000 operations to 300)

### Query Optimization
- Uses `joinedload` for many-to-one relationships
- Uses `selectinload` for one-to-many to avoid cartesian products
- Filters applied efficiently in database
- Only loads necessary relationships

---

## Algorithm Details

### Scoring System
1. **Base Score:** All trips that pass filters start with 25 points
2. **Theme Matching:** Checks overlap between user's preferred themes and trip's themes
3. **Difficulty:** Exact match gives +15 points
4. **Duration:** Within range = +12, within ±4 days = +8, outside ±7 days = filtered out
5. **Budget:** Within budget = +12, within 110% = +8, within 120% = +5
6. **Status Bonuses:** Guaranteed departures (+7), Last Places (+15)
7. **Urgency:** Departing within 30 days (+7)
8. **Geography:** Direct country match (+15), Continent match (+5)

**Final Score:** Clamped to 0-100 range

### Relaxed Search Trigger
- Triggered when primary results ≤ 5 (MIN_RESULTS_THRESHOLD)
- Fills up to MAX_RESULTS (10) with expanded search
- Relaxed trips have -20 penalty applied
- Different trip type gets -10 penalty

---

## Testing

### Unit Testing Individual Modules
Each module can be tested independently:

```python
# Test context processing
from app.services.recommendation.context import normalize_continents
assert normalize_continents(['Europe', 'Asia']) == ['EUROPE', 'ASIA']

# Test scoring
from app.services.recommendation.scoring import calculate_trip_score
score = calculate_trip_score(trip_occurrence, preferences, ...)

# Test filtering
from app.services.recommendation.filters import build_primary_query
query = build_primary_query(preferences, context, config)
```

### Integration Testing
Test the full recommendation flow:

```python
from app.services.recommendation import get_recommendations

result = get_recommendations(test_preferences, format_func)
assert len(result['primary_trips']) <= 10
assert result['total_candidates'] >= 0
```

---

## Dependencies

### External Dependencies
- `sqlalchemy` - Database ORM and query building
- `dateutil` - Date manipulation (relativedelta)
- `heapq` - Min-heap data structure (standard library)

### Internal Dependencies
- `app.core.database` - Database session
- `app.models.trip` - Trip models (TripOccurrence, TripTemplate, etc.)

### Inter-Module Dependencies
```
engine.py
  ├── constants.py
  ├── context.py
  ├── filters.py
  ├── scoring.py
  └── relaxed_search.py
      ├── constants.py
      ├── filters.py
      └── scoring.py
```

---

## Migration from recommendation.py

The old monolithic `recommendation.py` file has been split into this package structure and archived to `backend/scripts/_archive/recommendation_archive/recommendation.py`.

**Package Structure:**
```python
# Main entry point (only exports get_recommendations)
from app.services.recommendation import get_recommendations

# Direct module imports for constants
from app.services.recommendation.constants import RecommendationConfig, SCORING_WEIGHTS

# Direct module imports for advanced usage
from app.services.recommendation.engine import get_recommendations
from app.services.recommendation.scoring import score_candidates
```

**Note:** The old `recommendation.py` file has been archived and is no longer in use. All imports should use the package structure.

---

## Future Improvements

### Potential Enhancements
1. **Caching:** Cache `get_total_trips_count()` and `get_private_groups_type_id()`
2. **Async Support:** Make scoring functions async for better concurrency
3. **Configuration:** Move config to environment variables or config file
4. **Metrics:** Add performance metrics and logging for each module
5. **A/B Testing:** Support multiple scoring algorithms for experimentation

### Extension Points
- Custom scoring weights: Modify `constants.py` or pass custom weights
- Custom filters: Extend `filters.py` with additional filter functions
- Custom scoring: Extend `scoring.py` with additional scoring factors
- Custom relaxed search: Modify `relaxed_search.py` with different expansion strategies

---

## Code Organization Principles

This package follows **Single Responsibility Principle (SRP)**:

- **constants.py** - Only configuration
- **context.py** - Only preference processing
- **filters.py** - Only query building
- **scoring.py** - Only scoring logic
- **relaxed_search.py** - Only relaxed search logic
- **engine.py** - Only orchestration

Each module has a single, well-defined purpose, making the codebase easier to:
- **Test:** Test each module independently
- **Maintain:** Changes isolated to relevant module
- **Understand:** Clear boundaries between concerns
- **Extend:** Add new functionality without affecting existing code

---

## Troubleshooting

### Common Issues

**Import Errors:**
```python
# Ensure you're importing from the package, not the old file
from app.services.recommendation import get_recommendations  # Correct
from app.services import recommendation  # May import old file
```

**Circular Import Errors:**
- All inter-module imports use relative imports (`.constants`, `.filters`)
- External imports are at the top of each module
- No circular dependencies exist

**Performance Issues:**
- Check `MAX_CANDIDATES_TO_SCORE` - reduce if memory constrained
- Profile `score_candidates()` if scoring is slow
- Check database query performance in `filters.py`

---

## Contributing

When adding new functionality:

1. **Scoring Factors:** Add to `scoring.py` → `calculate_trip_score()`
2. **Filters:** Add to `filters.py` → `build_primary_query()`
3. **Config Values:** Add to `constants.py` → `RecommendationConfig`
4. **Preference Fields:** Add to `context.py` → `parse_preferences()`

Always maintain:
- Backward compatibility in `__init__.py`
- Type hints for all functions
- Comprehensive docstrings
- Min-heap optimization pattern in scoring functions
