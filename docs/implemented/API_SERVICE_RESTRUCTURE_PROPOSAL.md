# API Service Restructure Proposal

**Restructuring `api.service.ts` to Mirror Backend Blueprint Organization**

---

## Overview

The current `api.service.ts` file (634 lines) contains all API client functions in a single file, including legacy V1 endpoints and backward-compatible interfaces. This proposal restructures it to match the backend's blueprint organization, migrating to V2-only endpoints, improving maintainability, and adding API validation with developer-only logging.

---

## Current State

### Current Structure

**File:** `frontend/src/services/api.service.ts` (634 lines)

**Contents:**
- Core utilities (`getAuthHeaders`, `apiFetch`)
- Type definitions (interfaces and types, including legacy V1 interfaces)
- All API functions (18+ functions) grouped together:
  - System API: `healthCheck`
  - Resources API: `getCountries`, `getLocations`, `getCountry`, `getGuides`, `getGuide`, `getTags`, `getTripTypes`
  - V2 API: `getCompanies`, `getCompany`, `getTemplates`, `getTemplate`, `getOccurrences`, `getOccurrence`, `getTrips`, `getTrip`, `getRecommendations`, `getSchemaInfo`

**Issues:**
- Single large file (634 lines) with mixed concerns
- Contains legacy V1 endpoints and backward-compatible interfaces
- Types and implementation logic mixed together (prevents pure type imports)
- No API response validation
- Logs visible to end users (not just developers)
- All API functions in one namespace
- Difficult to navigate and maintain
- Doesn't mirror backend organization
- Hard to find specific API functions

---

## Backend Organization (Reference)

The backend is organized into blueprints:

```
backend/app/api/
├── system/
│   └── routes.py          # Health check, seed endpoints
├── resources/
│   └── routes.py          # Countries, guides, tags, trip types
├── events/
│   └── routes.py          # Event tracking, session management
├── analytics/
│   └── routes.py          # Metrics, evaluation endpoints
└── v2/
    └── routes.py          # Templates, occurrences, recommendations, companies (V2 only)
```

---

## Proposed Structure

### New Organization

```
frontend/src/services/
├── api/
│   ├── index.ts           # Main export file (re-exports all modules)
│   ├── client.ts          # Core utilities (apiFetch, getAuthHeaders)
│   ├── types.ts           # Type definitions only (pure interfaces, no side effects)
│   ├── system.ts          # System API (health check)
│   ├── resources.ts       # Resources API (countries, guides, tags, trip types)
│   └── v2.ts              # V2 API (templates, occurrences, trips, recommendations, companies)
└── tracking.service.ts    # (existing - unchanged)
```

### File Breakdown

#### 1. `services/api/types.ts` (~250 lines)
**Purpose:** Pure TypeScript type definitions only (no implementation, no side effects)

**Contents:**
- `ApiResponse<T>` interface
- All TypeScript interfaces and types:
  - `BaseCountry`, `BaseTripType`, `BaseTag` (base interfaces)
  - `Country`, `Guide`, `Tag`, `TripType`, `Company`
  - `TripTemplate` - The "what" of a trip (description, pricing, difficulty)
  - `TripOccurrence` - The "when" of a trip (dates, guide, availability)
  - `TripFilters` - Query parameters for filtering trips (snake_case for REST compatibility)
  - `RecommendationPreferences` - User preferences for recommendations (camelCase for frontend)
  - `RecommendedTripOccurrence` - Extends `TripOccurrence` with match score and details
  - All other type definitions

**Key Principles:**
- **Pure types only** - No functions, no constants, no side effects
- **No imports with side effects** - Only imports other types
- **V2-only interfaces** - Uses `TripTemplate` and `TripOccurrence` (no legacy `Trip` interface)
- **No runtime code** - Types are erased at compile time

**Exports:**
- All TypeScript types and interfaces (exported for consumers)

**Benefits:**
- Types can be imported without executing any code
- Prevents circular dependencies
- Better tree-shaking (types are erased)
- Clear separation of types from implementation

---

#### 2. `services/api/client.ts` (~200 lines)
**Purpose:** Core API client utilities (HTTP client logic)

**Contents:**
- `API_BASE_URL` constant
- `API_VERSION` constant (set to `/api/v2`)
- `getAuthHeaders()` function
- `apiFetch<T>()` function with:
  - Error handling
  - Authentication headers
  - Timeout handling
  - Retry logic
  - Response validation (NEW)
  - Developer-only logging (NEW)
