# Archived Recommendation Module

This directory contains the original monolithic `recommendation.py` file that was split into the modular package structure.

**Archive Date:** January 15, 2026

**Original Location:** `backend/app/services/recommendation.py`

**New Location:** `backend/app/services/recommendation/` (package)

**Reason for Archive:**
The original 1244-line monolithic file was refactored into a modular package structure following Single Responsibility Principle:
- `constants.py` - Configuration
- `context.py` - Preference processing
- `filters.py` - Query building
- `scoring.py` - Scoring functions
- `relaxed_search.py` - Relaxed search logic
- `engine.py` - Main orchestration

**Status:** This file is archived and no longer in use. The package structure is now active.

**If you need to reference the old implementation:**
- Check the git history for the original file
- All functionality has been preserved in the new package structure
- See `backend/app/services/recommendation/README.md` for current documentation
