/**
 * Trip schemas
 * 
 * Schemas for trip-related entities:
 * - TripTemplate, TripOccurrence, RecommendedTripOccurrence
 * - Response wrapper schemas for trip endpoints
 * - Special response schemas (HealthCheckResponseSchema, SchemaInfoResponseSchema)
 * 
 * Note: Uses z.lazy() to handle circular dependencies between TripTemplate and TripOccurrence.
 */

import { z } from 'zod';
import { TripStatusSchema, DifficultyLevelSchema } from './base';
import { GuideSchema, CompanySchema, TripTypeSchema, CountrySchema, TagSchema } from './resources';

// ============================================
// CIRCULAR REFERENCE SCHEMAS (using z.lazy())
// ============================================

/**
 * TripTemplate schema (defined first, references TripOccurrenceSchema via lazy)
 * Note: Circular reference fields (occurrences) use z.lazy() to prevent circular dependency issues
 */
export const TripTemplateSchema: z.ZodType<any> = z.object({
  id: z.number(),
  title: z.string(),
  titleHe: z.string(),
  description: z.string(),
  descriptionHe: z.string(),
  shortDescription: z.string().nullable().optional(),
  shortDescriptionHe: z.string().nullable().optional(),
  imageUrl: z.string().nullable().optional(),
  basePrice: z.union([z.number(), z.string()]).transform((val) => typeof val === 'string' ? parseFloat(val) : val),
  singleSupplementPrice: z.union([z.number(), z.string()]).transform((val) => typeof val === 'string' ? parseFloat(val) : val).nullable().optional(),
  typicalDurationDays: z.number(),
  defaultMaxCapacity: z.number(),
  difficultyLevel: DifficultyLevelSchema,
  companyId: z.number(),
  tripTypeId: z.number().nullable().optional(),
  primaryCountryId: z.number().nullable().optional(),
  isActive: z.boolean(),
  properties: z.record(z.string(), z.any()).nullable().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
  // Optional relations (occurrences uses lazy for circular reference, others are validated)
  company: CompanySchema.nullable().optional(),
  tripType: TripTypeSchema.nullable().optional(),
  primaryCountry: CountrySchema.nullable().optional(),
  countries: z.array(CountrySchema).optional(),
  tags: z.array(TagSchema).optional(),
  // Lazy reference to TripOccurrenceSchema (defined below)
  occurrences: z.lazy(() => z.array(TripOccurrenceSchema)).optional(),
}).passthrough(); // Allow additional fields from backend

/**
 * TripOccurrence schema
 * Note: Circular reference fields (template) use z.lazy() to prevent circular dependency issues
 */
export const TripOccurrenceSchema: z.ZodType<any> = z.object({
  id: z.number(),
  tripTemplateId: z.number(),
  guideId: z.number().nullable().optional(),
  startDate: z.string(),
  endDate: z.string(),
  priceOverride: z.union([z.number(), z.string()]).transform((val) => typeof val === 'string' ? parseFloat(val) : val).nullable().optional(),
  singleSupplementOverride: z.union([z.number(), z.string()]).transform((val) => typeof val === 'string' ? parseFloat(val) : val).nullable().optional(),
  maxCapacityOverride: z.number().nullable().optional(),
  spotsLeft: z.number(),
  status: TripStatusSchema,
  imageUrlOverride: z.string().nullable().optional(),
  notes: z.string().nullable().optional(),
  notesHe: z.string().nullable().optional(),
  properties: z.record(z.string(), z.any()).nullable().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
  // Computed fields (backend sends Decimal as string)
  effectivePrice: z.union([z.number(), z.string()]).transform((val) => typeof val === 'string' ? parseFloat(val) : val).nullable().optional(),
  effectiveMaxCapacity: z.number().nullable().optional(),
  effectiveImageUrl: z.string().nullable().optional(),
  durationDays: z.number().nullable().optional(),
  // Optional relations (template uses lazy for circular reference, guide is validated)
  template: z.lazy(() => TripTemplateSchema).nullable().optional(),
  guide: GuideSchema.nullable().optional(),
}).passthrough(); // Allow additional fields from backend

