# Data Archive

This folder contains archived CSV files that were previously used for database seeding.

## Why Archived?

- **Data Source**: The application now uses data directly from Supabase (PostgreSQL database)
- **Prevents Duplication**: CSV files caused data mismatches and duplication issues
- **V2 Schema**: These CSV files contain V1 schema data (trips.csv) which is deprecated
- **Production**: Production environment should use Supabase data, not CSV files

## Files

- `countries.csv` - Country data (still used by seed scripts if needed)
- `guides.csv` - Guide information
- `tags.csv` - Theme tags
- `trip_types.csv` - Trip type categories
- `trips.csv` - **DEPRECATED V1 schema** - Use TripTemplate/TripOccurrence in Supabase
- `trip_tags.csv` - **DEPRECATED V1 schema** - Use trip_template_tags in Supabase

## Usage

**DO NOT USE** these files in production. They are archived for historical reference only.

If you need to seed a local development database:
1. Use `scripts/seed.py` (generates data programmatically)
2. Or update scripts to use Supabase data
3. Do NOT import from these archived CSV files in production

## Migration Notes

The app reads all data from Supabase using the V2 schema:
- `trip_templates` - Trip descriptions, pricing, difficulty
- `trip_occurrences` - Trip dates, availability, guides
- All other data comes directly from Supabase tables

## Auto-Seed Removal

Auto-seed functionality has been removed from `app.py` to prevent:
- Automatic seeding on startup
- Data duplication issues
- Conflicts with Supabase data

Archived: 2024-01-15

