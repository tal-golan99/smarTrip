# Backend Utility Scripts

Diagnostic and verification scripts for the SmartTrip database.

## Usage

Run all scripts from the `backend` folder:

```bash
cd backend

# Check trip status distribution (OPEN, GUARANTEED, etc.)
python scripts/check_guaranteed_trips.py

# List all trip types with counts
python scripts/check_types.py

# Verify frontend/backend name consistency
python scripts/verify_names.py

# Comprehensive schema verification
python scripts/verify_schema.py

# Quick check after seeding
python scripts/verify_seed.py
```

## Script Descriptions

| Script | Purpose |
|--------|---------|
| `check_guaranteed_trips.py` | Shows distribution of trip statuses |
| `check_types.py` | Lists all trip types with trip counts and sample countries |
| `verify_names.py` | Verifies trip type names match between frontend and backend |
| `verify_schema.py` | Comprehensive schema verification (types, tags, countries, geography logic) |
| `verify_seed.py` | Quick verification of seeded data counts |
