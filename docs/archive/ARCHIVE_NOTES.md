# Archive Notes - Data Folder and Auto-Seed

## Changes Made

### 1. Removed Auto-Seed Functionality
- **Removed**: `auto_seed_if_empty()` function from `app.py`
- **Removed**: Auto-seed call from app initialization
- **Reason**: Prevents automatic seeding on startup that could conflict with Supabase data

### 2. Archived CSV Data Folder
- **Archived**: `backend/data/` → `backend/docs/archive/data_archive/`
- **Reason**: CSV files caused data duplication and mismatches with Supabase data
- **Status**: CSV files are deprecated, app uses Supabase directly

### 3. Endpoints Updated/Removed
- **`/api/seed`**: Still active but **restricted to development only** (disabled in production)
- **`/api/migrate`**: **REMOVED** (depended on deprecated CSV files)

## Current Data Source

The application now uses data **directly from Supabase**:
- All queries read from Supabase PostgreSQL database
- V2 schema tables: `trip_templates`, `trip_occurrences`, etc.
- No CSV file usage at runtime

## Scripts Status

Scripts Status:
- ✅ `scripts/seed.py` - **ACTIVE** - Generates data programmatically (for local dev)
- ✅ `scripts/export_data.py` - **ACTIVE** - Exports Supabase data to CSV (for backups)
- 🗄️ `seed_from_csv.py` - **ARCHIVED** to `docs/archive/` (deprecated, uses CSV)
- 🗄️ `import_data.py` - **ARCHIVED** to `docs/archive/` (deprecated, uses CSV)

**Note**: These scripts are utility tools, not used by the main application.

## Impact

- ✅ No automatic seeding on app startup
- ✅ No data conflicts with Supabase
- ✅ Clear data source (Supabase only)
- ✅ `/api/migrate` endpoint removed (was using deprecated CSV)
- ✅ `/api/seed` restricted to development only (production returns 403)
- ✅ CSV import scripts archived

## Summary

All deprecated functionality has been cleaned up:
- ✅ Auto-seed removed
- ✅ `/api/migrate` endpoint removed
- ✅ `/api/seed` restricted to development only
- ✅ CSV import scripts archived
- ✅ CSV data folder archived

The application now exclusively uses Supabase data in production, with optional programmatic seeding for local development only.

Date: 2024-01-15

