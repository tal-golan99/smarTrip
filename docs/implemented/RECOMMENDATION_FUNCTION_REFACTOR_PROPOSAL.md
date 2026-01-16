# Recommendation Function Refactor Proposal

**Splitting the Monolithic `get_recommendations()` Function into Focused, Testable Components**

---

## Overview

The `get_recommendations()` function in `backend/app/services/recommendation.py` is currently a monolithic 176-line function that handles multiple responsibilities. This proposal outlines a refactoring strategy to split it into smaller, focused functions that improve maintainability, testability, and readability.

**Goals:**
1. **Separation of Concerns:** Each function handles a single, well-defined responsibility
2. **Improved Testability:** Smaller functions are easier to unit test in isolation
3. **Better Readability:** Clear function names make the algorithm flow obvious
4. **Easier Maintenance:** Changes to one aspect don't require understanding the entire function
5. **Reduced Complexity:** Break down the cognitive load of understanding the recommendation algorithm

---

## Current Problem

### Monolithic Function Structure

The current `get_recommendations()` function (lines 636-812) handles:

1. **Preference Parsing & Normalization** (~25 lines)
   - Extracting preferences from dict
   - Parsing dates
   - Normalizing continents
   - Determining trip type flags

2. **Database Query Building** (~15 lines)
   - Building base query
   - Applying multiple filters
   - Getting total trip counts

3. **Candidate Scoring** (~20 lines)
   - Iterating through candidates
   - Calling scoring function
   - Filtering skipped trips

4. **Result Processing** (~10 lines)
   - Sorting by score and date
   - Selecting top results
   - Tracking included IDs

5. **Relaxed Search Logic** (~45 lines)
   - Checking if relaxed search needed
   - Building relaxed query
   - Scoring relaxed candidates
   - Merging results

6. **Cleanup & Return** (~10 lines)
   - Removing internal fields
   - Formatting response

### Issues with Current Structure

- **High Cognitive Load:** Understanding the entire flow requires reading 176 lines
- **Difficult Testing:** Hard to test individual steps without mocking the entire function
- **Poor Reusability:** Logic is tightly coupled and cannot be reused elsewhere
- **Maintenance Risk:** Changes to one part may inadvertently affect others
- **Code Duplication:** Some logic (like preference extraction) is repeated

---

## Proposed Solution

### Function Decomposition Strategy

Split `get_recommendations()` into focused functions organized by responsibility:

#### 1. **Preference Processing Layer**
   - `parse_preferences()` - Extract and validate preferences
   - `normalize_preferences()` - Normalize continents, dates, etc.
   - `determine_search_context()` - Determine flags like `is_private_groups`

#### 2. **Query Building Layer**
   - `build_primary_query()` - Build the main filtered query
   - `get_total_trips_count()` - Get database statistics

#### 3. **Scoring & Ranking Layer**
   - `score_candidates()` - Score all candidate trips
   - `rank_and_select_top()` - Sort and select top results

#### 4. **Relaxed Search Layer**
   - `should_use_relaxed_search()` - Determine if relaxed search is needed
   - `execute_relaxed_search()` - Execute the relaxed search logic

#### 5. **Result Assembly Layer**
   - `format_results()` - Clean up and format final results

### Proposed Function Signatures

