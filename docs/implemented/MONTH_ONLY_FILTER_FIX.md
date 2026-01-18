# Fix: Month-Only Filter Not Working

## Issue

When users filtered trips by selecting ONLY a month (without selecting a year), the search algorithm was not applying the month filter at all. The month filter only worked when a year was also selected.

**Example of the bug:**
- User selects "July" (no year selected)
- Expected: Show all trips in July across all available years
- Actual: Month filter was ignored, showing trips from all months

## Root Cause

The month filter logic was **nested inside** the year filter condition in both the primary and relaxed search algorithms:

```python
# BEFORE (broken logic)
if selected_year and selected_year != 'all':
    query = query.filter(extract('year', TripOccurrence.start_date) == int(selected_year))
    if selected_month and selected_month != 'all':  # ← Only checked if year is selected!
        query = query.filter(extract('month', TripOccurrence.start_date) == int(selected_month))
```

This meant the month filter would only be evaluated when a year was selected, making it impossible to filter by month alone.

## Solution

Made the month filter **independent** of the year filter, so both can work separately or together.

### Primary Search (filters.py)

```python
# AFTER (fixed logic)
# Apply year filter if selected
if selected_year and selected_year != 'all':
    query = query.filter(extract('year', TripOccurrence.start_date) == int(selected_year))

# Apply month filter if selected (independent of year selection)
if selected_month and selected_month != 'all':
    query = query.filter(extract('month', TripOccurrence.start_date) == int(selected_month))
```

### Relaxed Search (relaxed_search.py)

For relaxed search, added a new `elif` branch to handle month-only filtering with the 2-month expansion:

```python
# AFTER (fixed logic)
if selected_year and selected_year != 'all':
    # Handle year with or without month
    # ... existing year logic ...
elif selected_month and selected_month != 'all':
    # NEW: Handle month-only filter
    month_int = int(selected_month)
    
    # Expand by 2 months before and after
    target_months = []
    for offset in [-2, -1, 0, 1, 2]:
        target_month = (month_int + offset - 1) % 12 + 1
        target_months.append(target_month)
    
    relaxed_query = relaxed_query.filter(
        extract('month', TripOccurrence.start_date).in_(target_months)
    )
```

## Changes Made

### File: `backend/app/services/recommendation/filters.py`

**Lines 81-87** - Made month filter independent of year filter:
- Separated the year filter and month filter into two independent `if` statements
- Month filter now applies regardless of whether a year is selected

### File: `backend/app/services/recommendation/relaxed_search.py`

**Lines 98-149** - Added month-only handling for relaxed search:
- Restructured the date filter logic to handle three cases:
  1. Year + Month: Expand by 2 months around the specific month in that year
  2. Year only: Expand by 2 months before/after the entire year
  3. **Month only (NEW)**: Filter by the month +/- 2 months across all valid years

## Filter Behavior After Fix

### Scenario 1: Month Only
**User Selection:** Month = "July" (no year)

**Primary Search:**
- Shows all trips in July across current year + next N years
- Example: July 2026, July 2027, etc.

**Relaxed Search:**
- Shows trips in May, June, July, August, September across all valid years
- Expands by 2 months before and after

### Scenario 2: Year Only
**User Selection:** Year = "2026" (no month)

**Primary Search:**
- Shows all trips in 2026

**Relaxed Search:**
- Shows trips from Nov 2025 to Feb 2027 (2 months before/after)

### Scenario 3: Year + Month
**User Selection:** Year = "2026", Month = "July"

**Primary Search:**
- Shows trips in July 2026 only

**Relaxed Search:**
- Shows trips from May 2026 to September 2026 (2 months before/after)

### Scenario 4: No Year, No Month
**User Selection:** All dates

**Primary Search:**
- Shows all trips from today onwards (up to current year + N years)

**Relaxed Search:**
- Same as primary

## Technical Details

### SQL Query Impact

**Before (month filter ignored):**
```sql
-- When user selects only month = 7
SELECT * FROM trip_occurrences
WHERE start_date >= '2026-01-18'
  AND EXTRACT(year FROM start_date) <= 2027
-- No month filter applied!
```

**After (month filter works):**
```sql
-- When user selects only month = 7
SELECT * FROM trip_occurrences
WHERE start_date >= '2026-01-18'
  AND EXTRACT(year FROM start_date) <= 2027
  AND EXTRACT(month FROM start_date) = 7
-- Month filter now applied!
```

### Edge Cases Handled

1. **Month wrap-around in relaxed search:**
   - Selected month: January (1)
   - Expanded months: November (11), December (12), January (1), February (2), March (3)
   - Uses modulo arithmetic: `(month_int + offset - 1) % 12 + 1`

2. **Year boundaries:**
   - Month filter works across year boundaries
   - Example: Filtering by December shows December in both 2026 and 2027

3. **Invalid values:**
   - Try-except blocks catch ValueError/TypeError for invalid month/year values
   - Falls back to basic date filtering (>= today)

## Testing

To verify the fix:

1. **Test Month-Only Filter:**
   - Go to search page
   - Select only a month (e.g., "July")
   - Do NOT select a year
   - Click search
   - Verify results show trips in July across multiple years

2. **Test Year-Only Filter:**
   - Select only a year (e.g., "2026")
   - Do NOT select a month
   - Verify results show trips across all months in 2026

3. **Test Year + Month Filter:**
   - Select both year and month
   - Verify results show trips in that specific month and year

4. **Test No Filters:**
   - Leave both year and month as "all"
   - Verify results show all available trips

## Related Files

- `backend/app/services/recommendation/filters.py` - Primary search filtering
- `backend/app/services/recommendation/relaxed_search.py` - Relaxed search filtering
- `backend/app/api/recommendations.py` - API endpoint that calls these functions

## Impact

This fix ensures that users can:
- ✅ Filter by month alone (e.g., "show me all July trips")
- ✅ Filter by year alone (e.g., "show me all 2026 trips")
- ✅ Filter by both (e.g., "show me July 2026 trips")
- ✅ Use no date filters (e.g., "show me all trips")

All combinations now work as expected!
