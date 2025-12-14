# Complete Database Reseeding Guide

## Overview

This guide walks you through the complete database schema cleanup and reseeding process with the new **TripType Foreign Key model** and strict **Type-to-Country geographical logic**.

---

## What's Changed

### 1. TripType Model (Foreign Key)
- Trip types are now stored in a dedicated `trip_types` table
- Each trip has a `trip_type_id` foreign key (not a many-to-many tag)
- This enforces that each trip has exactly ONE type

### 2. Theme Tags Only
- The `tags` table now contains **THEME tags only** (no more TYPE tags)
- "Cultural" and "Historical" combined into "Cultural & Historical"
- "Boutique Tours" removed

### 3. Geographical Logic
- Each trip type has a strict country mapping (e.g., "African Safari" only in African countries)
- Ensures realistic trips (no "Snowmobile Tours in Morocco")

### 4. Antarctica Added
- Antarctica is now a country (not just a continent)
- Supports trips like Geographic Cruises to Antarctica

---

## Step-by-Step Execution

### Step 1: Run Schema Cleanup Migration

```bash
cd backend
python migrate_clean_schema.py
```

**What This Does:**
- Drops `trips` and `trip_tags` tables
- Combines "Cultural" + "Historical" tags
- Deletes "Boutique Tours" tag
- Reorders theme tags starting from ID=1
- Adds Antarctica as a country
- Recreates empty `trips` and `trip_tags` tables

**Expected Output:**
```
[STEP 1] Dropping trips and trip_tags tables...
✓ Dropped trips and trip_tags tables

[STEP 2] Combining Cultural and Historical tags...
✓ Combined tags into 'Cultural & Historical' (ID=1)

[STEP 3] Deleting 'Boutique Tours' tag...
✓ Deleted 'Boutique Tours' tag

[STEP 4] Reordering theme tags from ID=1...
✓ Reordered 10 theme tags:
   ID 1: Cultural & Historical (תרבות והיסטוריה)
   ID 2: Wildlife (חיות בר)
   ...

[STEP 5] Adding Antarctica as a country...
✓ Added Antarctica (ID=108)

[STEP 6] Recreating trips and trip_tags tables...
✓ Recreated trips and trip_tags tables (empty)

✅ Final State:
   - Theme Tags: 10
   - Countries: 108
   - Trips: 0

✅ Ready for new seeding with TripType logic!
```

---

### Step 2: Run New Seed Script

```bash
python seed.py
```

**What This Does:**
- Seeds all countries (108 total, including Antarctica)
- Seeds 10 Trip Types in `trip_types` table (Foreign Key model)
- Seeds 10 Theme Tags in `tags` table (THEME only)
- Seeds 25 guides
- Generates 100-150 trips using:
  - **Phase 1:** At least 10 trips per TripType (following geographical logic)
  - **Phase 2:** At least 1 trip per Country
  - **Phase 3:** Saves all trips with theme tags

**Expected Output:**
```
📍 Seeding countries...
✓ Seeded 108 countries (including Antarctica)

🎯 Seeding Trip Types (Foreign Key Model)...
✓ Seeded 10 Trip Types (Foreign Key)

🏷️  Seeding Theme Tags (THEME Category Only)...
✓ Seeded 10 Theme Tags

👨‍🏫 Seeding guides...
✓ Seeded 25 guides

🌍 Generating trips with TripType-Country logic...

PHASE 1: Generating trips by TripType (min 10 per type)...
  🎯 Geographic Depth: Generating 12 trips...
  🎯 African Safari: Generating 11 trips...
  🎯 Snowmobile Tours: Generating 10 trips...
  ...

✓ Phase 1 Complete: 110 trips generated

PHASE 2: Ensuring every country has at least 1 trip...
  📍 Added trip for Malta (Nature Hiking)
  📍 Added trip for Estonia (Geographic Depth)
  ...

✓ Phase 2 Complete: 40 countries filled

PHASE 3: Saving trips to database...
  ... 50 trips saved
  ... 100 trips saved
  ... 150 trips saved

✓ Saved 150 trips to database

📊 Final Statistics:
   - Countries: 108
   - Trip Types: 10
   - Theme Tags: 10
   - Guides: 25
   - Trips: 150

🎯 Trips per Type:
   - Geographic Depth: 15 trips
   - African Safari: 11 trips
   - Snowmobile Tours: 10 trips
   ...

✅ All countries have at least 1 trip!
✅ Database ready for production!
```

