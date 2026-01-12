# Backend Utility Scripts

Diagnostic, verification, and analysis scripts for the SmartTrip database.

## Usage

Run all scripts from the `backend` folder:

```bash
cd backend

# Database Verification
python scripts/check_guaranteed_trips.py   # Check trip status distribution
python scripts/check_types.py              # List all trip types with counts
python scripts/verify_names.py             # Verify frontend/backend name consistency
python scripts/verify_schema.py            # Comprehensive schema verification
python scripts/verify_seed.py              # Quick check after seeding

# Scoring Analysis
python scripts/analyze_scoring_v2.py       # Enhanced scoring analysis with insights
```

## Script Descriptions

### Database Verification

| Script | Purpose |
|--------|---------|
| `check_guaranteed_trips.py` | Shows distribution of trip statuses |
| `check_types.py` | Lists all trip types with trip counts and sample countries |
| `verify_names.py` | Verifies trip type names match between frontend and backend |
| `verify_schema.py` | Comprehensive schema verification (types, tags, countries, geography logic) |
| `verify_seed.py` | Quick verification of seeded data counts |

### Scoring Analysis

| Script | Purpose |
|--------|---------|
| `analyze_scoring_v2.py` | Enhanced analysis with recommendations for weight tuning |
