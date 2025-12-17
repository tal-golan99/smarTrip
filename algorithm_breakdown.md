## SmartTrip Recommendation Engine (V2) — Algorithm Breakdown

### Where the algorithm lives
- **Endpoint**: `POST /api/v2/recommendations`
- **Handler**: `get_recommendations_v2()` in `backend/api_v2.py`
- **Shared config/constants (imported by V2)**: `SCORING_WEIGHTS`, `SCORE_THRESHOLDS`, `RecommendationConfig` from `backend/app.py`
- **Core entities used**:
  - `TripTemplate` (“what”: title, base price, difficulty, company, tags)
  - `TripOccurrence` (“when”: dates, status, availability, price overrides)
  - `TripOccurrence.effective_price` (hybrid property used for DB‑level budget filtering)

---

## 1) Input variables
`get_recommendations_v2()` reads a JSON body (`prefs = request.get_json(...)`) with keys:

- **Geography**
  - `selected_countries: number[]`
  - `selected_continents: string[]` (mapped to DB enum names via `continent_mapping`)

- **Trip style vs interests**
  - `preferred_type_id: number | null` (hard filter on `TripTemplate.trip_type_id`)
  - `preferred_theme_ids: number[]` (soft scoring via template tag overlap)

- **Constraints**
  - `min_duration: number`
  - `max_duration: number`
  - `budget: number | null` (filters by `effective_price <= budget * RecommendationConfig.BUDGET_MAX_MULTIPLIER`)
  - `difficulty: number | null` (filters by `difficulty_level` within `RecommendationConfig.DIFFICULTY_TOLERANCE`)

- **Time window**
  - `year: string | number | 'all'`
  - `month: string | number | 'all'`
  - `start_date: string | null` (legacy support; ISO date)

---

## 2) Logic flow (step-by-step)

### Step A — Normalize inputs
- Parse `prefs` fields.
- Convert `selected_continents` into DB enum keys (e.g., `'North America' -> 'NORTH_AND_CENTRAL_AMERICA'`).
- Determine if search is for **Private Groups** (`TripType.name == 'Private Groups'`) to relax date/availability constraints.

### Step B — Build the strict candidate query (hard filters)
The strict query is built on `TripOccurrence` joined to `TripTemplate`:
- **Active templates**: `TripTemplate.is_active == True`
- **Exclude unavailable**: `TripOccurrence.status.notin_(['Cancelled', 'Full'])`
- **Availability (non-private)**: `TripOccurrence.spots_left > 0`
- **Future departures (non-private)**: `TripOccurrence.start_date >= today`
- **Trip type (if provided)**: `TripTemplate.trip_type_id == preferred_type_id`
- **Difficulty band (if provided)**: `TripTemplate.difficulty_level.between(difficulty - RecommendationConfig.DIFFICULTY_TOLERANCE, difficulty + RecommendationConfig.DIFFICULTY_TOLERANCE)`
- **Budget cap (if provided)**: `TripOccurrence.effective_price <= budget * RecommendationConfig.BUDGET_MAX_MULTIPLIER`
- **Geography**:
  - country filter via `TripTemplate.primary_country_id.in_(selected_countries)`
  - continent filter via joining `Country` and applying `Country.continent.in_(selected_continents_enum)`
  - combined with OR (union behavior) when both are provided
- **Year/month**:
  - `extract('year', TripOccurrence.start_date) == int(selected_year)`
  - `extract('month', TripOccurrence.start_date) == int(selected_month)`
- **Legacy start date** (only if `year` is not used): `TripOccurrence.start_date >= user_start_date`

### Step C — Score each candidate (strict pass)
For each candidate occurrence `occ`:
- Start from `current_score = SCORING_WEIGHTS['BASE_SCORE']`.
- Compute and append human-readable reasons into `match_details`.
- Clamp at the end: `final_score = max(0.0, min(100.0, current_score))`.
- Serialize as a legacy-friendly trip shape via `format_occurrence_as_trip(occ, include_relations=True)`.

### Step D — Sort and select primary results
- Sort by:
  - descending `_float_score`
  - ascending `_sort_date` (start date)

```text
sort_key = (-_float_score, _sort_date)
```

- Take the top `RecommendationConfig.MAX_RESULTS`.