- `camelToSnake()` helper function (for query parameter conversion)
- `camelToSnakeObject()` helper function (for request body conversion)

**Exports:**
- `apiFetch` (internal, used by other modules)
- `getAuthHeaders` (internal)
- Helper functions (internal)

**Note:** Uses `client.ts` to represent the HTTP client utilities (following common naming conventions)

---

#### 3. `services/api/system.ts` (~30 lines)
**Purpose:** System API endpoints

**Contents:**
- `healthCheck()` function

**Exports:**
- `healthCheck`

**Endpoints:**
- `GET /api/health`

**Note:** System endpoints remain at `/api/health` (not versioned in V2)

---

#### 4. `services/api/resources.ts` (~150 lines)
**Purpose:** Resources API endpoints (reference data)

**Contents:**
- `getCountries()` function
- `getLocations()` function
- `getCountry()` function
- `getGuides()` function
- `getGuide()` function
- `getTags()` function
- `getTripTypes()` function

**Exports:**
- `getCountries`
- `getLocations`
- `getCountry`
- `getGuides`
- `getGuide`
- `getTags`
- `getTripTypes`

**Endpoints:**
- `GET /api/countries`
- `GET /api/locations`
- `GET /api/countries/:id`
- `GET /api/guides`
- `GET /api/guides/:id`
- `GET /api/tags`
- `GET /api/trip-types`

**Note:** Resources endpoints remain at `/api/*` (not versioned in V2)

---

#### 5. `services/api/v2.ts` (~250 lines)
**Purpose:** V2 API endpoints (templates, occurrences, trips, recommendations, companies)

**Contents:**
- `getCompanies()` function
- `getCompany()` function
- `getTemplates()` function - Returns `TripTemplate[]` with optional filters
- `getTemplate()` function - Returns `TripTemplate` with full details
- `getOccurrences()` function - Returns `TripOccurrence[]` with optional filters
- `getOccurrence()` function - Returns `TripOccurrence` with full details
- `getTripOccurrences()` function - Returns `TripOccurrence[]` (uses `/api/v2/trip-occurrences` endpoint)
- `getTripOccurrence()` function - Returns `TripOccurrence` by ID
- `getRecommendations()` function - Returns `RecommendedTripOccurrence[]` with match scores
- `getSchemaInfo()` function - Returns schema version and statistics

**Exports:**
- `getCompanies`
- `getCompany`
- `getTemplates`
- `getTemplate`
- `getOccurrences`
- `getOccurrence`
- `getTripOccurrences`
- `getTripOccurrence`
- `getRecommendations`
- `getSchemaInfo`

**Endpoints:**
- `GET /api/v2/companies`
- `GET /api/v2/companies/:id`
- `GET /api/v2/templates`
- `GET /api/v2/templates/:id`
- `GET /api/v2/occurrences`
- `GET /api/v2/occurrences/:id`
- `GET /api/v2/trip-occurrences` (NEW - specific endpoint for trip occurrences)
- `POST /api/v2/recommendations`
- `GET /api/v2/schema-info`

**Key Implementation Details:**
- **V2-only endpoints** - All functions use `/api/v2/*` endpoints
- **V2-only interfaces** - Use `TripOccurrence` and `TripTemplate` types (no legacy `Trip` interface)
- **CamelCase to snake_case conversion** - Frontend uses camelCase, backend expects snake_case for query params and request body
- **Type-safe recommendations** - `RecommendedTripOccurrence` extends `TripOccurrence` with match scoring
- **No backward compatibility** - All code uses V2 schema exclusively

---

#### 6. `services/api/index.ts` (~50 lines)
**Purpose:** Main export file - re-exports all modules

**Contents:**
- Re-exports all types from `types.ts`
- Re-exports all functions from `system.ts`
- Re-exports all functions from `resources.ts`
- Re-exports all functions from `v2.ts`

**Exports:**
- All types (TripTemplate, TripOccurrence, Country, Guide, etc.)
- All API functions

**Usage:**
```typescript
// Import from main index
import { getTrip, getRecommendations, TripOccurrence } from '@/services/api';

// Or import from specific modules
import { getTrip, getRecommendations } from '@/services/api/v2';
import { getCountries } from '@/services/api/resources';
import type { TripOccurrence, TripTemplate } from '@/services/api/types';
```

