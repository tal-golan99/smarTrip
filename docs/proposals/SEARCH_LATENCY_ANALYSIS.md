# Search Latency Analysis

## Overview

This document analyzes the latency sources in the trip recommendation search system, identifying bottlenecks and potential optimizations.

## Current Performance Profile

### Typical Search Request Timeline

```
User clicks search
  ↓
Frontend builds request (~5ms)
  ↓
Network: Frontend → Backend API (~50-200ms) [Geographic latency]
  ↓
Backend receives request (~1ms)
  ↓
Database Query 1: Build base query with joins (~100-500ms)
  ↓
Database Query 2: Apply filters and fetch candidates (~50-300ms)
  ↓
Python Scoring: Process all candidates (~50-200ms)
  ↓
[If < 6 results] Relaxed Search Query (~100-500ms)
  ↓
[If < 6 results] Python Scoring: Process relaxed candidates (~50-200ms)
  ↓
Format results (~10-50ms)
  ↓
Network: Backend → Frontend (~50-200ms) [Geographic latency]
  ↓
Frontend renders results (~50-100ms)
```

**Total Estimated Time: 500ms - 2,500ms (0.5 - 2.5 seconds)**

---

## Latency Sources Breakdown

### 1. Geographic Network Latency (100-400ms)

**Location**: Frontend ↔ Backend ↔ Database

**Impact**: HIGH

**Details**:
- **Frontend → Backend**: User location to backend server
  - If backend is in US and user is in Israel: ~150-250ms
  - If backend is in US and user is in US: ~20-50ms
- **Backend → Database**: Backend server to Supabase database
  - If both in US: ~10-30ms
  - If backend in US, database in different region: ~50-150ms

**Mitigation Options**:
1. Deploy backend closer to users (CDN/Edge functions)
2. Use database connection pooling (already implemented)
3. Implement response caching (partially implemented in frontend)

**Current Status**: 
- ✅ Connection pooling configured (pool_size=5-10)
- ✅ Frontend caching for results page
- ❌ No backend response caching
- ❌ No CDN/edge deployment

---

### 2. Database Query Complexity (150-800ms)

**Location**: `backend/app/services/recommendation.py` → `build_base_query()`

**Impact**: HIGH

**Query Structure**:
```python
db_session.query(TripOccurrence).options(
    joinedload(TripOccurrence.template).joinedload(TripTemplate.company),
    joinedload(TripOccurrence.template).joinedload(TripTemplate.trip_type),
    joinedload(TripOccurrence.template).joinedload(TripTemplate.primary_country),
    joinedload(TripOccurrence.template).selectinload(TripTemplate.template_tags).joinedload(TripTemplateTag.tag),
    joinedload(TripOccurrence.guide),
).join(TripTemplate).filter(TripTemplate.is_active == True)
```

**Joins Performed**:
1. `TripOccurrence` → `TripTemplate` (INNER JOIN)
2. `TripTemplate` → `Company` (LEFT JOIN via joinedload)
3. `TripTemplate` → `TripType` (LEFT JOIN via joinedload)
4. `TripTemplate` → `Country` (LEFT JOIN via joinedload)
5. `TripTemplate` → `TripTemplateTag` → `Tag` (LEFT JOIN via selectinload)
6. `TripOccurrence` → `Guide` (LEFT JOIN via joinedload)

**Total Joins**: 6-7 joins per query

**Additional Filters Applied**:
- Geographic filters (countries/continents)
- Date filters (year/month/start_date)
- Status filters (exclude Cancelled/Full)
- Difficulty filter
- Budget filter
- Trip type filter

**Potential Issues**:
1. **No explicit indexes** on frequently filtered columns:
   - `TripOccurrence.start_date`
   - `TripOccurrence.status`
   - `TripOccurrence.spots_left`
   - `TripTemplate.is_active`
   - `TripTemplate.trip_type_id`
   - `TripTemplate.primary_country_id`
   - `TripTemplate.difficulty_level`
   - `TripOccurrence.effective_price`

2. **Cartesian product risk**: Multiple joinedloads can create large result sets

3. **N+1 query potential**: selectinload for tags is good, but could be optimized

**Mitigation Options**:
1. Add database indexes on filtered columns
2. Use `selectinload` instead of `joinedload` for one-to-many relationships
3. Limit initial query results before scoring
4. Use database views for common query patterns
5. Implement query result caching

