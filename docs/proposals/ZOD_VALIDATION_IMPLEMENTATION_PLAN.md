# Zod Validation Implementation Plan

**Complete Zod Schema Implementation for All API Endpoints**

---

## Overview

This plan outlines the complete implementation of Zod runtime validation for all API endpoints. Validation will be active in development mode only to catch API response mismatches early without impacting production performance.

---

## Goals

1. **Runtime Type Safety** - Validate all API responses match TypeScript types at runtime
2. **Early Error Detection** - Catch API contract violations during development
3. **Developer Experience** - Clear validation error messages for debugging
4. **Zero Production Impact** - Validation only runs in development mode
5. **Maintainable Schemas** - Organized, reusable Zod schemas that mirror TypeScript types

---

## Current State

### Infrastructure Ready
- ✅ Zod package installed
- ✅ `apiFetch` function accepts optional `schema` parameter
- ✅ `validateResponse` function implemented
- ✅ Developer-only logging implemented

### Missing
- ❌ Zod schemas for API response types
- ❌ Schemas not passed to `apiFetch` calls
- ❌ No validation currently active

---

## Implementation Strategy

### Phase 1: Create Zod Schemas Module
Create a dedicated `schemas.ts` file with all Zod schemas organized by domain.

### Phase 2: Define Base Schemas
Start with base/primitive schemas, then build complex schemas from them.

### Phase 3: Define Response Schemas
Create schemas for each API endpoint's response type.

### Phase 4: Integrate Schemas
Update all API functions to pass schemas to `apiFetch`.

### Phase 5: Test and Validate
Test validation in development mode and verify error messages.

---

## Schema Organization

### File Structure

```
frontend/src/services/api/
├── schemas.ts          # All Zod schemas (NEW - PRIMARY SOURCE)
├── types.ts            # TypeScript types inferred from schemas (UPDATED)
├── client.ts           # apiFetch with validation (existing)
├── system.ts           # System API (needs schemas)
├── resources.ts        # Resources API (needs schemas)
└── v2.ts               # V2 API (needs schemas)
```

### Schema-First Approach

**Key Principle:** Define Zod schemas first, then infer TypeScript types using `z.infer<typeof Schema>`.

**Benefits:**
- Single source of truth - Zod schemas define both runtime validation and types
- Types and schemas can never go out of sync
- Less code duplication
- Schema serves as both validation and type definition

### Schema Hierarchy

1. **Base Schemas** - Primitives and common structures
2. **Entity Schemas** - Domain entities (Country, Guide, Tag, etc.)
3. **Response Schemas** - API response wrappers
4. **Endpoint Schemas** - Specific endpoint responses
5. **Type Exports** - TypeScript types inferred from schemas using `z.infer`

---

## Detailed Implementation Plan

### Phase 1: Create Base Schemas

**File:** `services/api/schemas.ts`

**Base Schemas to Create:**

```typescript
// Base field schemas
const BaseCountrySchema = z.object({
  id: z.number(),
  name: z.string(),
  nameHe: z.string(),
});

const BaseTripTypeSchema = z.object({
  id: z.number(),
  name: z.string(),
  nameHe: z.string(),
});

const BaseTagSchema = z.object({
  id: z.number(),
  name: z.string(),
  nameHe: z.string(),
  category: z.string(),
});

// Status enum
const TripStatusSchema = z.enum(['Open', 'Guaranteed', 'Last Places', 'Full', 'Cancelled']);

// Difficulty level
const DifficultyLevelSchema = z.union([z.literal(1), z.literal(2), z.literal(3), z.literal(4), z.literal(5)]);
```

---

### Phase 2: Create Entity Schemas

**Entity Schemas (Full Objects):**