---

## Migration to V2 Only

### Remove Legacy Interfaces

**Interfaces Already Removed (Current State):**
- Legacy `Trip` interface has been removed from the current codebase
- The codebase now uses `TripOccurrence` and `TripTemplate` exclusively

**Interfaces in Current Codebase (V2 Schema):**
- `TripTemplate` - The "what" of a trip (description, pricing, difficulty)
- `TripOccurrence` - The "when" of a trip (dates, guide, availability)
- `RecommendedTripOccurrence` - Extends `TripOccurrence` with match score and details
- `Company` - Trip operators
- `Country`, `Guide`, `Tag`, `TripType` - Reference data
- `BaseCountry`, `BaseTripType`, `BaseTag` - Base interfaces

### Update Functions

**Current Function State:**
- `getTripOccurrences()` - Returns `TripOccurrence[]` (uses V2 endpoint)
- `getTripOccurrence()` - Returns `TripOccurrence` by ID
- `getRecommendations()` - Returns `RecommendedTripOccurrence[]`
- All functions already use V2 schema

**Note:** The current codebase is already using V2-only interfaces. The restructure will organize these existing functions into the new modular structure.

### Migration Checklist

- [ ] Remove legacy `Trip` interface from `types.ts`
- [ ] Update `getTrips()` to return `TripOccurrence[]`
- [ ] Update `getTrip()` to return `TripOccurrence`
- [ ] Update `RecommendedTrip` to extend `TripOccurrence` instead of `Trip`
- [ ] Update all consuming code to use `TripOccurrence` instead of `Trip`
- [ ] Remove format conversion utilities (if any)
- [ ] Update TypeScript types throughout codebase
- [ ] Test all API calls with V2 schema

---

## API Response Validation

### Proposal: Add Runtime Validation

**Purpose:** Validate API responses match expected TypeScript types at runtime

**Implementation Approach:**
- Use **Zod** for runtime schema validation
- Create Zod schemas for all API response types
- Validate responses in `apiFetch` function
- Provide clear error messages for validation failures
- Only validate in development mode (performance consideration)
- Install `zod` package: `npm install zod`

**Example Implementation:**
```typescript
// services/api/client.ts

import { z } from 'zod';
import type { ApiResponse } from './types';

// Basic ApiResponse schema
const ApiResponseSchema = <T extends z.ZodTypeAny>(dataSchema: T) => z.object({
  success: z.boolean(),
  data: dataSchema.optional(),
  count: z.number().optional(),
  total: z.number().optional(),
  error: z.string().optional(),
  message: z.string().optional(),
  api_version: z.string().optional(),
});

function validateResponse<T>(
  data: any,
  schema?: z.ZodSchema<T>
): { isValid: boolean; errors?: z.ZodError[]; data?: T } {
  // In production, skip validation for performance
  if (process.env.NODE_ENV === 'production') {
    return { isValid: true, data: data as T };
  }
  
  // In development, validate if schema provided
  if (schema) {
    try {
      const validated = schema.parse(data);
      return { isValid: true, data: validated };
    } catch (error) {
      if (error instanceof z.ZodError) {
        logApiWarning('Response validation failed', error.errors);
        return { isValid: false, errors: error.errors, data: data as T };
      }
    }
  }
  
  // Basic validation: check for success field
  if (data && typeof data === 'object') {
    if (!data.hasOwnProperty('success')) {
      logApiWarning('Response missing "success" field', data);
    }
  }
  
  return { isValid: true, data: data as T };
}

async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit,
  retryAttempt = 0,
  schema?: z.ZodSchema<T> // Optional Zod schema for validation
): Promise<ApiResponse<T>> {
  // ... existing fetch logic ...
  
  const response = await fetch(/* ... */);
  const data = await response.json();
  
  // Validate response structure (development only)
  if (process.env.NODE_ENV === 'development') {
    validateResponse(data, schema);
  }
  
  // Return validated data
  return data as ApiResponse<T>;
}
```

**Usage Example:**
```typescript
// In v2.ts or resources.ts
import { z } from 'zod';
import { apiFetch } from './client';

// Define Zod schema for TripOccurrence
const TripOccurrenceSchema = z.object({
  id: z.number(),
  tripTemplateId: z.number(),
  guideId: z.number().optional(),
  startDate: z.string(),
  endDate: z.string(),
  // ... other fields
});

export async function getTripOccurrence(id: number) {
  return apiFetch<TripOccurrence>(
    `/api/v2/occurrences/${id}`,
    undefined,
    0,
    TripOccurrenceSchema // Pass schema for validation
  );
}
```