**Current Status**:
- ✅ Using `selectinload` for tags (avoids cartesian product)
- ✅ Using `joinedload` for many-to-one relationships
- ❌ No explicit database indexes documented
- ❌ No query result caching

---

### 3. Python Scoring Algorithm (50-200ms)

**Location**: `backend/app/services/recommendation.py` → `calculate_trip_score()`

**Impact**: MEDIUM

**Process**:
1. Loads all candidate trips into memory
2. Iterates through each trip in Python
3. Calculates complex scoring for each trip:
   - Theme matching (set intersection)
   - Difficulty matching
   - Duration matching
   - Budget matching
   - Status bonuses
   - Geography bonuses
4. Sorts results by score

**Complexity**: O(n) where n = number of candidates

**Typical Candidate Count**: 50-500 trips

**Bottlenecks**:
1. **Python iteration**: Slower than database-level filtering
2. **Set operations**: Theme tag matching uses set intersections
3. **Multiple calculations per trip**: 6-8 scoring calculations per trip
4. **Sorting**: Python sort after scoring

**Mitigation Options**:
1. Move scoring logic to database (PostgreSQL functions)
2. Use database-level filtering before scoring
3. Limit candidates before scoring (e.g., top 100 by date)
4. Parallelize scoring (multiprocessing)
5. Cache scoring results for common queries

**Current Status**:
- ✅ Efficient set operations for theme matching
- ❌ All scoring in Python (not database)
- ❌ No candidate limiting before scoring
- ❌ No parallelization

---

### 4. Relaxed Search (100-500ms additional)

**Location**: `backend/app/services/recommendation.py` → `build_relaxed_query()`

**Impact**: MEDIUM (only when primary results < 6)

**Trigger**: When primary search returns fewer than 6 results

**Process**:
1. Builds a second query with relaxed filters:
   - Expanded date range (±2 months)
   - Expanded difficulty tolerance (±2 levels)
   - Expanded budget (50% over instead of 30%)
   - Expanded geography (same continent)
2. Fetches additional candidates
3. Scores all relaxed candidates
4. Adds top results to fill up to 10 total

**Additional Latency**: 100-500ms when triggered

**Mitigation Options**:
1. Run relaxed search in parallel with primary search
2. Cache relaxed results for common queries
3. Pre-compute relaxed candidates
4. Use database materialized views

**Current Status**:
- ❌ Runs sequentially after primary search
- ❌ No parallelization
- ❌ No caching

---

### 5. Response Serialization (10-50ms)

**Location**: `backend/app/api/v2/routes.py` → `format_occurrence_as_trip()`

**Impact**: LOW

**Process**:
- Converts SQLAlchemy objects to dictionaries
- Includes related objects (company, guide, country, etc.)
- Formats dates and prices

**Mitigation Options**:
1. Use faster serialization (e.g., orjson instead of json)
2. Reduce response payload size
3. Use response compression

**Current Status**:
- ✅ Standard JSON serialization
- ❌ No compression
- ❌ No optimized serialization library

---

## Performance Metrics by Component

| Component | Typical Time | Worst Case | Optimization Potential |
|-----------|--------------|------------|-------------------------|
| Network (Frontend→Backend) | 50-200ms | 300ms | Medium (CDN/Edge) |
| Network (Backend→Database) | 10-50ms | 150ms | Low (already optimized) |
| Database Query (Base) | 100-500ms | 1000ms | High (indexes) |
| Database Query (Filters) | 50-300ms | 800ms | High (indexes) |
| Python Scoring | 50-200ms | 500ms | Medium (DB functions) |
| Relaxed Search | 100-500ms | 1000ms | Medium (parallel) |
| Serialization | 10-50ms | 100ms | Low |
| **Total** | **500-2000ms** | **4000ms** | **High** |

---

## Recommended Optimizations (Priority Order)

### Priority 1: Database Indexes (High Impact, Low Effort)

**Estimated Improvement**: 30-50% reduction in query time

**Actions**:
1. Add indexes on frequently filtered columns:
   ```sql
   CREATE INDEX idx_trip_occurrence_start_date ON trip_occurrences(start_date);
   CREATE INDEX idx_trip_occurrence_status ON trip_occurrences(status);
   CREATE INDEX idx_trip_occurrence_spots_left ON trip_occurrences(spots_left);
   CREATE INDEX idx_trip_template_is_active ON trip_templates(is_active);
   CREATE INDEX idx_trip_template_trip_type_id ON trip_templates(trip_type_id);
   CREATE INDEX idx_trip_template_primary_country_id ON trip_templates(primary_country_id);
   CREATE INDEX idx_trip_template_difficulty_level ON trip_templates(difficulty_level);
   CREATE INDEX idx_trip_occurrence_effective_price ON trip_occurrences(effective_price);
   ```