```typescript
// Country schema
const CountrySchema: z.ZodType<Country> = BaseCountrySchema.extend({
  continent: z.string(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

// Guide schema
const GuideSchema: z.ZodType<Guide> = z.object({
  id: z.number(),
  name: z.string(),
  email: z.string(),
  phone: z.string().optional(),
  gender: z.string(),
  age: z.number().optional(),
  bio: z.string().optional(),
  bioHe: z.string().optional(),
  imageUrl: z.string().optional(),
  isActive: z.boolean(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

// Tag schema
const TagSchema: z.ZodType<Tag> = BaseTagSchema.extend({
  description: z.string().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

// TripType schema
const TripTypeSchema: z.ZodType<TripType> = BaseTripTypeSchema.extend({
  description: z.string().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

// Company schema
const CompanySchema: z.ZodType<Company> = z.object({
  id: z.number(),
  name: z.string(),
  nameHe: z.string(),
  description: z.string().optional(),
  descriptionHe: z.string().optional(),
  logoUrl: z.string().optional(),
  websiteUrl: z.string().optional(),
  email: z.string().optional(),
  phone: z.string().optional(),
  isActive: z.boolean(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

// TripTemplate schema (with optional relations)
const TripTemplateSchema: z.ZodType<TripTemplate> = z.object({
  id: z.number(),
  title: z.string(),
  titleHe: z.string(),
  description: z.string(),
  descriptionHe: z.string(),
  shortDescription: z.string().optional(),
  shortDescriptionHe: z.string().optional(),
  imageUrl: z.string().optional(),
  basePrice: z.number(),
  singleSupplementPrice: z.number().optional(),
  typicalDurationDays: z.number(),
  defaultMaxCapacity: z.number(),
  difficultyLevel: DifficultyLevelSchema,
  companyId: z.number(),
  tripTypeId: z.number().optional(),
  primaryCountryId: z.number().optional(),
  isActive: z.boolean(),
  properties: z.record(z.any()).optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
  // Optional relations
  company: CompanySchema.optional(),
  tripType: TripTypeSchema.optional(),
  primaryCountry: CountrySchema.optional(),
  countries: z.array(CountrySchema).optional(),
  tags: z.array(TagSchema).optional(),
  occurrences: z.lazy(() => z.array(TripOccurrenceSchema)).optional(),
});

// TripOccurrence schema (with optional relations)
const TripOccurrenceSchema: z.ZodType<TripOccurrence> = z.object({
  id: z.number(),
  tripTemplateId: z.number(),
  guideId: z.number().optional(),
  startDate: z.string(),
  endDate: z.string(),
  priceOverride: z.number().optional(),
  singleSupplementOverride: z.number().optional(),
  maxCapacityOverride: z.number().optional(),
  spotsLeft: z.number(),
  status: TripStatusSchema,
  imageUrlOverride: z.string().optional(),
  notes: z.string().optional(),
  notesHe: z.string().optional(),
  properties: z.record(z.any()).optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
  // Computed fields
  effectivePrice: z.number().optional(),
  effectiveMaxCapacity: z.number().optional(),
  effectiveImageUrl: z.string().optional(),
  durationDays: z.number().optional(),
  // Optional relations
  template: z.lazy(() => TripTemplateSchema).optional(),
  guide: GuideSchema.optional(),
});

// RecommendedTripOccurrence schema
const RecommendedTripOccurrenceSchema: z.ZodType<RecommendedTripOccurrence> = TripOccurrenceSchema.extend({
  match_score: z.number(),
  match_details: z.array(z.string()),
  is_relaxed: z.boolean().optional(),
});
```

---

### Phase 3: Create Response Wrapper Schemas

**Generic Response Schema:**