/**
 * RecommendedTripOccurrence schema
 * Note: Includes all TripOccurrence fields plus recommendation-specific fields
 * Uses z.lazy() for template field to handle circular reference
 * Uses .passthrough() to allow additional fields from backend
 */
export const RecommendedTripOccurrenceSchema: z.ZodType<any> = z.object({
  id: z.number(),
  tripTemplateId: z.number(),
  guideId: z.number().nullable().optional(),
  startDate: z.string(),
  endDate: z.string(),
  priceOverride: z.union([z.number(), z.string()]).transform((val) => typeof val === 'string' ? parseFloat(val) : val).nullable().optional(),
  singleSupplementOverride: z.union([z.number(), z.string()]).transform((val) => typeof val === 'string' ? parseFloat(val) : val).nullable().optional(),
  maxCapacityOverride: z.number().nullable().optional(),
  spotsLeft: z.number(),
  status: TripStatusSchema,
  imageUrlOverride: z.string().nullable().optional(),
  notes: z.string().nullable().optional(),
  notesHe: z.string().nullable().optional(),
  properties: z.record(z.string(), z.any()).nullable().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
  // Computed fields (backend sends Decimal as string)
  effectivePrice: z.union([z.number(), z.string()]).transform((val) => typeof val === 'string' ? parseFloat(val) : val).nullable().optional(),
  effectiveMaxCapacity: z.number().nullable().optional(),
  effectiveImageUrl: z.string().nullable().optional(),
  durationDays: z.number().nullable().optional(),
  // Optional relations (template uses lazy for circular reference, guide is validated)
  template: z.lazy(() => TripTemplateSchema).nullable().optional(),
  guide: GuideSchema.nullable().optional(),
  // Recommendation-specific fields
  match_score: z.number(),
  match_details: z.array(z.string()).optional(), // Sometimes might be missing
  is_relaxed: z.boolean().optional(),
}).passthrough(); // Allow additional fields from backend

// ============================================
// RESPONSE WRAPPER SCHEMAS
// ============================================

/**
 * Generic ApiResponse schema factory
 */
function createApiResponseSchema<T extends z.ZodTypeAny>(dataSchema: T) {
  return z.object({
    success: z.boolean(),
    data: dataSchema.optional(),
    count: z.number().nullable().optional(),
    total: z.number().nullable().optional(),
    error: z.string().nullable().optional(), // Can be null or undefined
    message: z.string().nullable().optional(), // Can be null or undefined
    api_version: z.string().nullable().optional(),
  }).passthrough(); // Allow additional fields like primary_count, relaxed_count, etc.
}

/**
 * Trip response schemas
 */
export const TripTemplateArrayResponseSchema = createApiResponseSchema(z.array(TripTemplateSchema));
export const TripTemplateResponseSchema = createApiResponseSchema(TripTemplateSchema);
export const TripOccurrenceArrayResponseSchema = createApiResponseSchema(z.array(TripOccurrenceSchema));
export const TripOccurrenceResponseSchema = createApiResponseSchema(TripOccurrenceSchema);
export const RecommendedTripOccurrenceArrayResponseSchema = createApiResponseSchema(z.array(RecommendedTripOccurrenceSchema));

// ============================================
// SPECIAL RESPONSE SCHEMAS
// ============================================

/**
 * Health check response schema (non-standard format)
 * Returns: { status, service, version, schema, database }
 */
export const HealthCheckResponseSchema = z.object({
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

/**
 * Schema info response schema
 */
export const SchemaInfoResponseSchema = z.object({
  success: z.boolean(),
  schema_version: z.string(),
  statistics: z.object({
    companies: z.number(),
    templates: z.number(),
    occurrences: z.number(),
    active_occurrences: z.number(),
  }),
  endpoints: z.record(z.string(), z.string()),
  error: z.string().optional(),
});