```python
def parse_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and parse all preferences from the input dict.
    
    Returns a normalized dict with all preference values extracted and parsed.
    """
    pass

def normalize_preferences(raw_preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize preference values (continents, dates, etc.).
    
    Returns preferences dict with normalized values.
    """
    pass

def determine_search_context(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine search context flags and IDs.
    
    Returns dict with:
    - is_private_groups: bool
    - private_groups_id: int
    - today: date
    """
    pass

def build_primary_query(
    preferences: Dict[str, Any],
    context: Dict[str, Any],
    config: type
) -> Query:
    """
    Build the primary filtered query based on preferences.
    
    Returns SQLAlchemy query object.
    """
    pass

def get_total_trips_count(today: date) -> int:
    """
    Get total count of available trips in database.
    
    Returns count of active, non-cancelled, non-full trips.
    """
    pass

def score_candidates(
    candidates: List[TripOccurrence],
    preferences: Dict[str, Any],
    context: Dict[str, Any],
    weights: Dict[str, float],
    config: type,
    format_trip_func
) -> List[Dict[str, Any]]:
    """
    Score all candidate trips.
    
    Returns list of scored trip dicts (None entries filtered out).
    """
    pass

def rank_and_select_top(
    scored_trips: List[Dict[str, Any]],
    max_results: int
) -> Tuple[List[Dict[str, Any]], set]:
    """
    Sort trips by score and select top results.
    
    Returns:
    - top_trips: List of top scored trips
    - included_ids: Set of trip IDs already included
    """
    pass

def should_use_relaxed_search(
    top_trips: List[Dict[str, Any]],
    min_threshold: int
) -> Tuple[bool, int]:
    """
    Determine if relaxed search should be executed.
    
    Returns:
    - should_relax: bool
    - needed_count: int (how many more trips needed)
    """
    pass

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
    
    Returns list of relaxed trip results.
    """
    pass

def format_results(
    primary_trips: List[Dict[str, Any]],
    relaxed_trips: List[Dict[str, Any]],
    total_candidates: int,
    total_trips_in_db: int
) -> Dict[str, Any]:
    """
    Clean up internal fields and format final response.
    
    Returns formatted response dict.
    """
    pass

def get_recommendations(
    preferences: Dict[str, Any],
    format_trip_func
) -> Dict[str, Any]:
    """
    Main recommendation algorithm orchestration function.
    
    Now acts as a thin orchestrator that coordinates the smaller functions.
    """
    # Parse and normalize preferences
    parsed = parse_preferences(preferences)
    normalized = normalize_preferences(parsed)
    context = determine_search_context(normalized)
    
    # Build query and get candidates
    query = build_primary_query(normalized, context, RecommendationConfig)
    candidates = query.all()
    total_trips_in_db = get_total_trips_count(context['today'])
    
    # Score and rank
    scored_trips = score_candidates(
        candidates, normalized, context, 
        SCORING_WEIGHTS, RecommendationConfig, format_trip_func
    )
    top_trips, included_ids = rank_and_select_top(
        scored_trips, RecommendationConfig.MAX_RESULTS
    )
    
    # Relaxed search if needed
    should_relax, needed = should_use_relaxed_search(
        top_trips, RecommendationConfig.MIN_RESULTS_THRESHOLD
    )
    relaxed_trips = []
    if should_relax:
        relaxed_trips = execute_relaxed_search(
            normalized, context, included_ids, needed,
            SCORING_WEIGHTS, RecommendationConfig, format_trip_func
        )
    
    # Format and return
    return format_results(
        top_trips, relaxed_trips, len(candidates), total_trips_in_db
    )
```

---

## Implementation Plan

### Phase 1: Extract Preference Processing (Low Risk)
**Estimated Effort:** 1-2 hours

1. Create `parse_preferences()` function
   - Extract all preference values
   - Handle defaults and type conversions
   - Parse date strings

2. Create `normalize_preferences()` function
   - Normalize continents using existing `normalize_continents()`
   - Handle date parsing

3. Create `determine_search_context()` function
   - Get private groups ID
   - Determine `is_private_groups` flag
   - Get current date

4. Update `get_recommendations()` to use these functions
5. Test to ensure behavior unchanged

### Phase 2: Extract Query Building (Low Risk)
**Estimated Effort:** 1-2 hours

1. Create `build_primary_query()` function
   - Use existing filter functions
   - Apply all filters in sequence
   - Return query object

2. Create `get_total_trips_count()` function
   - Extract the count query logic
   - Return integer count

3. Update `get_recommendations()` to use these functions
4. Test to ensure behavior unchanged

### Phase 3: Extract Scoring & Ranking (Medium Risk)
**Estimated Effort:** 2-3 hours

1. Create `score_candidates()` function
   - Iterate through candidates
   - Call `calculate_trip_score()` for each
   - Filter out None results
   - Return list of scored trips

2. Create `rank_and_select_top()` function
   - Sort by score and date
   - Select top N results
   - Track included IDs
   - Return both results and ID set

3. Update `get_recommendations()` to use these functions
4. Test to ensure behavior unchanged