**Validation Levels:**
1. **Basic validation** (always on): Check for required fields (`success`, `data`)
2. **Schema validation** (development only): Full runtime schema validation using Zod
   - Create Zod schemas for all API response types
   - Validate responses match expected structure
   - Log validation errors with detailed field information
   - Graceful degradation (invalid responses still returned, but logged)

**Error Handling:**
- Validation errors logged to console (development only)
- Invalid responses still returned (graceful degradation)
- Option to throw errors on validation failure (configurable)

---

## Developer-Only Logging

### Proposal: Environment-Based Logging

**Purpose:** Show API logs only to developers, not end users

**Implementation Approach:**
- Use environment variable to detect development mode
- Log API calls, errors, and debugging info only in development
- Use console methods appropriately (console.log, console.error, console.warn)
- Consider using a logging utility for better control

**Example Implementation:**
```typescript
// services/api/client.ts

const IS_DEVELOPMENT = process.env.NODE_ENV === 'development';

function logApiCall(endpoint: string, method: string, status: number, duration: number): void {
  if (!IS_DEVELOPMENT) return;
  
  console.log(`[API] ${method} ${endpoint} - ${status} (${duration}ms)`);
}

function logApiError(endpoint: string, error: Error, retryAttempt: number): void {
  if (!IS_DEVELOPMENT) return;
  
  console.error(`[API] Error on ${endpoint} (attempt ${retryAttempt + 1}):`, error);
}

function logApiWarning(message: string, data?: any): void {
  if (!IS_DEVELOPMENT) return;
  
  console.warn(`[API] ${message}`, data || '');
}

// Usage in apiFetch
async function apiFetch<T>(endpoint: string, options?: RequestInit, retryAttempt = 0): Promise<ApiResponse<T>> {
  const startTime = Date.now();
  
  try {
    if (IS_DEVELOPMENT) {
      logApiCall(endpoint, options?.method || 'GET', 0, 0);
    }
    
    const response = await fetch(/* ... */);
    const duration = Date.now() - startTime;
    
    if (IS_DEVELOPMENT) {
      logApiCall(endpoint, options?.method || 'GET', response.status, duration);
    }
    
    // ... rest of logic ...
  } catch (error) {
    if (IS_DEVELOPMENT) {
      logApiError(endpoint, error as Error, retryAttempt);
    }
    // ... error handling ...
  }
}
```

**Logging Levels:**
1. **Development mode (default):**
   - All API calls (method, endpoint, status, duration)
   - Errors and warnings
   - Retry attempts
   - Validation warnings

2. **Production mode:**
   - No console logs
   - Critical errors only (sent to error tracking service if configured)
   - Silent failures (user-friendly error messages)

**Benefits:**
- Cleaner production console (no developer logs)
- Better debugging in development
- Improved performance (no logging overhead in production)
- Professional user experience

**Configuration:**
- Automatic detection via `NODE_ENV`
- Can be overridden with environment variable if needed
- Respects browser console settings

---

## Implementation Plan

### Phase 1: Create New Structure (Breaking Change - Option B)

1. **Create `services/api/` directory**
2. **Create `services/api/types.ts`**
   - Move all type definitions from `api.service.ts`
   - Include: `ApiResponse`, `Country`, `Guide`, `Tag`, `TripType`, `Company`
   - Include: `TripTemplate`, `TripOccurrence`, `RecommendedTripOccurrence`
   - Include: `TripFilters`, `RecommendationPreferences`
   - Include: Base interfaces (`BaseCountry`, `BaseTripType`, `BaseTag`)
   - Ensure pure types only (no side effects, no functions)
3. **Create `services/api/client.ts`**
   - Move `apiFetch` and `getAuthHeaders` functions
   - Move `API_BASE_URL` and `API_VERSION` constants
   - Move `camelToSnake()` and `camelToSnakeObject()` helper functions
   - Add API validation (NEW)
   - Add developer-only logging (NEW)
4. **Create `services/api/system.ts`**
   - Move `healthCheck` function
   - Import `apiFetch` from `./client`
   - Import types from `./types`
