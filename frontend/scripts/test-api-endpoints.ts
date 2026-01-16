/**
 * API Endpoints Test Script
 * 
 * Tests all API endpoints to ensure they're working correctly.
 * Uses the actual API client functions for realistic testing.
 */

// Import API functions directly to avoid Next.js/React dependencies
import { healthCheck } from '../src/api/system';
import { 
  getCountries, 
  getLocations, 
  getCountry, 
  getGuides, 
  getTags, 
  getTripTypes 
} from '../src/api/resources';
import {
  startSession,
  trackEventsBatch,
  getEventTypes
} from '../src/api/events';
import {
  getMetrics,
  getDailyMetrics,
  getTopSearches,
  getEvaluationScenarios
} from '../src/api/analytics';
import {
  getCompanies,
  getTemplates,
  getOccurrences,
  getSchemaInfo
} from '../src/api/v2';

// Create namespace for easier access
const api = {
  healthCheck,
  getCountries,
  getLocations,
  getCountry,
  getGuides,
  getTags,
  getTripTypes,
  startSession,
  trackEventsBatch,
  getEventTypes,
  getMetrics,
  getDailyMetrics,
  getTopSearches,
  getEvaluationScenarios,
  getCompanies,
  getTemplates,
  getOccurrences,
  getSchemaInfo,
};

// ============================================
// CONFIGURATION
// ============================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

interface TestResult {
  name: string;
  success: boolean;
  error?: string;
  statusCode?: number;
  responseTime?: number;
}

const results: TestResult[] = [];

// ============================================
// TEST UTILITIES
// ============================================

function logResult(result: TestResult) {
  results.push(result);
  const status = result.success ? '✓' : '✗';
  const time = result.responseTime ? ` (${result.responseTime}ms)` : '';
  console.log(`${status} ${result.name}${time}`);
  if (!result.success && result.error) {
    console.log(`  Error: ${result.error}`);
  }
}

async function testEndpoint<T>(
  name: string,
  testFn: () => Promise<T>,
  logResponse = false
): Promise<void> {
  const startTime = Date.now();
  try {
    const result = await testFn();
    const responseTime = Date.now() - startTime;
    if (logResponse && result) {
      console.log(`  Response:`, JSON.stringify(result, null, 2).substring(0, 200));
    }
    logResult({
      name,
      success: true,
      responseTime,
    });
  } catch (error: any) {
    const responseTime = Date.now() - startTime;
    const errorMessage = error?.message || String(error);
    logResult({
      name,
      success: false,
      error: errorMessage,
      statusCode: error?.response?.status,
      responseTime,
    });
    // Log actual response if available for debugging
    if (error?.response?.data) {
      console.log(`  Actual response:`, JSON.stringify(error.response.data, null, 2).substring(0, 300));
    }
  }
}

// ============================================
// SYSTEM API TESTS
// ============================================

async function testSystemAPI() {
  console.log('\n=== SYSTEM API ===\n');

  await testEndpoint('GET /api/health', async () => {
    const response = await api.healthCheck();
    // Health check endpoint returns non-standard format: { status, service, version, schema, database }
    // It doesn't use the standard { success, data } wrapper
    if (!response || typeof response !== 'object') {
      throw new Error('Health check failed - invalid response format');
    }
    // Check for either standard format or non-standard format
    const responseData = response.data || response;
    if (response.success !== undefined) {
      if (!response.success) {
        throw new Error('Health check returned success: false');
      }
      // Standard format - check data object
      if (responseData && typeof responseData === 'object' && !responseData.status) {
        throw new Error('Invalid health check response - missing status field');
      }
    } else if (!responseData || typeof responseData !== 'object' || typeof (responseData as any).status !== 'string') {
      throw new Error('Invalid health check response - missing status field');
    }
  }, true);
}

// ============================================
// RESOURCES API TESTS
// ============================================

