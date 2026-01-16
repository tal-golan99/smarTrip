/**
 * Base Zod schemas
 * 
 * Core schemas used across multiple entity schemas:
 * - Base entity schemas (BaseCountrySchema, BaseTripTypeSchema, BaseTagSchema)
 * - Enums (TripStatusSchema, DifficultyLevelSchema)
 */

import { z } from 'zod';

// ============================================
// BASE ENTITY SCHEMAS
// ============================================

/**
 * Base country schema (core fields only)
 */
export const BaseCountrySchema = z.object({
  id: z.number(),
  name: z.string(),
  nameHe: z.string(),
});

/**
 * Base trip type schema (core fields only)
 */
export const BaseTripTypeSchema = z.object({
  id: z.number(),
  name: z.string(),
  nameHe: z.string(),
});

/**
 * Base tag schema (core fields only)
 * Note: category is optional as backend may not always include it
 */
export const BaseTagSchema = z.object({
  id: z.number(),
  name: z.string(),
  nameHe: z.string(),
  category: z.string().optional(), // Optional - backend may not always include this
});

// ============================================
// ENUM SCHEMAS
// ============================================

/**
 * Trip status enum
 * Note: Backend uses VARCHAR, so we accept any string but validate against known values
 */
export const TripStatusSchema = z.union([
  z.literal('Open'),
  z.literal('Guaranteed'),
  z.literal('Last Places'),
  z.literal('Full'),
  z.literal('Cancelled'),
  z.string(), // Fallback for any other status value from backend
]);

/**
 * Difficulty level (1-5)
 */
export const DifficultyLevelSchema = z.union([
  z.literal(1),
  z.literal(2),
  z.literal(3),
  z.literal(4),
  z.literal(5),
]);