5. **Create `services/api/resources.ts`**
   - Move resource API functions: `getCountries`, `getLocations`, `getCountry`, `getGuides`, `getGuide`, `getTags`, `getTripTypes`
   - Import `apiFetch` from `./client`
   - Import types from `./types`
6. **Create `services/api/v2.ts`**
   - Move V2 API functions: `getCompanies`, `getCompany`, `getTemplates`, `getTemplate`, `getOccurrences`, `getOccurrence`, `getTripOccurrences`, `getTripOccurrence`, `getRecommendations`, `getSchemaInfo`
   - Functions already use V2 endpoints and V2 interfaces (no changes needed)
   - Import `apiFetch` from `./client`
   - Import types from `./types`
   - Note: Helper functions (`camelToSnake`, `camelToSnakeObject`) are used for converting camelCase (frontend) to snake_case (backend)
7. **Create `services/api/index.ts`**
   - Re-export all types from `types.ts`
   - Re-export all functions from `system.ts`
   - Re-export all functions from `resources.ts`
   - Re-export all functions from `v2.ts`

### Phase 2: Update All Imports (Breaking Change)

**Update all files that import from `api.service.ts`:**

```bash
# Find all files using api.service
grep -r "from '@/services/api.service'" frontend/src --include="*.ts" --include="*.tsx"

# Update imports:
# OLD: import { getTripOccurrence, getRecommendations, TripOccurrence } from '@/services/api.service'
# NEW: import { getTripOccurrence, getRecommendations, TripOccurrence } from '@/services/api'

# Or use specific module imports:
# import { getTripOccurrence, getRecommendations } from '@/services/api/v2'
# import type { TripOccurrence, TripTemplate } from '@/services/api/types'
```

**Files to Update:**
- `frontend/src/app/search/page.tsx` - Uses `getLocations`, `getTripTypes`, `getTags`
- `frontend/src/app/search/results/page.tsx` - Uses `getRecommendations`, `TripOccurrence`, `RecommendedTripOccurrence`
- `frontend/src/app/trip/[id]/page.tsx` - Uses `getTripOccurrence` or `getOccurrence`
- `frontend/src/lib/dataStore.tsx` - Uses resource API functions
- `frontend/src/components/features/TripResultCard.tsx` - Uses `TripOccurrence` types
- Any other files importing from `api.service.ts`

**Important Type Updates:**
- Update any references from old `Trip` interface to `TripOccurrence`
- Update `RecommendedTrip` to `RecommendedTripOccurrence`
- Ensure all imports use V2 types

### Phase 3: Remove Old File and Legacy Code

- [ ] Delete `services/api.service.ts`
- [ ] Verify no legacy V1 interfaces remain (current codebase is already V2-only)
- [ ] Verify all TypeScript types use V2 schema (`TripOccurrence`, `TripTemplate`, `RecommendedTripOccurrence`)
- [ ] Clean up any remaining references to old file structure
- [ ] Verify camelCase to snake_case conversion is handled correctly in `client.ts`

### Phase 4: Update Documentation

- [ ] Update `FRONTEND_OVERVIEW.md` to reflect new structure
- [ ] Update API usage examples
- [ ] Document new import patterns
- [ ] Document V2-only migration
- [ ] Document API validation
- [ ] Document developer-only logging

---

## Migration Strategy

### Approach: Option B (Breaking Change)

**Step 1: Create new structure**
- Create `services/api/` directory with new modules
- Implement V2-only interfaces and functions
- Add API validation and developer-only logging

**Step 2: Update all imports**
- Search and replace: `from '@/services/api.service'` → `from '@/services/api'`
- Update type imports to use V2 schema
- Update function calls to use V2 return types

**Step 3: Delete old file**
- Remove `api.service.ts`
- Remove legacy interfaces
- Clean up any remaining V1 code

**Step 4: Test thoroughly**
- Test all API calls
- Verify TypeScript compilation
- Test error handling
- Test validation (development mode)
- Test logging (development vs production)

---

## Benefits

### 1. Better Organization
- **Mirrors backend structure** - Easier to find corresponding functions
- **Separated concerns** - Types, base utilities, and API functions are separated
- **Clearer structure** - Developers know where to look
- **Pure type imports** - Types can be imported without side effects

### 2. Improved Maintainability
- **Smaller files** - Easier to read and understand
- **Focused modules** - Changes to one API area don't affect others
- **Better navigation** - IDE can navigate to specific modules
- **V2-only** - No legacy code to maintain