### Step E — Relaxed fallback (if strict results are too few)
If `len(top_trips) < RecommendationConfig.MIN_RESULTS_THRESHOLD`:
- Build a relaxed query similar to strict, but with expanded constraints:
  - **Geography expansion**: if a country was selected, expand to its continent(s)
  - **Trip type removed as a filter**: do not filter by type; apply a penalty later if types differ
  - **Date expansion**: if year/month provided, expand by ±2 months using `relativedelta`
  - **Difficulty expansion**: tolerance widened to `RELAXED_DIFFICULTY_TOLERANCE = 2`
  - **Budget expansion**: multiplier raised to `RELAXED_BUDGET_MULTIPLIER = 1.5`
- Score relaxed candidates similarly, but with:
  - baseline penalty: `SCORING_WEIGHTS['RELAXED_PENALTY']` (default `-20`)
  - extra penalty for different type: `-10.0` when `template.trip_type_id != preferred_type_id`
- Add only as many relaxed results as needed to reach `MAX_RESULTS`.

---

## 3) Mathematical / logical model

### Hard-filter phase
A trip occurrence is eligible if it passes all enabled constraints:

- **Status constraint**: `status ∉ {'Cancelled','Full'}`
- **Future constraint**: `start_date ≥ today` (unless private groups)
- **Availability constraint**: `spots_left > 0` (unless private groups)
- **Budget constraint** (optional):

\[
\text{effective\_price} \le \text{budget} \times \text{BUDGET\_MAX\_MULTIPLIER}
\]

- **Difficulty constraint** (optional):

\[
|difficulty\_level - difficulty| \le \text{DIFFICULTY\_TOLERANCE}
\]

### Scoring phase (strict)
Let `S` start at `BASE_SCORE` and add/subtract weights from `SCORING_WEIGHTS`:

- **Themes** (based on overlap of `preferred_theme_ids` with `template.template_tags`)
  - `THEME_FULL` when matches ≥ `RecommendationConfig.THEME_MATCH_THRESHOLD`
  - `THEME_PARTIAL` when matches == 1
  - `THEME_PENALTY` when matches == 0

- **Difficulty**
  - add `DIFFICULTY_PERFECT` when exact match

- **Duration**
  - add `DURATION_IDEAL` when `min_duration ≤ duration_days ≤ max_duration`
  - add `DURATION_GOOD` when within `RecommendationConfig.DURATION_GOOD_DAYS`
  - skip candidate if outside `RecommendationConfig.DURATION_HARD_FILTER_DAYS`

- **Budget**
  - add `BUDGET_PERFECT` if `effective_price ≤ budget`
  - add `BUDGET_GOOD` if `effective_price ≤ budget * 1.1`
  - add `BUDGET_ACCEPTABLE` if `effective_price ≤ budget * 1.2`

- **Status / urgency**
  - add `STATUS_GUARANTEED` when `status == 'Guaranteed'`
  - add `STATUS_LAST_PLACES` when `status == 'Last Places'`
  - add `DEPARTING_SOON` when days to departure ≤ `RecommendationConfig.DEPARTING_SOON_DAYS`

- **Geography**
  - add `GEO_DIRECT_COUNTRY` on direct country match (or Antarctica special case)
  - add `GEO_CONTINENT` on continent match

Finally:

\[
\text{match\_score} = \text{clamp}_{0..100}(S)
\]

### Relaxed scoring
Relaxed results start lower:

\[
S_{relaxed} = BASE\_SCORE + RELAXED\_PENALTY
\]

and can additionally include:

\[
S_{relaxed} = S_{relaxed} - 10 \quad \text{if trip type differs}
\]

---

## 4) Output
The endpoint returns JSON shaped for the frontend results page (`src/app/search/results/page.tsx`):

- `success: boolean`
- `data: list` of “trip-like” objects produced by `format_occurrence_as_trip()` with extra recommendation fields:
  - `match_score: number`
  - `match_details: string[]`
  - `is_relaxed: boolean`
- `primary_count`, `relaxed_count`, `has_relaxed_results`
- `score_thresholds` (from `SCORE_THRESHOLDS`)
- `show_refinement_message` (based on the top result vs `SCORE_THRESHOLDS['HIGH']`)
- `request_id` (when logging is enabled)
- `api_version: 'v2'`

This structure enables the UI to render:
- a ranked list,
- score color-coding,
- “expanded results” separator when relaxed results are present,
- and user-facing explanation strings.