### Phase 4: Extract Relaxed Search (Medium Risk)
**Estimated Effort:** 2-3 hours

1. Create `should_use_relaxed_search()` function
   - Check if results below threshold
   - Calculate needed count
   - Return boolean and count

2. Create `execute_relaxed_search()` function
   - Build relaxed query using existing `build_relaxed_query()`
   - Score relaxed candidates using `calculate_relaxed_trip_score()`
   - Sort and select needed trips
   - Clean up internal fields
   - Return relaxed trips list

3. Update `get_recommendations()` to use these functions
4. Test to ensure behavior unchanged

### Phase 5: Extract Result Formatting (Low Risk)
**Estimated Effort:** 1 hour

1. Create `format_results()` function
   - Remove internal fields from primary trips
   - Assemble final response dict
   - Return formatted response

2. Update `get_recommendations()` to use this function
3. Test to ensure behavior unchanged

### Phase 6: Final Cleanup & Documentation
**Estimated Effort:** 1-2 hours

1. Review all functions for consistency
2. Add comprehensive docstrings
3. Add type hints where missing
4. Update module-level documentation
5. Run full test suite
6. Code review

---

## Benefits

### 1. Improved Testability

**Before:**
```python
# Hard to test individual steps
def test_difficulty_filtering():
    # Must mock entire get_recommendations() function
    # Cannot test just the filtering logic
    pass
```

**After:**
```python
# Easy to test individual components
def test_build_primary_query_with_difficulty():
    preferences = {'difficulty': 3}
    context = {'today': date.today(), 'is_private_groups': False}
    query = build_primary_query(preferences, context, RecommendationConfig)
    # Test query directly
    pass
```

### 2. Better Readability

**Before:**
- 176-line function requires reading entire function to understand flow
- Logic is buried in nested conditionals

**After:**
- Main function is ~30 lines showing high-level flow
- Each step is clearly named and focused
- Easy to understand algorithm at a glance

### 3. Easier Maintenance

**Before:**
- Changing preference parsing requires understanding entire function
- Risk of breaking unrelated logic

**After:**
- Change preference parsing in one focused function
- Clear boundaries between responsibilities
- Reduced risk of side effects

### 4. Reusability

**Before:**
- Cannot reuse preference parsing logic elsewhere
- Query building logic is tightly coupled

**After:**
- `parse_preferences()` can be used in other contexts
- `build_primary_query()` can be used for different recommendation types
- Functions can be composed in different ways

### 5. Performance Debugging

**Before:**
- Hard to identify which step is slow
- Must profile entire function

**After:**
- Can profile individual functions
- Easy to identify bottlenecks
- Can optimize specific steps independently

---

## Migration Strategy

### Backward Compatibility

- **No API Changes:** The public interface `get_recommendations()` remains unchanged
- **Same Behavior:** All refactored functions produce identical results
- **Gradual Migration:** Can be done incrementally, testing after each phase

### Testing Strategy

1. **Unit Tests:** Write tests for each new function
2. **Integration Tests:** Ensure `get_recommendations()` still works end-to-end
3. **Regression Tests:** Compare outputs before/after refactoring
4. **Performance Tests:** Ensure no performance degradation

### Rollback Plan

- Each phase is independent and can be rolled back
- Git commits after each phase for easy rollback
- Original function can be kept as reference during migration

---

## Code Organization

### Proposed File Structure

```
backend/app/services/recommendation.py
├── Constants (SCORING_WEIGHTS, SCORE_THRESHOLDS, RecommendationConfig)
├── Helper Functions (normalize_continents, get_private_groups_type_id, build_base_query)
├── Filtering Functions (apply_geographic_filters, apply_date_filters, etc.)
├── Scoring Functions (calculate_trip_score, calculate_relaxed_trip_score)
├── Query Building Functions (build_relaxed_query)
│
├── NEW: Preference Processing Functions
│   ├── parse_preferences()
│   ├── normalize_preferences()
│   └── determine_search_context()
│
├── NEW: Query Building Functions
│   ├── build_primary_query()
│   └── get_total_trips_count()
│
├── NEW: Scoring & Ranking Functions
│   ├── score_candidates()
│   └── rank_and_select_top()
│
├── NEW: Relaxed Search Functions
│   ├── should_use_relaxed_search()
│   └── execute_relaxed_search()
│
├── NEW: Result Formatting Functions
│   └── format_results()
│
└── Main Orchestration Function
    └── get_recommendations()  # Now ~30 lines, orchestrates above functions
```

