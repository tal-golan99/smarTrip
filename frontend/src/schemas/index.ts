/**
 * Barrel export for schemas
 * 
 * Central export point for all Zod schemas, mirroring backend's __init__.py pattern.
 * This allows importing from a single location:
 *   import { CountrySchema, TripTemplateSchema } from './schemas'
 */

// Base schemas
export {
  BaseCountrySchema,
  BaseTripTypeSchema,
  BaseTagSchema,
  TripStatusSchema,
  DifficultyLevelSchema,
} from './base';

// Resource schemas
export {
  CountrySchema,
  GuideSchema,
  TagSchema,
  TripTypeSchema,
  CompanySchema,
  CountryArrayResponseSchema,
  CountryResponseSchema,
  GuideArrayResponseSchema,
  GuideResponseSchema,
  TagArrayResponseSchema,
  TripTypeArrayResponseSchema,
  CompanyArrayResponseSchema,
  CompanyResponseSchema,
  LocationsResponseSchema,
} from './resources';

// Trip schemas
export {
  TripTemplateSchema,
  TripOccurrenceSchema,
  RecommendedTripOccurrenceSchema,
  TripTemplateArrayResponseSchema,
  TripTemplateResponseSchema,
  TripOccurrenceArrayResponseSchema,
  TripOccurrenceResponseSchema,
  RecommendedTripOccurrenceArrayResponseSchema,
  HealthCheckResponseSchema,
  SchemaInfoResponseSchema,
} from './trip';

// Event schemas
export {
  SessionStartRequestSchema,
  SessionStartResponseSchema,
  EventRequestSchema,
  EventResponseSchema,
  EventBatchRequestSchema,
  EventBatchResponseSchema,
  UserIdentifyRequestSchema,
  UserIdentifyResponseSchema,
  EventTypesResponseSchema,
} from './events';

// Analytics schemas
export {
  EvaluationRunRequestSchema,
  MetricsResponseSchema,
  DailyMetricsResponseSchema,
  TopSearchesResponseSchema,
  EvaluationRunResponseSchema,
  EvaluationScenarioSchema,
  EvaluationScenariosResponseSchema,
} from './analytics';