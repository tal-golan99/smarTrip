# Models V1 Archive

## File: `models_v1.py` (formerly `backend/models.py`)

This file contains the **deprecated V1 database schema** that has been replaced by V2.

## Why Archived?

- **Replaced by V2 Schema**: The application now uses `models_v2.py` with the new schema
- **V1 Schema Deprecated**: V1 used a single `Trip` model, V2 uses `TripTemplate` and `TripOccurrence`
- **No Active Usage**: No code in the backend imports from this file anymore

## V1 vs V2 Schema

### V1 Schema (Deprecated)
- Single `Trip` model with all trip information
- `TripTag` junction table
- Direct relationships between trips and countries/guides

### V2 Schema (Active)
- `TripTemplate` - The "what" of a trip (description, pricing, difficulty)
- `TripOccurrence` - The "when" of a trip (dates, guide, availability)
- `TripTemplateTag` - Junction table for templates and tags
- `TripTemplateCountry` - Junction table for templates and countries

## Migration

All code now uses `models_v2.py`:
- `app.py` imports from `models_v2`
- `api_v2.py` imports from `models_v2`
- `database.py` uses `models_v2.Base`
- All scripts use `models_v2` models

## Current Models (V2)

The active models are in `backend/models_v2.py`:
- `TripTemplate` - Trip descriptions and configurations
- `TripOccurrence` - Individual trip dates and availability
- `Country`, `Guide`, `Tag`, `TripType` - Shared entities
- `Company` - Trip provider companies
- `TripTemplateTag`, `TripTemplateCountry` - Junction tables

Archived: 2024-01-15