```typescript
// Generic ApiResponse schema factory
function createApiResponseSchema<T extends z.ZodTypeAny>(dataSchema: T) {
  return z.object({
    success: z.boolean(),
    data: dataSchema.optional(),
    count: z.number().optional(),
    total: z.number().optional(),
    error: z.string().optional(),
    message: z.string().optional(),
    api_version: z.string().optional(),
  });
}

// Specific response schemas
const CountryArrayResponseSchema = createApiResponseSchema(z.array(CountrySchema));
const CountryResponseSchema = createApiResponseSchema(CountrySchema);
const GuideArrayResponseSchema = createApiResponseSchema(z.array(GuideSchema));
const GuideResponseSchema = createApiResponseSchema(GuideSchema);
const TagArrayResponseSchema = createApiResponseSchema(z.array(TagSchema));
const TripTypeArrayResponseSchema = createApiResponseSchema(z.array(TripTypeSchema));
const CompanyArrayResponseSchema = createApiResponseSchema(z.array(CompanySchema));
const CompanyResponseSchema = createApiResponseSchema(CompanySchema);
const TripTemplateArrayResponseSchema = createApiResponseSchema(z.array(TripTemplateSchema));
const TripTemplateResponseSchema = createApiResponseSchema(TripTemplateSchema);
const TripOccurrenceArrayResponseSchema = createApiResponseSchema(z.array(TripOccurrenceSchema));
const TripOccurrenceResponseSchema = createApiResponseSchema(TripOccurrenceSchema);
const RecommendedTripOccurrenceArrayResponseSchema = createApiResponseSchema(z.array(RecommendedTripOccurrenceSchema));

// Special schemas for non-standard responses
const LocationsResponseSchema = z.object({
  success: z.boolean(),
  countries: z.array(CountrySchema).optional(),
  continents: z.array(z.object({
    value: z.string(),
    nameHe: z.string(),
  })).optional(),
  error: z.string().optional(),
  count: z.number().optional(),
});

const HealthCheckResponseSchema = z.object({
  status: z.string(),
  service: z.string(),
  version: z.string(),
  schema: z.string(),
  database: z.object({
    trip_occurrences: z.number(),
    trip_templates: z.number(),
    countries: z.number(),
    guides: z.number(),
    tags: z.number(),
    trip_types: z.number(),
  }),
});

const SchemaInfoResponseSchema = z.object({
  success: z.boolean(),
  schema_version: z.string(),
  statistics: z.object({
    companies: z.number(),
    templates: z.number(),
    occurrences: z.number(),
    active_occurrences: z.number(),
  }),
  endpoints: z.record(z.string()),
  error: z.string().optional(),
});
```

---

### Phase 4: Export Schemas

**Export all schemas for use in API functions:**

```typescript
// Export all entity schemas
export {
  CountrySchema,
  GuideSchema,
  TagSchema,
  TripTypeSchema,
  CompanySchema,
  TripTemplateSchema,
  TripOccurrenceSchema,
  RecommendedTripOccurrenceSchema,
};

// Export all response schemas
export {
  CountryArrayResponseSchema,
  CountryResponseSchema,
  GuideArrayResponseSchema,
  GuideResponseSchema,
  TagArrayResponseSchema,
  TripTypeArrayResponseSchema,
  CompanyArrayResponseSchema,
  CompanyResponseSchema,
  TripTemplateArrayResponseSchema,
  TripTemplateResponseSchema,
  TripOccurrenceArrayResponseSchema,
  TripOccurrenceResponseSchema,
  RecommendedTripOccurrenceArrayResponseSchema,
  LocationsResponseSchema,
  HealthCheckResponseSchema,
  SchemaInfoResponseSchema,
};
```

---

### Phase 5: Integrate Schemas into API Functions

#### 5.1 System API (`system.ts`)

**Update `healthCheck`:**

```typescript
import { apiFetch } from './client';
import { HealthCheckResponseSchema } from './schemas';
import type { ApiResponse } from './types';

export async function healthCheck(): Promise<ApiResponse> {
  return apiFetch('/api/health', undefined, 0, HealthCheckResponseSchema);
}
```

---

#### 5.2 Resources API (`resources.ts`)

**Update all functions:**

```typescript
import { apiFetch } from './client';
import {
  CountryArrayResponseSchema,
  CountryResponseSchema,
  GuideArrayResponseSchema,
  GuideResponseSchema,
  TagArrayResponseSchema,
  TripTypeArrayResponseSchema,
  LocationsResponseSchema,
} from './schemas';
import type { ApiResponse, Country, Guide, Tag, TripType } from './types';

export async function getCountries(continent?: string): Promise<ApiResponse<Country[]>> {
  const query = continent ? `?continent=${continent}` : '';
  return apiFetch<Country[]>(`/api/countries${query}`, undefined, 0, CountryArrayResponseSchema);
}

export async function getLocations(): Promise<ApiResponse<{
  countries: Country[];
  continents: Array<{ value: string; nameHe: string }>;
}>> {
  const response = await apiFetch<any>('/api/locations', undefined, 0, LocationsResponseSchema) as any;
  
  // ... existing transformation logic ...
  
  return {
    success: true,
    data: {
      countries: countries.map((c) => ({
        id: c.id,
        name: c.name,
        nameHe: c.name_he || c.nameHe || c.name,
        continent: c.continent,
        createdAt: '',
        updatedAt: '',
      })),
      continents: continents,
    },
  };
}

export async function getCountry(id: number): Promise<ApiResponse<Country>> {
  return apiFetch<Country>(`/api/countries/${id}`, undefined, 0, CountryResponseSchema);
}

export async function getGuides(): Promise<ApiResponse<Guide[]>> {
  return apiFetch<Guide[]>('/api/guides', undefined, 0, GuideArrayResponseSchema);
}

export async function getGuide(id: number): Promise<ApiResponse<Guide>> {
  return apiFetch<Guide>(`/api/guides/${id}`, undefined, 0, GuideResponseSchema);
}

export async function getTags(): Promise<ApiResponse<Tag[]>> {
  return apiFetch<Tag[]>('/api/tags', undefined, 0, TagArrayResponseSchema);
}

export async function getTripTypes(): Promise<ApiResponse<TripType[]>> {
  return apiFetch<TripType[]>('/api/trip-types', undefined, 0, TripTypeArrayResponseSchema);
}
```

