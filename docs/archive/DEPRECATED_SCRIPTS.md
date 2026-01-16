# Deprecated Scripts Archive

This folder contains archived scripts that are no longer used by the application.

## Archived Scripts

### `seed_from_csv.py`
- **Purpose**: Import database data from CSV files
- **Reason Archived**: CSV data is deprecated, app now uses Supabase directly
- **Status**: Deprecated - CSV files are archived in `data_archive/`
- **Replacement**: Use Supabase data directly, or `scripts/seed.py` for local dev

### `import_data.py`
- **Purpose**: Import all database tables from CSV files
- **Reason Archived**: CSV data is deprecated, app now uses Supabase directly
- **Status**: Deprecated - CSV files are archived in `data_archive/`
- **Replacement**: Use Supabase data directly, or `scripts/seed.py` for local dev

## Current Active Scripts

### `scripts/seed.py` ✅
- **Purpose**: Generate database data programmatically
- **Status**: Active - Used for local development with empty databases
- **Usage**: `python scripts/seed.py` or via `/api/seed` endpoint (dev only)

### `scripts/export_data.py` ✅
- **Purpose**: Export current Supabase data to CSV for backup/reference
- **Status**: Active - Useful for backups and data export
- **Usage**: `python scripts/export_data.py`

## Removed Endpoints

### `/api/migrate` (REMOVED)
- **Reason**: Depended on archived CSV files (`seed_from_csv.py`)
- **Replacement**: Not needed - use Supabase data directly

### `/api/seed` (MODIFIED)
- **Status**: Still active but **development-only**
- **Restriction**: Disabled in production (returns 403)
- **Usage**: Local development only
- **Replacement in Production**: Use Supabase data

## Migration Path

If you need to seed a local development database:

1. **Use Supabase data directly** (recommended for production)
2. **Use `scripts/seed.py`** for local dev with empty database
3. **Use `/api/seed` endpoint** (dev only, production returns 403)

**DO NOT** use CSV import scripts - they are deprecated and archived.

## Notes

- CSV data folder is archived in `data_archive/`
- CSV import scripts are archived in `docs/archive/`
- Production should always use Supabase data
- Local development can use programmatic seed (`seed.py`)

Date: 2024-01-15