---

## Example: Refactored Main Function

```python
def get_recommendations(
    preferences: Dict[str, Any],
    format_trip_func
) -> Dict[str, Any]:
    """
    Main recommendation algorithm orchestration function.
    
    Coordinates the recommendation pipeline:
    1. Parse and normalize user preferences
    2. Build filtered query and get candidates
    3. Score and rank candidates
    4. Execute relaxed search if needed
    5. Format and return results
    
    Args:
        preferences: User preferences dict
        format_trip_func: Function to format TripOccurrence as dict
    
    Returns:
        Dict with primary_trips, relaxed_trips, total_candidates, total_trips_in_db
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
    top_trips, included_ids = rank_and_select_top(scored_trips, config.MAX_RESULTS)
    
    # Step 4: Relaxed search if needed
    should_relax, needed = should_use_relaxed_search(
        top_trips, config.MIN_RESULTS_THRESHOLD
    )
    relaxed_trips = []
    if should_relax:
        relaxed_trips = execute_relaxed_search(
            normalized, context, included_ids, needed,
            weights, config, format_trip_func
        )
    
    # Step 5: Format and return results
    return format_results(
        top_trips, relaxed_trips, len(candidates), total_trips_in_db
    )
```

**Line Count:** ~45 lines (down from 176)
**Readability:** High - clear step-by-step flow
**Maintainability:** High - each step is independently testable

---

## Risk Assessment

### Low Risk Areas
- **Preference Processing:** Well-isolated logic, easy to extract
- **Query Building:** Uses existing helper functions
- **Result Formatting:** Simple data transformation

### Medium Risk Areas
- **Scoring & Ranking:** Must ensure sorting logic is preserved exactly
- **Relaxed Search:** Complex logic with multiple dependencies

### Mitigation Strategies
1. **Incremental Migration:** One phase at a time with testing
2. **Comprehensive Testing:** Unit tests for each function
3. **Output Comparison:** Compare outputs before/after each phase
4. **Code Review:** Review each phase before proceeding

---

## Success Criteria

1. ✅ All existing tests pass
2. ✅ No change in recommendation results (verified by comparison)
3. ✅ Main function reduced to ~30-50 lines
4. ✅ Each extracted function is < 50 lines
5. ✅ All functions have comprehensive docstrings
6. ✅ Code coverage maintained or improved
7. ✅ No performance degradation

---

## Timeline

- **Phase 1-2:** 2-4 hours (Preference Processing + Query Building)
- **Phase 3:** 2-3 hours (Scoring & Ranking)
- **Phase 4:** 2-3 hours (Relaxed Search)
- **Phase 5-6:** 2-3 hours (Formatting + Cleanup)

**Total Estimated Time:** 8-13 hours

---

## Next Steps

1. **Review this proposal** with the team
2. **Get approval** for the refactoring approach
3. **Start with Phase 1** (lowest risk)
4. **Test thoroughly** after each phase
5. **Iterate** based on feedback

---

## Questions & Considerations

1. **Should we create a separate module?** 
   - Option A: Keep all functions in `recommendation.py`
   - Option B: Split into `recommendation/` package with multiple modules
   - **Recommendation:** Start with Option A, split later if needed

2. **Should we add caching?**
   - Some functions (like `get_total_trips_count()`) could benefit from caching
   - Consider adding after refactoring is complete

3. **Should we add logging?**
   - Each function could log its execution time
   - Helps with performance debugging

4. **Type hints?**
   - Add comprehensive type hints to all new functions
   - Improves IDE support and catches errors early

---

## Conclusion

This refactoring will significantly improve the maintainability and testability of the recommendation system. By breaking down the monolithic function into focused, single-responsibility functions, we make the codebase more professional, easier to understand, and simpler to modify.

The incremental approach minimizes risk while providing immediate benefits after each phase. The main orchestration function will become a clear, readable pipeline that's easy to understand at a glance.