---

#### 5.3 V2 API (`v2.ts`)

**Update all functions:**

```typescript
import { apiFetch, camelToSnake, camelToSnakeObject, API_VERSION } from './client';
import {
  CompanyArrayResponseSchema,
  CompanyResponseSchema,
  TripTemplateArrayResponseSchema,
  TripTemplateResponseSchema,
  TripOccurrenceArrayResponseSchema,
  TripOccurrenceResponseSchema,
  RecommendedTripOccurrenceArrayResponseSchema,
  SchemaInfoResponseSchema,
} from './schemas';
import type { 
  ApiResponse, 
  Company, 
  TripTemplate, 
  TripOccurrence, 
  TripFilters,
  RecommendationPreferences,
  RecommendedTripOccurrence
} from './types';

export async function getCompanies(): Promise<ApiResponse<Company[]>> {
  return apiFetch<Company[]>(`${API_VERSION}/companies`, undefined, 0, CompanyArrayResponseSchema);
}

export async function getCompany(id: number): Promise<ApiResponse<Company>> {
  return apiFetch<Company>(`${API_VERSION}/companies/${id}`, undefined, 0, CompanyResponseSchema);
}

export async function getTemplates(filters?: {
  companyId?: number;
  tripTypeId?: number;
  countryId?: number;
  difficulty?: number;
  includeOccurrences?: boolean;
  limit?: number;
  offset?: number;
}): Promise<ApiResponse<TripTemplate[]>> {
  // ... existing filter logic ...
  return apiFetch<TripTemplate[]>(`${API_VERSION}/templates${query}`, undefined, 0, TripTemplateArrayResponseSchema);
}

export async function getTemplate(id: number): Promise<ApiResponse<TripTemplate>> {
  return apiFetch<TripTemplate>(`${API_VERSION}/templates/${id}`, undefined, 0, TripTemplateResponseSchema);
}

export async function getOccurrences(filters?: {
  templateId?: number;
  guideId?: number;
  status?: string;
  startDate?: string;
  endDate?: string;
  year?: number;
  month?: number;
  maxPrice?: number;
  includeTemplate?: boolean;
  limit?: number;
  offset?: number;
}): Promise<ApiResponse<TripOccurrence[]>> {
  // ... existing filter logic ...
  return apiFetch<TripOccurrence[]>(`${API_VERSION}/occurrences${query}`, undefined, 0, TripOccurrenceArrayResponseSchema);
}

export async function getOccurrence(id: number): Promise<ApiResponse<TripOccurrence>> {
  return apiFetch<TripOccurrence>(`${API_VERSION}/occurrences/${id}`, undefined, 0, TripOccurrenceResponseSchema);
}

export async function getTripOccurrences(filters?: TripFilters): Promise<ApiResponse<TripOccurrence[]>> {
  // ... existing filter logic ...
  return apiFetch<TripOccurrence[]>(`${API_VERSION}/trip-occurrences${query}`, undefined, 0, TripOccurrenceArrayResponseSchema);
}

export async function getTripOccurrence(id: number): Promise<ApiResponse<TripOccurrence>> {
  return apiFetch<TripOccurrence>(`${API_VERSION}/occurrences/${id}`, undefined, 0, TripOccurrenceResponseSchema);
}

export async function getRecommendations(
  preferences: RecommendationPreferences
): Promise<ApiResponse<RecommendedTripOccurrence[]>> {
  const requestBody = camelToSnakeObject(preferences);
  return apiFetch<RecommendedTripOccurrence[]>(
    `${API_VERSION}/recommendations`, 
    {
      method: 'POST',
      body: JSON.stringify(requestBody),
    },
    0,
    RecommendedTripOccurrenceArrayResponseSchema
  );
}

export async function getSchemaInfo(): Promise<ApiResponse<{
  schema_version: string;
  statistics: {
    companies: number;
    templates: number;
    occurrences: number;
    active_occurrences: number;
  };
  endpoints: Record<string, string>;
}>> {
  return apiFetch(`${API_VERSION}/schema-info`, undefined, 0, SchemaInfoResponseSchema);
}
```