async function testResourcesAPI() {
  console.log('\n=== RESOURCES API ===\n');

  await testEndpoint('GET /api/locations', async () => {
    const response = await api.getLocations() as any;
    // getLocations() maps backend response to standard format: { success, data: { countries, continents } }
    if (!response.success) {
      throw new Error('Failed to get locations');
    }
    // Response data has countries and continents in data field
    if (!response.data) {
      throw new Error('Invalid locations response - missing data field');
    }
    if (!response.data.countries || !Array.isArray(response.data.countries)) {
      throw new Error('Invalid locations response - missing countries array');
    }
    if (!response.data.continents || !Array.isArray(response.data.continents)) {
      throw new Error('Invalid locations response - missing continents array');
    }
  }, true);

  await testEndpoint('GET /api/countries', async () => {
    const response = await api.getCountries();
    if (!response.success) {
      throw new Error('Failed to get countries');
    }
    if (!response.data || !Array.isArray(response.data)) {
      throw new Error('Invalid countries response');
    }
  });

  await testEndpoint('GET /api/guides', async () => {
    const response = await api.getGuides();
    if (!response.success) {
      throw new Error('Failed to get guides');
    }
    if (!response.data || !Array.isArray(response.data)) {
      throw new Error('Invalid guides response');
    }
  });

  await testEndpoint('GET /api/tags', async () => {
    const response = await api.getTags();
    if (!response.success) {
      throw new Error('Failed to get tags');
    }
    if (!response.data || !Array.isArray(response.data)) {
      throw new Error('Invalid tags response');
    }
  });

  await testEndpoint('GET /api/trip-types', async () => {
    const response = await api.getTripTypes();
    if (!response.success) {
      throw new Error('Failed to get trip types');
    }
    if (!response.data || !Array.isArray(response.data)) {
      throw new Error('Invalid trip types response');
    }
  });

  // Test getting a specific country (use first country if available)
  await testEndpoint('GET /api/countries/:id', async () => {
    const countriesResponse = await api.getCountries();
    if (countriesResponse.success && countriesResponse.data && countriesResponse.data.length > 0) {
      const countryId = countriesResponse.data[0].id;
      const response = await api.getCountry(countryId);
      if (!response.success) {
        throw new Error('Failed to get country by ID');
      }
      if (!response.data || response.data.id !== countryId) {
        throw new Error('Invalid country response');
      }
    } else {
      throw new Error('No countries available to test with');
    }
  });
}

// ============================================
// EVENTS API TESTS
// ============================================

async function testEventsAPI() {
  console.log('\n=== EVENTS API ===\n');

  // Generate test UUIDs
  const testSessionId = '00000000-0000-0000-0000-000000000001';
  const testAnonymousId = '00000000-0000-0000-0000-000000000002';

  await testEndpoint('POST /api/session/start', async () => {
    const response = await api.startSession({
      sessionId: testSessionId,
      anonymousId: testAnonymousId,
      deviceType: 'desktop',
      referrer: 'http://test.example.com',
    });
    if (!response.success) {
      throw new Error('Failed to start session');
    }
    // Response data should have userId, sessionId, isNewSession (in camelCase from API client)
    if (!response.data) {
      throw new Error('Invalid session start response - missing data field');
    }
    const data = response.data as any;
    if (data.userId === undefined && data.user_id === undefined) {
      throw new Error('Invalid session start response - missing userId');
    }
    if (!data.sessionId && !data.session_id) {
      throw new Error('Invalid session start response - missing sessionId');
    }
  }, true);

  await testEndpoint('POST /api/events/batch', async () => {
    const response = await api.trackEventsBatch({
      events: [
        {
          eventType: 'page_view',
          sessionId: testSessionId,
          anonymousId: testAnonymousId,
          pageUrl: '/test',
          referrer: 'http://test.example.com',
          clientTimestamp: new Date().toISOString(),
        },
      ],
    });
    if (!response.success) {
      throw new Error('Failed to track events batch');
    }
    if (response.data && response.data.processed === undefined) {
      throw new Error('Invalid batch events response');
    }
  });

  await testEndpoint('GET /api/events/types', async () => {
    const response = await api.getEventTypes();
    if (!response.success) {
      throw new Error('Failed to get event types');
    }
    if (!response.data) {
      throw new Error('Invalid event types response - missing data field');
    }
    const data = response.data as any;
    // Check for either camelCase or snake_case field names
    if (!Array.isArray(data.eventTypes) && !Array.isArray(data.event_types)) {
      throw new Error('Invalid event types response - missing eventTypes/event_types array');
    }
  }, true);
}

// ============================================
// ANALYTICS API TESTS
// ============================================