---

## Type-to-Country Logic Map

```python
TYPE_TO_COUNTRY_LOGIC = {
    "Geographic Depth": "ALL",  # Can go anywhere
    "African Safari": ["Kenya", "Tanzania", "South Africa", "Namibia", ...],
    "Snowmobile Tours": ["Iceland", "Lapland", "Norway", "Canada", ...],
    "Jeep Tours": ["Jordan", "Morocco", "Namibia", "Kyrgyzstan", ...],
    "Train Tours": ["Switzerland", "Japan", "India", "Russia", ...],
    "Geographic Cruises": ["Antarctica", "Norway", "Vietnam", ...],
    "Nature Hiking": "ALL",
    "Carnivals & Festivals": ["Brazil", "Bolivia", "Peru", "Spain", ...],
    "Photography": "ALL",
    "Private Groups": "ALL",
}
```

---

## Verification

### Check TripTypes Table
```bash
psql $DATABASE_URL -c "SELECT id, name, name_he FROM trip_types ORDER BY id;"
```

### Check Theme Tags
```bash
psql $DATABASE_URL -c "SELECT id, name, name_he, category FROM tags WHERE category='Theme' ORDER BY id;"
```

### Check Trips with Types
```bash
psql $DATABASE_URL -c "SELECT t.id, t.title_he, tt.name as type, c.name as country FROM trips t JOIN trip_types tt ON t.trip_type_id = tt.id JOIN countries c ON t.country_id = c.id LIMIT 10;"
```

### Test API Endpoints
```bash
# Get trip types
curl http://localhost:5000/api/trip-types

# Get theme tags
curl http://localhost:5000/api/tags

# Get trips
curl http://localhost:5000/api/trips?limit=10
```

---

## Troubleshooting

### Migration Fails at Step 1
**Problem:** `trips` or `trip_tags` table doesn't exist

**Solution:** Already handled - migration uses `DROP TABLE IF EXISTS`

---

### Seed Fails: "No valid countries for X"
**Problem:** TYPE_TO_COUNTRY_LOGIC references countries that don't exist in DB

**Solution:** Check that all country names in `TYPE_TO_COUNTRY_LOGIC` match the `countries_data` list

---

### Frontend Shows Empty Type Dropdown
**Problem:** Frontend still calling `/api/tags` for types

**Solution:** Update frontend to call `/api/trip-types` instead

---

## Next Steps

1. ✅ Run `migrate_clean_schema.py`
2. ✅ Run `seed.py`
3. Update frontend to use `/api/trip-types` endpoint
4. Update recommendation logic to use `trip_type_id` as hard filter
5. Test search and recommendations

---

## Rollback (If Needed)

If you need to start over:

```bash
cd backend
python migrate_types.py  # Run old migration
python seed.py           # Run old seed
```

**Note:** This will restore the old tag-based TYPE system.

---

## Summary of Files Changed

- `backend/models.py` - Added `TripType` model, updated `Trip.type` relationship
- `backend/app.py` - Added `/api/trip-types` endpoint, updated recommendation logic
- `backend/migrate_clean_schema.py` - **NEW** - Schema cleanup migration
- `backend/seed.py` - **REWRITTEN** - New seeding logic with TripType FK
- `src/app/search/page.tsx` - Updated to fetch `/api/trip-types`
- `src/app/search/results/page.tsx` - Updated to send `preferred_trip_type_id`

---

**You're ready to reseed!** Run the migration first, then the seed script.

