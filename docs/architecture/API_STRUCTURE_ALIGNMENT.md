# API Structure Alignment: Backend ↔ Frontend

**Purpose:** Document the current differences between backend and frontend API structures and provide a plan to fully mirror the backend blueprint organization on the frontend.

**Last Updated:** 2024-12-19

---

## Table of Contents

1. [Current Structure Comparison](#current-structure-comparison)
2. [Detailed Differences](#detailed-differences)
3. [Best Practices](#best-practices)
4. [Implementation Plan](#implementation-plan)
5. [Migration Strategy](#migration-strategy)

---

## Current Structure Comparison

### Backend API Structure (`backend/app/api/`)

```
backend/app/api/
├── __init__.py                    # Blueprint registration
├── system/
│   ├── __init__.py
│   └── routes.py                  # Health check, seed
├── resources/
│   ├── __init__.py
│   └── routes.py                  # Countries, guides, tags, trip-types, locations
├── analytics/
│   ├── __init__.py
│   └── routes.py                  # Metrics, evaluation
├── events/
│   ├── __init__.py
│   └── routes.py                  # Session, events, user identify
└── v2/
    ├── __init__.py
    └── routes.py                  # Companies, templates, occurrences, recommendations
```

**Total Blueprints:** 5 (system, resources, analytics, events, v2)

### Frontend API Structure (`frontend/src/api/`)

```
frontend/src/api/
├── index.ts                       # Barrel export (like __init__.py)
├── client.ts                      # Core API client utilities
├── types.ts                       # TypeScript type definitions
├── system.ts                      # ✅ Health check
├── resources.ts                   # ✅ Countries, guides, tags, trip-types, locations
└── v2.ts                          # ✅ Companies, templates, occurrences, recommendations

frontend/src/services/
└── tracking.service.ts            # ⚠️ Events API (not in api/ structure)
```

**Current Files:** 3 structured API files + 1 service file outside structure

### Backend Schemas Structure (`backend/app/schemas/`)

```
backend/app/schemas/
├── __init__.py                    # Schema exports
├── base.py                        # BaseSchema, camelCase alias generator
├── resources.py                   # Country, Guide, TripType, Tag, Company schemas
├── trip.py                        # TripTemplate, TripOccurrence schemas
└── utils.py                       # Response serialization helpers
```

### Frontend Schemas Structure (`frontend/src/schemas/`)

```
frontend/src/schemas/
├── index.ts                       # ✅ Barrel export
├── base.ts                        # ✅ Base schemas, enums
├── resources.ts                   # ✅ Resource schemas
└── trip.ts                        # ✅ Trip schemas
```

**Note:** Frontend missing `utils.ts` equivalent (currently handled in `client.ts`)

---

## Detailed Differences

### 1. Missing API Modules

#### ❌ Analytics API (`analytics.ts`)
**Backend Endpoints:**
- `GET /api/metrics` - Current recommendation metrics
- `GET /api/metrics/daily` - Daily metrics breakdown
- `GET /api/metrics/top-searches` - Top search patterns
- `POST /api/evaluation/run` - Run evaluation scenarios
- `GET /api/evaluation/scenarios` - List available scenarios

**Frontend Status:** Not implemented. No frontend usage detected.

**Impact:** Low (admin/internal tool, not user-facing)

#### ❌ Events API (`events.ts`)
**Backend Endpoints:**
- `POST /api/session/start` - Initialize/resume session
- `POST /api/events` - Track single event
- `POST /api/events/batch` - Track multiple events
- `POST /api/user/identify` - Identify/register user
- `GET /api/events/types` - Get valid event types

**Frontend Status:** Implemented in `frontend/src/services/tracking.service.ts` using raw `fetch()` calls, not integrated into structured API client.

**Impact:** Medium (currently working but not following structured pattern)

**Current Implementation Issues:**
- Uses raw `fetch()` instead of `apiFetch()` utility
- No Zod schema validation
- No automatic error handling/retry
- No consistent logging
- Not exported from `api/index.ts`

### 2. Schema Structure Differences

#### ✅ Schema Utilities (Handled in `client.ts`)

**Backend (`schemas/utils.py`):**
- `serialize_response()` helper function
- Response formatting utilities

**Frontend Status:** Response formatting handled in `client.ts` via `validateResponse()` function.

**Decision:** Do NOT create `utils.ts` in schemas. Keep `validateResponse()` in `client.ts` unless logic is duplicated across multiple API files.

**Impact:** None (functionality exists and is properly located)

### 3. File Organization

#### ✅ Matched Structure
- `system.ts` ↔ `system/routes.py`
- `resources.ts` ↔ `resources/routes.py`
- `v2.ts` ↔ `v2/routes.py`

#### ⚠️ Partial Match
- `tracking.service.ts` ↔ `events/routes.py` (functionality exists but wrong location/pattern)

#### ❌ Missing
- `analytics.ts` ↔ `analytics/routes.py`

---

## Best Practices

### 1. **Mirror Backend Structure Exactly**
- Each backend blueprint should have a corresponding frontend API file
- Use consistent naming: `system.ts`, `resources.ts`, `analytics.ts`, `events.ts`, `v2.ts`
- Keep the same logical grouping of endpoints

### 2. **Consistent API Client Usage**
- All API calls should use `apiFetch()` from `client.ts`
- Benefits:
  - Automatic authentication handling
  - Consistent error handling
  - Retry logic for cold starts
  - Zod schema validation
  - Developer-only logging

### 3. **Schema Validation**
- Every endpoint should have a corresponding Zod schema
- Use `z.infer<typeof Schema>` for type inference
- Maintain schema in `schemas/` directory matching backend structure

### 4. **Type Safety**
- All types should be inferred from Zod schemas via `types.ts`
- No manual type definitions that duplicate schema information
- Use barrel exports (`index.ts`) for clean imports

### 5. **Separation of Concerns**
- **API Client (`api/`):** "Dumb" transport layer - HTTP calls, request/response handling, validation only
  - ✅ Should: Make HTTP requests, validate responses with Zod
  - ❌ Should NOT: Handle business logic, retry strategies, queuing, batching orchestration
  
- **Schemas (`schemas/`):** Validation schemas, data structure definitions
- **Types (`api/types.ts`):** TypeScript type definitions (inferred from schemas)
  
- **Services (`services/`):** Business logic, orchestration, state management
  - ✅ Should: Handle queuing, batching, retry strategies, offline handling
  - ✅ Should: Use API client functions for HTTP communication
  - ❌ Should NOT: Make raw `fetch()` calls (should use API client)

### 6. **Service Layer Pattern**
- For complex operations (like event tracking with batching), use a service file
- **API Client** (`api/events.ts`): Exports raw functions like `trackEvent()`, `trackEventsBatch()` - just HTTP calls
- **Service Layer** (`tracking.service.ts`): Imports API client functions, handles:
  - Event queuing
  - Batching logic (when to flush)
  - Retry strategies
  - Offline handling
  - Session management orchestration
- Example: `tracking.service.ts` imports `trackEventsBatch()` from `api/events.ts` and orchestrates when/how to call it

---

## Implementation Plan

### Phase 1: Create Missing API Files ✅

#### Step 1.1: Create `frontend/src/api/events.ts`
**Purpose:** Mirror `backend/app/api/events/routes.py` - Transport layer only

**Important:** This file should be "dumb" - just HTTP calls with validation. NO business logic.

**Tasks:**
1. Create `events.ts` file in `frontend/src/api/`
2. Define Zod schemas for all events endpoints in `schemas/`
3. Implement raw API functions (transport layer only):
   - `startSession()` - POST /api/session/start (just makes the HTTP call)
   - `trackEvent()` - POST /api/events (just makes the HTTP call)
   - `trackEventsBatch()` - POST /api/events/batch (just makes the HTTP call)
   - `identifyUser()` - POST /api/user/identify (just makes the HTTP call)
   - `getEventTypes()` - GET /api/events/types (just makes the HTTP call)
4. Use `apiFetch()` with appropriate schemas
5. Export from `api/index.ts`
6. **DO NOT** add retry logic, queuing, or batching orchestration here

**Estimated Effort:** 1-2 hours

#### Step 1.2: Create `frontend/src/api/analytics.ts`
**Purpose:** Mirror `backend/app/api/analytics/routes.py`

**Tasks:**
1. Create `analytics.ts` file in `frontend/src/api/`
2. Define Zod schemas for analytics endpoints
3. Implement functions:
   - `getMetrics()` - GET /api/metrics
   - `getDailyMetrics()` - GET /api/metrics/daily
   - `getTopSearches()` - GET /api/metrics/top-searches
   - `runEvaluation()` - POST /api/evaluation/run
   - `getEvaluationScenarios()` - GET /api/evaluation/scenarios
4. Use `apiFetch()` with appropriate schemas
5. Export from `api/index.ts`

**Estimated Effort:** 2-3 hours

### Phase 2: Migrate Events from Service to API Client ✅

#### Step 2.1: Update `tracking.service.ts`
**Purpose:** Refactor to use structured API client instead of raw `fetch()` while preserving all business logic

**Critical:** Keep ALL business logic in the service layer. API client is just for HTTP transport.

**Tasks:**
1. Import `trackEventsBatch()` and `startSession()` from `api/events.ts`
2. Replace raw `fetch()` calls with API client functions
3. Remove duplicate API URL constants (use from `client.ts`)
4. **PRESERVE** all service-specific logic:
   - Event queuing logic
   - Batching orchestration (when to flush)
   - Retry strategies
   - Offline handling
   - Session management orchestration
   - Device detection
5. Ensure error handling remains graceful (don't block user experience)

**Estimated Effort:** 1-2 hours

**Key Principles:**
- Service layer handles ALL business logic (batching, queuing, retry strategies)
- API client handles ONLY HTTP communication (fetch + validate)
- Service layer orchestrates when/how to call API client functions
- Maintain backward compatibility (no breaking changes)

**Example:**
```typescript
// ✅ GOOD: Service orchestrates, API client does transport
import { trackEventsBatch } from '@/api/events';

async function flushEvents() {
  // Service handles batching logic
  const eventsToSend = [...eventQueue];
  eventQueue = [];
  
  // Service handles retry strategy
  try {
    await trackEventsBatch({ events: eventsToSend }); // API client just does HTTP
  } catch (error) {
    // Service handles error recovery (re-queue, etc.)
    eventQueue = [...eventsToSend, ...eventQueue];
  }
}

// ❌ BAD: API client handling business logic
// Don't add retry/queuing logic to api/events.ts
```

### Phase 3: Add Missing Schemas ✅

#### Step 3.1: Add Event Schemas to `schemas/`
**Purpose:** Define Zod schemas for all events API endpoints

**Location:** Create `frontend/src/schemas/events.ts` (keep schemas organized by domain)

**Schemas Needed:**
- `SessionStartRequestSchema`
- `SessionStartResponseSchema`
- `EventRequestSchema`
- `EventResponseSchema`
- `EventBatchRequestSchema`
- `EventBatchResponseSchema`
- `UserIdentifyRequestSchema`
- `UserIdentifyResponseSchema`
- `EventTypesResponseSchema`

**Note:** Use `createApiResponseSchema()` pattern from `resources.ts` for response wrappers.

**Estimated Effort:** 1-2 hours

#### Step 3.2: Add Analytics Schemas to `schemas/`
**Purpose:** Define Zod schemas for all analytics API endpoints

**Location:** Create `frontend/src/schemas/analytics.ts`

**Schemas Needed:**
- `MetricsResponseSchema`
- `DailyMetricsResponseSchema`
- `TopSearchesResponseSchema`
- `EvaluationRunRequestSchema`
- `EvaluationRunResponseSchema`
- `EvaluationScenariosResponseSchema`

**Note:** Analytics schemas may need `.passthrough()` if response structure is flexible.

**Estimated Effort:** 1-2 hours

### Phase 4: Update Exports and Documentation ✅

#### Step 4.1: Update `api/index.ts`
**Tasks:**
- Export all functions from `events.ts`
- Export all functions from `analytics.ts`
- Ensure consistent export pattern

#### Step 4.2: Update Type Exports
**Tasks:**
- Add event-related types to `api/types.ts`
- Add analytics-related types to `api/types.ts`
- Ensure all types are inferred from schemas

#### Step 4.3: Update Documentation
**Tasks:**
- Update `docs/api/API_STRUCTURE.md` if it exists
- Document new API files
- Update any architecture diagrams

**Estimated Effort:** 30 minutes

---

## Migration Strategy

### Option A: Non-Breaking Migration (Recommended)

**Approach:** Add new structured API files alongside existing implementations, then gradually migrate.

**Steps:**
1. ✅ Create `api/events.ts` with new structured functions
2. ✅ Update `tracking.service.ts` to use `api/events.ts` functions instead of raw `fetch()`
3. ✅ Create `api/analytics.ts` (no existing usage, safe to add)
4. ✅ Test all functionality to ensure nothing breaks
5. ✅ Remove any deprecated code paths

**Advantages:**
- No breaking changes
- Can test incrementally
- Easy rollback if issues arise

**Timeline:** 1-2 days

### Option B: Breaking Change Migration

**Approach:** Replace existing implementations immediately.

**Steps:**
1. Create new API files
2. Update all imports across codebase
3. Remove old implementations

**Advantages:**
- Cleaner migration
- Forces consistency immediately

**Disadvantages:**
- Risk of breaking existing functionality
- Requires comprehensive testing

**Timeline:** 1 day (but higher risk)

---

## File Structure After Completion

### Final Frontend API Structure

```
frontend/src/api/
├── index.ts                       # Exports all API functions
├── client.ts                      # Core API client utilities
├── types.ts                       # TypeScript type definitions (inferred from schemas)
├── system.ts                      # ✅ System API (health check, seed)
├── resources.ts                   # ✅ Resources API (countries, guides, tags, trip-types)
├── analytics.ts                   # ✅ Analytics API (metrics, evaluation)
├── events.ts                      # ✅ Events API (session, events, user identify)
└── v2.ts                          # ✅ V2 API (companies, templates, occurrences, recommendations)
```

### Final Frontend Schemas Structure

```
frontend/src/schemas/
├── index.ts                       # Exports all schemas
├── base.ts                        # Base schemas, enums (TripStatus, DifficultyLevel)
├── resources.ts                   # Resource schemas (Country, Guide, TripType, Tag, Company)
├── trip.ts                        # Trip schemas (TripTemplate, TripOccurrence)
├── events.ts                      # ✅ Event schemas (Session, Event, UserIdentify)
└── analytics.ts                   # ✅ Analytics schemas (Metrics, Evaluation)
```

### Final Frontend Services Structure

```
frontend/src/services/
├── tracking.service.ts            # Event tracking service (uses api/events.ts)
└── (other services as needed)
```

---

## Testing Checklist

After implementation, verify:

- [ ] All events API endpoints work via `api/events.ts`
- [ ] `tracking.service.ts` uses structured API client
- [ ] All analytics API endpoints work via `api/analytics.ts`
- [ ] All functions exported from `api/index.ts`
- [ ] Zod schema validation works for all endpoints
- [ ] Type inference works correctly
- [ ] Error handling is consistent
- [ ] No breaking changes to existing functionality
- [ ] Developer logging works as expected

---

## Success Criteria

✅ **Structure Match:**
- Frontend `api/` directory mirrors backend `api/` blueprints exactly
- Same number of API files as backend blueprints (5 files)

✅ **Consistency:**
- All API calls use `apiFetch()` utility
- All endpoints have Zod schema validation
- All types inferred from schemas

✅ **Maintainability:**
- Clear separation between API client and service logic
- Easy to add new endpoints by following existing patterns
- Documentation is up-to-date

---

## Notes

1. **Analytics API:** Currently not used in frontend, but should be implemented for completeness and potential future admin tools.

2. **Events API:** Already functional via `tracking.service.ts`, but needs to be refactored to use structured API client for consistency.

3. **Backward Compatibility:** The migration should not break existing functionality. All current event tracking should continue to work.

4. **Performance:** Using structured API client should not impact performance. The `apiFetch()` utility is optimized and validation is development-only.

5. **Future Extensibility:** Once structure is mirrored, adding new endpoints becomes straightforward by following the established pattern.

---

## References

- Backend API Structure: `docs/api/API_STRUCTURE.md`
- Frontend API Client: `frontend/src/api/client.ts`
- Backend Blueprints: `backend/app/api/*/routes.py`
- Frontend Tracking Service: `frontend/src/services/tracking.service.ts`