---

## Implementation Checklist

### Phase 1: Create Schemas File and Update Types ✅ COMPLETED
- [x] Create `services/api/schemas.ts`
- [x] Define base schemas (BaseCountrySchema, BaseTripTypeSchema, BaseTagSchema, TripStatusSchema, DifficultyLevelSchema)
- [x] Define entity schemas (CountrySchema, GuideSchema, TagSchema, TripTypeSchema, CompanySchema)
- [x] Define complex entity schemas (TripTemplateSchema, TripOccurrenceSchema, RecommendedTripOccurrenceSchema)
  - [x] Handle circular references using `z.any()` for circular fields (template/occurrences)
- [x] Create response wrapper schemas
- [x] Create special schemas (LocationsResponseSchema, HealthCheckResponseSchema, SchemaInfoResponseSchema)
- [x] Export all schemas
- [x] **Update `types.ts` to infer types from schemas using `z.infer<typeof Schema>`**
- [x] Remove manually defined interfaces (replaced with inferred types)

**Note:** Circular reference fields (`template` in TripOccurrence, `occurrences` in TripTemplate) use `z.any()` to avoid circular dependency issues. This provides basic structure validation while allowing the circular references.

### Phase 2: Update System API
- [ ] Import schemas in `system.ts`
- [ ] Update `healthCheck()` to pass `HealthCheckResponseSchema`

### Phase 3: Update Resources API
- [ ] Import schemas in `resources.ts`
- [ ] Update `getCountries()` to pass `CountryArrayResponseSchema`
- [ ] Update `getLocations()` to pass `LocationsResponseSchema`
- [ ] Update `getCountry()` to pass `CountryResponseSchema`
- [ ] Update `getGuides()` to pass `GuideArrayResponseSchema`
- [ ] Update `getGuide()` to pass `GuideResponseSchema`
- [ ] Update `getTags()` to pass `TagArrayResponseSchema`
- [ ] Update `getTripTypes()` to pass `TripTypeArrayResponseSchema`

### Phase 4: Update V2 API
- [ ] Import schemas in `v2.ts`
- [ ] Update `getCompanies()` to pass `CompanyArrayResponseSchema`
- [ ] Update `getCompany()` to pass `CompanyResponseSchema`
- [ ] Update `getTemplates()` to pass `TripTemplateArrayResponseSchema`
- [ ] Update `getTemplate()` to pass `TripTemplateResponseSchema`
- [ ] Update `getOccurrences()` to pass `TripOccurrenceArrayResponseSchema`
- [ ] Update `getOccurrence()` to pass `TripOccurrenceResponseSchema`
- [ ] Update `getTripOccurrences()` to pass `TripOccurrenceArrayResponseSchema`
- [ ] Update `getTripOccurrence()` to pass `TripOccurrenceResponseSchema`
- [ ] Update `getRecommendations()` to pass `RecommendedTripOccurrenceArrayResponseSchema`
- [ ] Update `getSchemaInfo()` to pass `SchemaInfoResponseSchema`

### Phase 5: Testing and Validation
- [ ] Test all API calls in development mode
- [ ] Verify validation errors are logged correctly
- [ ] Test with invalid API responses (mock server)
- [ ] Verify validation is skipped in production mode
- [ ] Test TypeScript compilation
- [ ] Verify no runtime errors

---

## Special Considerations

### 1. Circular References