async function testAnalyticsAPI() {
  console.log('\n=== ANALYTICS API ===\n');

  await testEndpoint('GET /api/metrics', async () => {
    const response = await api.getMetrics(7);
    if (!response.success) {
      // Analytics might not be available, so log but don't fail
      throw new Error('Metrics endpoint unavailable (this may be expected)');
    }
  });

  await testEndpoint('GET /api/metrics/daily', async () => {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 7);
    
    const response = await api.getDailyMetrics({
      start: startDate.toISOString().split('T')[0],
      end: endDate.toISOString().split('T')[0],
    });
    if (!response.success) {
      // Analytics might not be available, so log but don't fail
      throw new Error('Daily metrics endpoint unavailable (this may be expected)');
    }
  });

  await testEndpoint('GET /api/metrics/top-searches', async () => {
    const response = await api.getTopSearches({ days: 7, limit: 10 });
    if (!response.success) {
      // Analytics might not be available, so log but don't fail
      throw new Error('Top searches endpoint unavailable (this may be expected)');
    }
  });

  await testEndpoint('GET /api/evaluation/scenarios', async () => {
    const response = await api.getEvaluationScenarios();
    if (!response.success) {
      // Evaluation might not be available, so log but don't fail
      throw new Error('Evaluation scenarios endpoint unavailable (this may be expected)');
    }
  });
}

// ============================================
// V2 API TESTS
// ============================================

async function testV2API() {
  console.log('\n=== V2 API ===\n');

  await testEndpoint('GET /api/v2/companies', async () => {
    const response = await api.getCompanies();
    if (!response.success) {
      throw new Error('Failed to get companies');
    }
    if (!response.data || !Array.isArray(response.data)) {
      throw new Error('Invalid companies response');
    }
  });

  await testEndpoint('GET /api/v2/templates', async () => {
    const response = await api.getTemplates({ limit: 10 });
    if (!response.success) {
      throw new Error('Failed to get templates');
    }
    if (!response.data || !Array.isArray(response.data)) {
      throw new Error('Invalid templates response');
    }
  });

  await testEndpoint('GET /api/v2/occurrences', async () => {
    const response = await api.getOccurrences({ limit: 10 });
    if (!response.success) {
      throw new Error('Failed to get occurrences');
    }
    if (!response.data || !Array.isArray(response.data)) {
      throw new Error('Invalid occurrences response');
    }
  });

  await testEndpoint('GET /api/v2/schema-info', async () => {
    const response = await api.getSchemaInfo();
    if (!response.success) {
      throw new Error('Failed to get schema info');
    }
    if (!response.data) {
      throw new Error('Invalid schema info response - missing data field');
    }
    const data = response.data as any;
    // Check for either camelCase or snake_case field names
    if (!data.schemaVersion && !data.schema_version) {
      throw new Error('Invalid schema info response - missing schemaVersion/schema_version');
    }
  }, true);
}

// ============================================
// MAIN TEST RUNNER
// ============================================

async function runAllTests() {
  console.log('='.repeat(60));
  console.log('API Endpoints Test Suite');
  console.log(`Testing against: ${API_URL}`);
  console.log('='.repeat(60));

  try {
    await testSystemAPI();
    await testResourcesAPI();
    await testEventsAPI();
    await testAnalyticsAPI();
    await testV2API();
  } catch (error) {
    console.error('\nUnexpected error during testing:', error);
  }

  // Print summary
  console.log('\n' + '='.repeat(60));
  console.log('TEST SUMMARY');
  console.log('='.repeat(60));

  const total = results.length;
  const passed = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;

  console.log(`Total tests: ${total}`);
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);

  if (failed > 0) {
    console.log('\nFailed tests:');
    results
      .filter(r => !r.success)
      .forEach(r => {
        console.log(`  - ${r.name}: ${r.error || 'Unknown error'}`);
      });
  }

  const avgResponseTime = results.reduce((sum, r) => sum + (r.responseTime || 0), 0) / total;
  console.log(`\nAverage response time: ${Math.round(avgResponseTime)}ms`);

  console.log('\n' + '='.repeat(60));

  // Exit with error code if any tests failed
  process.exit(failed > 0 ? 1 : 0);
}

// Run tests
runAllTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