2. Composite indexes for common filter combinations:
   ```sql
   CREATE INDEX idx_trip_occurrence_status_date ON trip_occurrences(status, start_date);
   CREATE INDEX idx_trip_template_active_type_country ON trip_templates(is_active, trip_type_id, primary_country_id);
   ```

### Priority 2: Query Optimization (High Impact, Medium Effort)

**Estimated Improvement**: 20-40% reduction in query time

**Actions**:
1. Limit candidates before scoring:
   ```python
   # In get_recommendations(), before scoring:
   candidates = query.limit(200).all()  # Limit to top 200 by date
   ```

2. Use database-level filtering where possible:
   - Move theme matching to database (array operations)
   - Use database functions for scoring

3. Optimize join strategy:
   - Review if all joins are necessary for initial filtering
   - Consider deferred loading for non-critical fields

### Priority 3: Backend Response Caching (Medium Impact, Medium Effort)

**Estimated Improvement**: 50-90% reduction for cached requests

**Actions**:
1. Implement Redis caching for common queries
2. Cache key: hash of search parameters
3. Cache TTL: 5-15 minutes
4. Invalidate on data updates

### Priority 4: Parallel Processing (Medium Impact, High Effort)

**Estimated Improvement**: 30-50% reduction when relaxed search triggers

**Actions**:
1. Run primary and relaxed searches in parallel
2. Use asyncio or threading for concurrent queries
3. Combine results after both complete

### Priority 5: Geographic Optimization (High Impact, High Effort)

**Estimated Improvement**: 100-200ms reduction for non-US users

**Actions**:
1. Deploy backend to multiple regions (US, EU, Asia)
2. Use CDN for static assets
3. Route users to nearest backend
4. Consider edge functions for simple queries

---

## Monitoring Recommendations

### Key Metrics to Track

1. **End-to-End Latency**:
   - P50 (median): Target < 1 second
   - P95: Target < 2 seconds
   - P99: Target < 3 seconds

2. **Database Query Time**:
   - Base query: Target < 300ms
   - Filtered query: Target < 200ms
   - Total DB time: Target < 500ms

3. **Scoring Time**:
   - Per trip: Target < 1ms
   - Total scoring: Target < 200ms

4. **Cache Hit Rate**:
   - Target > 60% for common queries

### Tools

1. **Backend Logging**: Add timing logs to each component
2. **Database Query Logging**: Enable slow query logging (> 500ms)
3. **APM Tool**: Use New Relic, Datadog, or similar
4. **Frontend Monitoring**: Track user-perceived latency

---

## Current Bottlenecks Summary

| Bottleneck | Impact | Effort to Fix | Priority |
|------------|--------|---------------|----------|
| Missing Database Indexes | HIGH | LOW | 1 |
| Geographic Latency | HIGH | HIGH | 5 |
| Complex Joins | MEDIUM | MEDIUM | 2 |
| Python Scoring | MEDIUM | MEDIUM | 2 |
| Sequential Relaxed Search | MEDIUM | HIGH | 4 |
| No Backend Caching | MEDIUM | MEDIUM | 3 |

---

## Quick Wins (Can Implement Today)

1. ✅ **Frontend Caching**: Already implemented for results page
2. ⚠️ **Add Database Indexes**: Run migration to add indexes
3. ⚠️ **Limit Candidates**: Add `.limit(200)` before scoring
4. ⚠️ **Add Timing Logs**: Log each component's execution time
5. ⚠️ **Enable Query Logging**: Log slow queries (> 500ms)

---

## Conclusion

The search latency is primarily caused by:
1. **Database query complexity** (6-7 joins, no indexes) - 30-40% of latency
2. **Geographic network latency** (US-based servers) - 20-30% of latency
3. **Python scoring algorithm** (processing all candidates) - 15-25% of latency
4. **Sequential relaxed search** (when triggered) - 10-20% of latency

**Recommended immediate actions**:
1. Add database indexes (30-50% improvement)
2. Limit candidates before scoring (20-30% improvement)
3. Implement backend caching (50-90% improvement for cached requests)

**Total potential improvement**: 50-70% reduction in search latency with Priority 1-3 optimizations.