**Issue:** `TripTemplate` includes `occurrences?: TripOccurrence[]` and `TripOccurrence` includes `template?: TripTemplate`.

**Solution:** Use `z.lazy()` for circular references:

```typescript
const TripTemplateSchema = z.object({
  // ... fields ...
  occurrences: z.lazy(() => z.array(TripOccurrenceSchema)).optional(),
});

const TripOccurrenceSchema = z.object({
  // ... fields ...
  template: z.lazy(() => TripTemplateSchema).optional(),
});
```

### 2. Optional Relations

Many entities have optional relation fields. Use `.optional()` on relation schemas:

```typescript
company: CompanySchema.optional(),
tripType: TripTypeSchema.optional(),
primaryCountry: CountrySchema.optional(),
countries: z.array(CountrySchema).optional(),
tags: z.array(TagSchema).optional(),
```

### 3. Non-Standard Responses

Some endpoints return non-standard formats:

- **`/api/locations`** - Returns `{ countries: [...], continents: [...] }` at top level
- **`/api/health`** - Returns `{ status, service, version, database }` instead of `{ success, data }`

**Solution:** Create specific schemas for these endpoints.

### 4. Partial Validation

For endpoints that return partial objects or transformed data, create specific schemas:

```typescript
// For getLocations - countries might have missing createdAt/updatedAt
const LocationCountrySchema = CountrySchema.omit({ createdAt: true, updatedAt: true }).extend({
  createdAt: z.string().default(''),
  updatedAt: z.string().default(''),
});
```

### 5. Validation Error Handling

Validation errors are logged but don't break the application:

- Invalid responses are still returned (graceful degradation)
- Errors are logged to console in development only
- Production code continues to work even if validation fails

---

## Benefits

### 1. Early Error Detection
- Catch API contract violations during development
- Detect mismatches between backend and frontend types
- Find issues before they reach production

### 2. Better Debugging
- Clear validation error messages with field-level details
- Know exactly which fields are invalid
- Understand API response structure issues

### 3. Type Safety
- Runtime validation complements TypeScript compile-time types
- Catch issues that TypeScript can't detect (dynamic API responses)
- Ensure API responses match expected structure

### 4. Documentation
- Zod schemas serve as living documentation of API contracts
- Clear definition of expected response structure
- Self-documenting API types

### 5. Zero Production Impact
- Validation only runs in development mode
- No performance overhead in production
- No bundle size increase (validation code tree-shaken in production)

---

## Testing Strategy

### Manual Testing
1. **Test in Development Mode:**
   - Call each API endpoint
   - Verify validation passes for valid responses
   - Check console for validation logs

2. **Test Invalid Responses:**
   - Mock invalid API responses
   - Verify validation errors are logged
   - Verify application continues to work (graceful degradation)

3. **Test in Production Mode:**
   - Verify validation is skipped
   - Verify no console logs appear
   - Verify application works normally

### Automated Testing (Future)
- Create test suite for Zod schemas
- Test schema validation with various inputs
- Test edge cases (null, undefined, missing fields)

---

## Migration Notes

### Breaking Changes
- None - validation is additive and optional

### Performance
- No impact in production (validation skipped)
- Minimal impact in development (only during API calls)

### Backward Compatibility
- All existing code continues to work
- Validation is transparent to consumers
- No changes needed to consuming code

---

## Estimated Effort

### Phase 1: Create Schemas (2-3 hours)
- Define base schemas
- Define entity schemas
- Handle circular references
- Create response wrappers

### Phase 2-4: Integrate Schemas (1-2 hours)
- Update system.ts
- Update resources.ts
- Update v2.ts

### Phase 5: Testing (1 hour)
- Test all endpoints
- Verify error messages
- Test edge cases

**Total Estimated Time: 4-6 hours**

---

## Next Steps

1. **Review and approve this plan**
2. **Create `services/api/schemas.ts`** with all schemas
3. **Update API functions** to pass schemas
4. **Test validation** in development mode
5. **Verify production mode** skips validation
6. **Document any schema adjustments** needed based on actual API responses

---

## References

- Zod Documentation: https://zod.dev/
- Current API Types: `frontend/src/services/api/types.ts`
- API Client: `frontend/src/services/api/client.ts`
- API Structure: `docs/api/API_STRUCTURE.md`