### 3. Better Code Quality
- **Pure types** - Types in separate file prevent side effects
- **API validation** - Catch API response issues early
- **Developer-only logging** - Clean production logs
- **Type safety** - V2 schema provides better type safety

### 4. Better Code Reusability
- **Selective imports** - Import only what you need
- **Pure type imports** - Import types without executing code
- **Tree-shaking friendly** - Bundlers can eliminate unused code
- **Modular architecture** - Clear module boundaries

### 5. Scalability
- **Easy to add new APIs** - Add new modules (e.g., `events.ts`, `analytics.ts`)
- **Easy to extend** - Add new functions to appropriate modules
- **Matches backend growth** - Structure scales with backend changes
- **V2-focused** - Ready for future V2 enhancements

### 6. Developer Experience
- **Clearer imports** - `from '@/services/api/v2'` is self-documenting
- **Better autocomplete** - IDE can suggest relevant functions
- **Easier code reviews** - Changes are scoped to specific modules
- **Better debugging** - Developer-only logs help debugging

---

## File Size Comparison

| File | Current | Proposed | Change |
|------|---------|----------|--------|
| `api.service.ts` | 636 lines | **DELETED** | -100% |
| `api/types.ts` | - | ~250 lines | NEW |
| `api/client.ts` | - | ~200 lines | NEW |
| `api/system.ts` | - | ~30 lines | NEW |
| `api/resources.ts` | - | ~180 lines | NEW |
| `api/v2.ts` | - | ~280 lines | NEW |
| `api/index.ts` | - | ~50 lines | NEW |
| **Total** | **636 lines** | **~990 lines** | **+56%** |

**Note:** Total lines increase due to:
- Module imports/exports
- File headers and comments
- API validation code
- Developer logging code
- Better code organization
- Removal of legacy code (replaced with V2 code)

**Trade-off:** Increase in total lines for significantly better organization, V2-only codebase, validation, and maintainability.

---

## Example Usage (After Refactoring)

### New Usage (Recommended)

#### Import from Main Index
```typescript
import { getTrip, getRecommendations, TripOccurrence } from '@/services/api';
```

#### Import from Specific Modules (Recommended)
```typescript
import { getTripOccurrence, getRecommendations } from '@/services/api/v2';
import { getCountries } from '@/services/api/resources';
import type { TripOccurrence, TripTemplate, RecommendedTripOccurrence } from '@/services/api/types';
```

#### Pure Type Import (No Side Effects)
```typescript
// Only imports types, no code execution
import type { TripOccurrence, TripTemplate, Country } from '@/services/api/types';
```

#### Namespace Import
```typescript
import * as ResourcesAPI from '@/services/api/resources';
import * as V2API from '@/services/api/v2';

const countries = await ResourcesAPI.getCountries();
const trip = await V2API.getTrip(123);
```

---

## Testing Strategy

### 1. Verify TypeScript Compilation
- Ensure all imports resolve correctly
- Verify V2 types are used throughout
- Check for any remaining V1 type references
- Verify type inference works correctly

### 2. Verify Functionality
- Test all API calls in the application
- Verify error handling still works
- Test retry logic and timeouts
- Test API validation (development mode)
- Test developer logging (development vs production)

### 3. Verify V2 Migration
- Ensure no V1 endpoints are used
- Verify all responses use V2 schema
- Test that legacy interfaces are removed
- Verify consuming code uses V2 types

### 4. Verify Logging
- Test logs appear in development mode
- Test logs don't appear in production mode
- Verify error logging works correctly
- Test API call logging

---

## Migration Checklist

### Phase 1: Create New Structure
- [ ] Create `services/api/` directory
- [ ] Create `services/api/types.ts` with V2-only types (TripOccurrence, TripTemplate, RecommendedTripOccurrence)
- [ ] Create `services/api/client.ts` with apiFetch, validation, logging, and helper functions
- [ ] Create `services/api/system.ts` with system API
- [ ] Create `services/api/resources.ts` with resources API
- [ ] Create `services/api/v2.ts` with V2-only API functions (getTripOccurrences, getRecommendations, etc.)
- [ ] Create `services/api/index.ts` with re-exports
- [ ] Verify TypeScript compilation

