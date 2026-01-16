# V2 Schema Migration Plan - Complete Transition

## Executive Summary

**Goal:** Fully migrate from V1 schema (`models.py`) to V2 schema (`models_v2.py`) and remove all deprecated V1 endpoints.

**Current Status:**
- ✅ **Frontend**: Fully migrated to `/api/v2/*` endpoints (100% V2)
- ✅ **API V2**: `api_v2.py` fully uses `models_v2.py` (complete implementation)
- ✅ **Database**: `database.py` already uses V2 Base (from `models_v2`)
- ⚠️ **app.py**: Contains 3 deprecated V1 endpoints that reference non-existent `Trip` model
- ⚠️ **Scripts**: 12 scripts still use V1 models (can be migrated later)

**Risk Level:** **LOW** - Frontend already uses V2, V1 endpoints are broken (reference `Trip` which isn't imported)

---

## Phase 1: Pre-Migration Verification ✅

### 1.1 Frontend Verification
- [x] Frontend uses `/api/v2/*` exclusively
- [x] No references to `/api/trips` or `/api/recommendations` in frontend
- [x] All API calls use `API_VERSION = '/api/v2'` in `src/lib/api.ts`

### 1.2 Database Schema Status
- [x] `database.py` uses `from models_v2 import Base` (already migrated)
- [ ] **Action Needed**: Verify V2 tables exist in production database
- [ ] **Action Needed**: Confirm V1 `trips` table is legacy (or doesn't exist)

### 1.3 External Dependencies
- [x] No external services use V1 endpoints (frontend is only consumer)
- [x] V1 endpoints are marked as deprecated

---

## Phase 2: Remove Deprecated V1 Endpoints (SAFE - Execute Now)

### 2.1 Current Problem
The V1 endpoints in `app.py` reference `Trip` and `TripTag` models that are **not imported**:
- Line 13: Only imports V2 models (`TripOccurrence`, `TripTemplate`)
- Lines 583, 611, 617, 654, 878, 891, etc.: Reference `Trip` (doesn't exist)
- Line 894: References `TripTag` (doesn't exist)

**Result**: These endpoints would crash if called (NameError: name 'Trip' is not defined)

### 2.2 Endpoints to Remove

1. **`GET /api/trips`** (lines ~556-643)
   - **Status**: Broken (missing `@app.route` decorator, references `Trip`)
   - **Replacement**: `GET /api/v2/trips` (working in `api_v2.py`)

2. **`GET /api/trips/<id>`** (lines ~646-675)
   - **Status**: Broken (references `Trip`)
   - **Replacement**: `GET /api/v2/trips/<id>` (working in `api_v2.py`)

3. **`POST /api/recommendations`** (lines ~684-1520)
   - **Status**: Broken (references `Trip`, `TripTag`, `TripStatus`)
   - **Replacement**: `POST /api/v2/recommendations` (working in `api_v2.py`)

### 2.3 Safe Removal Steps

**Step 1**: Remove the three V1 endpoint functions
- Delete lines ~556-643 (GET /api/trips)
- Delete lines ~646-675 (GET /api/trips/<id>)
- Delete lines ~678-1520 (POST /api/recommendations)

**Step 2**: Remove `add_deprecation_headers()` helper (if it exists)
- This function is only used by V1 endpoints

**Step 3**: Update section comments
- Replace "V1 ENDPOINTS REMOVED" comment with clear note about V2-only status

---

## Phase 3: Update Health Check & Seed Endpoints

### 3.1 Health Check Endpoint
**Current**: Uses V1 `Trip` model (line 198, 234, 264)
**Action**: Already updated to use V2 models (from attached files) ✅

### 3.2 Seed Endpoints
**Current**: Reference `Trip` model (lines 234, 264)
**Action**: Update to use V2 models (`TripOccurrence`, `TripTemplate`)

---

## Phase 4: Script Migration (Optional - Can Do Later)

### 4.1 Critical Scripts (High Priority)
These scripts are used for database management:

1. **`seed.py`** - Uses V1 `Trip` model
2. **`seed_from_csv.py`** - Uses V1 `Trip` model
3. **`generate_trips.py`** - Uses V1 models

**Action**: Migrate to V2 OR mark as "legacy - use V2 scripts"

### 4.2 Utility Scripts (Low Priority)
- `verify_schema.py`, `verify_seed.py`, `check_guaranteed_trips.py`, etc.
- **Action**: Can migrate later or archive to `docs/archive/scripts/`

---

## Phase 5: Database Initialization Verification

### 5.1 Current Status
- ✅ `database.py` uses `from models_v2 import Base`
- ✅ `init_db()` creates V2 tables

### 5.2 Verification Needed
- [ ] Test `init_db()` on fresh database
- [ ] Verify all V2 tables are created:
  - `companies`
  - `trip_templates`
  - `trip_occurrences`
  - `trip_template_tags`
  - `trip_template_countries`
  - `price_history`
  - `reviews`

---

## Execution Plan

### Immediate Actions (Safe - Execute Now)

1. **Remove V1 Endpoints from `app.py`**
   - Delete broken V1 endpoint functions
   - Clean up imports (already done ✅)
   - Update comments

2. **Fix Seed Endpoints**
   - Update `/api/seed` to use V2 models
   - Update `/api/migrate` to use V2 models

3. **Verify Database**
   - Test that V2 tables are created correctly

### Future Actions (Can Do Later)

4. **Migrate Scripts**
   - Update `seed.py` and `seed_from_csv.py` to V2
   - Or create V2 versions of these scripts

5. **Archive Legacy Code**
   - Move `models.py` to `docs/archive/` (keep for reference)
   - Archive V1-only scripts

---

## Risk Assessment

### ✅ Low Risk (Safe to Execute)
- **Removing V1 Endpoints**: Frontend doesn't use them, endpoints are already broken
- **Database**: Already using V2 Base, just need verification
- **Health Check**: Already updated to V2 models

### ⚠️ Medium Risk (Needs Testing)
- **Seed Scripts**: May break if they're used for database initialization
- **Script Migration**: Scripts may have dependencies on V1 models

### Mitigation
- Keep V1 code in git history (can revert if needed)
- Test database initialization after changes
- Scripts can be migrated incrementally

---

## Rollback Plan

If issues occur:
1. Revert `app.py` changes (restore V1 endpoints)
2. Revert `database.py` if needed (but it's already correct)
3. V1 models file (`models.py`) remains intact for reference

---

## Success Criteria

✅ Migration is successful when:
1. All V1 endpoints removed from `app.py`
2. Health check uses V2 models
3. Seed endpoints use V2 models
4. Database initialization creates V2 tables
5. Frontend continues to work (uses V2 endpoints)
6. No broken imports or NameError exceptions

---

## Timeline

- **Phase 2 (Remove V1 Endpoints)**: 15-30 minutes
- **Phase 3 (Fix Seed Endpoints)**: 10-15 minutes
- **Phase 4 (Script Migration)**: 4-6 hours (can do later)
- **Phase 5 (Verification)**: 30 minutes

**Total Immediate Work**: ~1 hour
**Total Complete Migration**: ~6-8 hours (including scripts)

---

## Notes

- **Shared Enums**: `TripStatus`, `Gender`, `Continent` exist in both `models.py` and `models_v2.py` - import from V2
- **Backward Compatibility**: V1 endpoints are already broken (missing imports), so removal is safe
- **Data Migration**: If V1 `trips` table has data, it may need migration to V2 format (separate task)

---

**Last Updated:** 2025-12-14
**Status:** Ready for Execution
**Next Step:** Execute Phase 2 (Remove V1 Endpoints)



