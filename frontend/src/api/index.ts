/**
 * Main export file for API service
 * Re-exports all modules for convenient importing
 */

// Export all types
export type * from './types';

// Export system API
export { healthCheck } from './system';

// Export resources API
export { 
  getCountries, 
  getLocations, 
  getCountry, 
  getGuides, 
  getGuide, 
  getTags, 
  getTripTypes 
} from './resources';

// Export V2 API
export {
  getCompanies,
  getCompany,
  getTemplates,
  getTemplate,
  getOccurrences,
  getOccurrence,
  getTripOccurrences,
  getTripOccurrence,
  getRecommendations,
  getSchemaInfo
} from './v2';

// Export events API
export {
  startSession,
  trackEvent,
  trackEventsBatch,
  identifyUser,
  getEventTypes
} from './events';

// Export analytics API
export {
  getMetrics,
  getDailyMetrics,
  getTopSearches,
  runEvaluation,
  getEvaluationScenarios
} from './analytics';