### Phase 2: Update All Imports (Breaking Change)
- [ ] Find all files importing from `api.service.ts`
- [ ] Update imports to use `from '@/services/api'`
- [ ] Update type imports: `TripOccurrence`, `TripTemplate`, `RecommendedTripOccurrence` (remove any old `Trip` references)
- [ ] Update function calls: `getTripOccurrence()`, `getTripOccurrences()`, `getRecommendations()` (returns `RecommendedTripOccurrence[]`)
- [ ] Test TypeScript compilation

### Phase 3: Remove Old File and Legacy Code
- [ ] Delete `services/api.service.ts`
- [ ] Remove legacy V1 interfaces
- [ ] Remove backward-compatibility code
- [ ] Clean up any remaining V1 references

### Phase 4: Testing
- [ ] Test all API calls
- [ ] Test error handling
- [ ] Test API validation (development)
- [ ] Test developer logging (development vs production)
- [ ] Test V2 schema usage
- [ ] Run full application test suite

### Phase 5: Documentation
- [ ] Update `FRONTEND_OVERVIEW.md`
- [ ] Update API usage examples
- [ ] Document new import patterns
- [ ] Document V2-only migration
- [ ] Document API validation
- [ ] Document developer-only logging

---

## Considerations

### 1. Breaking Changes
- **Option B (Chosen):** Breaking change - requires updating all imports
- **All imports must be updated** - Cannot use old `api.service.ts`
- **V2-only migration** - Legacy V1 code removed
- **Type changes** - Consuming code must use V2 types

### 2. Bundle Size
- Minimal impact - modern bundlers handle tree-shaking
- Validation code only runs in development
- Logging code only runs in development
- May slightly improve bundle size (better tree-shaking, removed legacy code)

### 3. Developer Onboarding
- New structure is more intuitive
- Mirrors backend organization (easier for full-stack developers)
- Clearer module boundaries
- V2-only simplifies understanding

### 4. Performance
- API validation only runs in development (no production overhead)
- Developer logging only runs in development (no production overhead)
- No runtime performance impact in production
- Better tree-shaking may improve bundle size

### 5. Future Extensions
- Easy to add `events.ts` module (for event tracking API)
- Easy to add `analytics.ts` module (for analytics API)
- Structure scales naturally
- V2-focused ready for future enhancements

---

## Alternative Approaches

### Alternative 1: Keep Single File
**Pros:**
- No refactoring needed
- Simpler structure

**Cons:**
- File continues to grow
- Harder to maintain
- Doesn't match backend organization
- Mixed types and implementation
- No validation
- Logs visible to users

### Alternative 2: Split by Domain (Current Proposal)
**Pros:**
- Matches backend organization
- Clear module boundaries
- Scalable structure
- Pure type imports
- V2-only codebase
- API validation
- Developer-only logging

**Cons:**
- Requires refactoring
- Breaking change
- More files to manage

### Alternative 3: Keep Backward Compatibility
**Pros:**
- No breaking changes
- Gradual migration

**Cons:**
- Maintains legacy code
- More complex codebase
- Technical debt
- Doesn't align with V2-only goal

---

## Recommendation

**Recommendation: Implement Option B (Breaking Change with V2-Only Migration)**

This approach:
1. ✅ Creates better organization matching backend
2. ✅ Separates types from implementation (pure type imports)
3. ✅ Migrates to V2-only endpoints and interfaces
4. ✅ Removes legacy code and technical debt
5. ✅ Adds API validation for better error detection
6. ✅ Adds developer-only logging for better debugging
7. ✅ Improves maintainability and scalability
8. ✅ Better type safety with V2 schema
9. ✅ Cleaner codebase without backward-compatibility code

**Trade-offs:**
- Breaking change requires updating all imports
- More initial work to migrate
- Worth it for long-term maintainability

---

## Next Steps

1. **Review and approve this proposal**
2. **Create new `services/api/` structure**
3. **Implement Phase 1 (create new modules with V2-only code)**
4. **Update all imports (Phase 2)**
5. **Remove old file and legacy code (Phase 3)**
6. **Test thoroughly (Phase 4)**
7. **Update documentation (Phase 5)**

---

## References

- Backend API Structure: `docs/api/API_STRUCTURE.md`
- Current API Service: `frontend/src/services/api.service.ts`
- Frontend Overview: `docs/architecture/FRONTEND_OVERVIEW.md`
- Backend Blueprints: `backend/app/api/`
- V2 Schema Documentation: `docs/api/API_STRUCTURE.md` (V2 API section)
