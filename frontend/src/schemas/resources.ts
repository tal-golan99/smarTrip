/**
 * Resource schemas
 * 
 * Schemas for reference data entities:
 * - Country, Guide, Tag, TripType, Company
 * - Response wrapper schemas for each resource
 */

import { z } from 'zod';
import { BaseCountrySchema, BaseTripTypeSchema, BaseTagSchema } from './base';

// ============================================
// ENTITY SCHEMAS
// ============================================

/**
 * Country schema (full entity)
 */
export const CountrySchema = BaseCountrySchema.extend({
  continent: z.string(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

/**
 * Guide schema
 */
export const GuideSchema = z.object({
  id: z.number(),
  name: z.string(),
  email: z.string(),
  phone: z.string().nullable().optional(),
  gender: z.string(),
  age: z.number().nullable().optional(),
  bio: z.string().nullable().optional(),
  bioHe: z.string().nullable().optional(),
  imageUrl: z.string().nullable().optional(),
  isActive: z.boolean(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

/**
 * Tag schema (full entity)
 */
export const TagSchema = BaseTagSchema.extend({
  description: z.string().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

/**
 * TripType schema (full entity)
 */
export const TripTypeSchema = BaseTripTypeSchema.extend({
  description: z.string().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

/**
 * Company schema
 */
export const CompanySchema = z.object({
  id: z.number(),
  name: z.string(),
  nameHe: z.string(),
  description: z.string().nullable().optional(),
  descriptionHe: z.string().nullable().optional(),
  logoUrl: z.string().nullable().optional(),
  websiteUrl: z.string().nullable().optional(),
  email: z.string().nullable().optional(),
  phone: z.string().nullable().optional(),
  isActive: z.boolean(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

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
 * Resource response schemas
 */
export const CountryArrayResponseSchema = createApiResponseSchema(z.array(CountrySchema));
export const CountryResponseSchema = createApiResponseSchema(CountrySchema);
export const GuideArrayResponseSchema = createApiResponseSchema(z.array(GuideSchema));
export const GuideResponseSchema = createApiResponseSchema(GuideSchema);
export const TagArrayResponseSchema = createApiResponseSchema(z.array(TagSchema));
export const TripTypeArrayResponseSchema = createApiResponseSchema(z.array(TripTypeSchema));
export const CompanyArrayResponseSchema = createApiResponseSchema(z.array(CompanySchema));
export const CompanyResponseSchema = createApiResponseSchema(CompanySchema);

// ============================================
// SPECIAL RESPONSE SCHEMAS
// ============================================

/**
 * Locations response schema (non-standard format)
 * Returns: { success: true, countries: [...], continents: [...] }
 */
export const LocationsResponseSchema = z.object({
  success: z.boolean(),
  countries: z.array(z.object({
    id: z.number(),
    name: z.string(),
    name_he: z.string().optional(),
    nameHe: z.string().optional(),
    continent: z.string(),
  })).optional(),
  continents: z.array(z.object({
    value: z.string(),
    nameHe: z.string(),
  })).optional(),
  error: z.string().optional(),
  count: z.number().optional(),
});