# API Structure Documentation

This document details the new API structure, including all endpoints, their main attributes, and functions.

## Overview

The SmartTrip API is organized into multiple blueprints, each handling a specific domain:

- **System API** - Health checks and system operations
- **Resources API** - Read-only reference data (countries, guides, trip types, tags)
- **Analytics API** - Metrics and evaluation endpoints
- **Events API** - User event tracking and session management
- **V2 API** - New schema-based endpoints (templates and occurrences)

---

## System API (`/api/system`)

**Blueprint:** `system_bp`  
**Purpose:** System health monitoring and database operations

### Endpoints

#### `GET /api/health`
Health check endpoint for monitoring system status.

**Response Attributes:**
- `status` (string): System status ('healthy' or 'unhealthy')
- `service` (string): Service name
- `version` (string): API version
- `schema` (string): Database schema version
- `database` (object): Database statistics
  - `trip_occurrences` (int): Count of trip occurrences
  - `trip_templates` (int): Count of trip templates
  - `countries` (int): Count of countries
  - `guides` (int): Count of guides
  - `tags` (int): Count of tags
  - `trip_types` (int): Count of trip types

**Functions:**
- Verifies database connectivity
- Returns counts of key database entities
- Provides schema version information

**Error Handling:**
- Returns 503 for database connection errors
- Returns 500 for other errors

---

#### `POST /api/seed`
Seed database with programmatically generated data (development only).

**Request:** No body required

**Response Attributes:**
- `success` (boolean): Operation success status
- `message` (string): Success message
- `trip_templates` (int): Number of templates created
- `trip_occurrences` (int): Number of occurrences created
- `note` (string): Warning about development-only usage

**Functions:**
- Generates test data for local development
- Restricted to non-production environments
- Uses seed script from `backend/scripts/db/seed.py`

**Error Handling:**
- Returns 403 in production
- Returns 503 for database connection errors
- Returns 500 for other errors

---

## Resources API (`/api/resources`)

**Blueprint:** `resources_bp`  
**Purpose:** Read-only endpoints for reference data

### Endpoints

#### `GET /api/locations`
Get all countries and continents for search dropdowns.

**Response Attributes:**
- `success` (boolean): Operation success status
- `count` (int): Number of countries
- `countries` (array): List of country objects
  - `id` (int): Country ID
  - `name` (string): English name
  - `name_he` (string): Hebrew name
  - `continent` (string): Continent name
- `continents` (array): List of continent objects
  - `value` (string): English continent name
  - `nameHe` (string): Hebrew continent name

**Functions:**
- Returns all countries without filtering
- Builds continent list from unique values
- Maps continents to Hebrew names
- Excludes no countries (shows all available)

---

#### `GET /api/countries`
Get all countries, optionally filtered by continent.

**Query Parameters:**
- `continent` (string, optional): Filter by continent name

**Response Attributes:**
- `success` (boolean): Operation success status
- `count` (int): Number of countries returned
- `data` (array): List of country objects (from `country.to_dict()`)

**Functions:**
- Lists all countries
- Excludes Antarctica (selectable via continent)
- Supports continent filtering
- Returns country objects with full details

---

#### `GET /api/countries/<country_id>`
Get a specific country by ID.

**Path Parameters:**
- `country_id` (int): Country ID

**Response Attributes:**
- `success` (boolean): Operation success status
- `data` (object): Country object (from `country.to_dict()`)

**Functions:**
- Retrieves single country by ID
- Returns 404 if not found

---

#### `GET /api/guides`
Get all active guides.

**Response Attributes:**
- `success` (boolean): Operation success status
- `count` (int): Number of guides
- `data` (array): List of guide objects (from `guide.to_dict()`)

**Functions:**
- Returns only active guides (`is_active == True`)
- Ordered by name

---

#### `GET /api/guides/<guide_id>`
Get a specific guide by ID.

**Path Parameters:**
- `guide_id` (int): Guide ID

**Response Attributes:**
- `success` (boolean): Operation success status
- `data` (object): Guide object (from `guide.to_dict()`)

**Functions:**
- Retrieves single guide by ID
- Returns 404 if not found

---

#### `GET /api/trip-types`
Get all trip types (trip styles).

**Response Attributes:**
- `success` (boolean): Operation success status
- `count` (int): Number of trip types
- `data` (array): List of trip type objects (from `trip_type.to_dict()`)

**Functions:**
- Returns all trip types
- Ordered by name
- Handles CORS preflight requests

---

#### `GET /api/tags`
Get all theme tags (trip interests/themes).

**Response Attributes:**
- `success` (boolean): Operation success status
- `count` (int): Number of tags
- `data` (array): List of tag objects (from `tag.to_dict()`)

**Functions:**
- Returns all theme tags
- Note: After V2 migration, only theme tags are returned
- For trip styles, use `/api/trip-types` endpoint
- Ordered by name
- Handles CORS preflight requests

---

## Analytics API (`/api/analytics`)

**Blueprint:** `analytics_bp`  
**Purpose:** Metrics and evaluation endpoints for recommendation analytics

### Endpoints

#### `GET /api/metrics`
Get current recommendation metrics (summary).

**Query Parameters:**
- `days` (int, optional): Number of days to include (default: 7, max: 90)

**Response Attributes:**
- `success` (boolean): Operation success status
- `data` (object): Aggregated metrics object

**Functions:**
- Aggregates metrics for specified time period
- Uses metrics aggregator from `recommender.metrics`
- Returns 503 if metrics module not available

---

#### `GET /api/metrics/daily`
Get daily breakdown of recommendation metrics.

**Query Parameters:**
- `start` (string, optional): Start date (YYYY-MM-DD, default: 7 days ago)
- `end` (string, optional): End date (YYYY-MM-DD, default: today)

**Response Attributes:**
- `success` (boolean): Operation success status
- `start` (string): Actual start date used
- `end` (string): Actual end date used
- `count` (int): Number of daily records
- `data` (array): List of daily metrics objects

**Functions:**
- Returns daily metrics for date range
- Limits range to 90 days maximum
- Uses metrics aggregator's `get_metrics_range()` method

---

#### `GET /api/metrics/top-searches`
Get top search patterns (continents, types, etc.).

**Query Parameters:**
- `days` (int, optional): Number of days to analyze (default: 7, max: 90)
- `limit` (int, optional): Max items per category (default: 10, max: 50)

**Response Attributes:**
- `success` (boolean): Operation success status
- `data` (object): Top searches by category

**Functions:**
- Analyzes search patterns over time period
- Returns top searches by category (continents, types, etc.)
- Uses metrics aggregator's `get_top_searches()` method

---

#### `POST /api/evaluation/run`
Run evaluation scenarios and get results.

**Request Body:**
- `category` (string, optional): Filter by category (e.g., "core_persona")
- `scenario_ids` (array, optional): Specific scenario IDs to run

**Response Attributes:**
- Evaluation report object with pass/fail status for each scenario

**Functions:**
- Runs evaluation scenarios
- Uses evaluator from `recommender.evaluation`
- Requires base URL from request for scenario execution
- Returns 503 if evaluation module not available

---

#### `GET /api/evaluation/scenarios`
Get available evaluation scenarios without running them.

**Query Parameters:**
- `category` (string, optional): Filter by category

**Response Attributes:**
- `success` (boolean): Operation success status
- `count` (int): Number of scenarios
- `data` (array): List of scenario objects
  - `id` (int): Scenario ID
  - `name` (string): Scenario name
  - `description` (string): Scenario description
  - `category` (string): Scenario category
  - `expected_min_results` (int): Minimum expected results

**Functions:**
- Lists available evaluation scenarios
- Returns simplified list without preference details
- Uses evaluator's `load_scenarios()` method

---

## Events API (`/api/events`)

**Blueprint:** `events_bp`  
**Purpose:** User event tracking and session management

### Endpoints

#### `POST /api/session/start`
Initialize or resume a session with device info.

**Request Body:**
- `session_id` (string, required): Session UUID
- `anonymous_id` (string, required): Anonymous user UUID
- `device_type` (string, optional): Device type ('mobile', 'tablet', 'desktop')
- `referrer` (string, optional): Referrer URL

**Response Attributes:**
- `success` (boolean): Operation success status
- `user_id` (int): User ID (created or existing)
- `session_id` (string): Session UUID
- `is_new_session` (boolean): Whether this is a new session

**Functions:**
- Creates or retrieves user by anonymous_id
- Creates or retrieves session
- Captures device type from frontend (not user-agent)
- Captures referrer from frontend
- Extracts real IP (handles load balancers)
- Integrates with JWT authentication if available

---

#### `POST /api/events`
Track a single user event.

**Request Body:**
- `event_type` (string, required): Event type (e.g., 'click_trip')
- `session_id` (string, required): Session UUID
- `anonymous_id` (string, required): Anonymous user UUID
- `trip_id` (int, optional): Trip ID
- `source` (string, optional): Source of event (required for clicks)
- `recommendation_request_id` (string, optional): Links to recommendation request
- `metadata` (object, optional): Flexible event data
- `position` (int, optional): Position in results
- `score` (float, optional): Match score at time of event
- `client_timestamp` (string, optional): Client timestamp (ISO format)
- `page_url` (string, optional): Page URL
- `referrer` (string, optional): Referrer URL

**Response Attributes:**
- `success` (boolean): Operation success status
- `event_id` (int): Created event ID

**Functions:**
- Validates event data
- Requires source for click events
- Resolves user (prioritizes authenticated user)
- Tracks event with all metadata
- Returns 201 on success

---

#### `POST /api/events/batch`
Track multiple events in a batch.

**Request Body:**
- `events` (array, required): Array of event objects (max 100)

**Response Attributes:**
- `success` (boolean): Operation success status
- `processed` (int): Number of events processed
- `total` (int): Total events in batch
- `errors` (array, optional): List of errors if any

**Functions:**
- Processes up to 100 events per batch
- Resolves users for all unique anonymous_ids
- More efficient for accumulated events (e.g., impressions)
- Returns batch processing results

---

#### `POST /api/user/identify`
Identify/register a user (link anonymous to registered).

**Request Body:**
- `anonymous_id` (string, required): Anonymous user UUID
- `email` (string, optional): User email
- `name` (string, optional): User name

**Response Attributes:**
- `success` (boolean): Operation success status
- `user_id` (int): User ID
- `is_registered` (boolean): Whether user is registered

**Functions:**
- Links anonymous user to registered user
- Called when user provides email or logs in
- Creates or updates user record

---

#### `GET /api/events/types`
Get list of valid event types and their categories.

**Response Attributes:**
- `success` (boolean): Operation success status
- `event_types` (array): List of valid event type strings
- `categories` (object): Event categories mapping
- `valid_sources` (array): List of valid source strings

**Functions:**
- Returns valid event types for frontend validation
- Provides event categories
- Lists valid source values

---

## V2 API (`/api/v2`)

**Blueprint:** `api_v2_bp`  
**Purpose:** New schema-based endpoints using TripTemplate and TripOccurrence

### Endpoints

#### `GET /api/v2/companies`
Get all active companies.

**Response Attributes:**
- `success` (boolean): Operation success status
- `count` (int): Number of companies
- `data` (array): List of company objects

**Functions:**
- Returns active companies only
- Ordered by name

---

#### `GET /api/v2/companies/<company_id>`
Get a specific company with its trip templates.

**Path Parameters:**
- `company_id` (int): Company ID

**Response Attributes:**
- `success` (boolean): Operation success status
- `data` (object): Company object with `templateCount` attribute

**Functions:**
- Retrieves company by ID
- Includes count of active trip templates
- Returns 404 if not found

---

#### `GET /api/v2/templates`
Get trip templates with optional filters.

**Query Parameters:**
- `company_id` (int, optional): Filter by company
- `trip_type_id` (int, optional): Filter by trip type
- `country_id` (int, optional): Filter by country
- `difficulty` (int, optional): Filter by difficulty level
- `include_occurrences` (boolean, optional): Include upcoming occurrences (default: false)
- `limit` (int, optional): Max results (default: 50, max: 100)
- `offset` (int, optional): Pagination offset

**Response Attributes:**
- `success` (boolean): Operation success status
- `count` (int): Number of results
- `total` (int): Total matching templates
- `offset` (int): Offset used
- `limit` (int): Limit used
- `data` (array): List of template objects
  - Includes `upcomingOccurrences` if `include_occurrences=true`

**Functions:**
- Lists active trip templates
- Supports multiple filters
- Supports multi-country filtering via join
- Includes pagination
- Can optionally include upcoming occurrences

---

#### `GET /api/v2/templates/<template_id>`
Get a specific trip template with all details.

**Path Parameters:**
- `template_id` (int): Template ID

**Response Attributes:**
- `success` (boolean): Operation success status
- `data` (object): Template object with full relations and occurrences

**Functions:**
- Retrieves template with all relations (company, trip_type, countries, tags)
- Includes all upcoming occurrences
- Returns 404 if not found

---

#### `GET /api/v2/occurrences`
Get trip occurrences (scheduled trips) with filters.

**Query Parameters:**
- `template_id` (int, optional): Filter by template
- `guide_id` (int, optional): Filter by guide
- `status` (string, optional): Filter by status (OPEN, GUARANTEED, LAST_PLACES, FULL)
- `start_date` (string, optional): Minimum start date (ISO format)
- `end_date` (string, optional): Maximum end date (ISO format)
- `year` (int, optional): Filter by year
- `month` (int, optional): Filter by month (1-12)
- `min_price` (float, optional): Minimum price
- `max_price` (float, optional): Maximum price
- `include_template` (boolean, optional): Include template details (default: true)
- `limit` (int, optional): Max results (default: 50, max: 100)
- `offset` (int, optional): Pagination offset

**Response Attributes:**
- `success` (boolean): Operation success status
- `count` (int): Number of results
- `total` (int): Total matching occurrences
- `offset` (int): Offset used
- `limit` (int): Limit used
- `data` (array): List of occurrence objects

**Functions:**
- Lists trip occurrences (scheduled trips)
- Excludes cancelled and full trips by default
- Excludes past trips by default
- Supports extensive filtering (date, price, status, etc.)
- Includes template details by default
- Supports pagination

---

#### `GET /api/v2/occurrences/<occurrence_id>`
Get a specific trip occurrence with full details.

**Path Parameters:**
- `occurrence_id` (int): Occurrence ID

**Response Attributes:**
- `success` (boolean): Operation success status
- `data` (object): Occurrence object with full template details

**Functions:**
- Retrieves occurrence with all relations
- Includes full template details (company, trip_type, countries, tags)
- Returns 404 if not found

---

#### `GET /api/v2/trips`
Backward-compatible trips endpoint (returns occurrences formatted as trips).

**Query Parameters:**
- `country_id` (int, optional): Filter by country
- `trip_type_id` (int, optional): Filter by trip type
- `guide_id` (int, optional): Filter by guide
- `status` (string, optional): Filter by status
- `difficulty` (int, optional): Filter by difficulty
- `limit` (int, optional): Max results (max: 1000)
- `offset` (int, optional): Pagination offset

**Response Attributes:**
- `success` (boolean): Operation success status
- `count` (int): Number of results
- `total` (int): Total matching trips
- `offset` (int): Offset used
- `limit` (int): Limit used
- `data` (array): List of trip objects (formatted from occurrences)

**Functions:**
- Provides backward compatibility with old API
- Returns occurrences formatted like old trips table
- Handles Private Groups special case (no date filter)
- Excludes cancelled and full trips
- Excludes past trips (except Private Groups)
- Filters by spots_left > 0 (except Private Groups)

---

#### `GET /api/v2/trips/<trip_id>`
Get a specific trip by occurrence ID (backward compatible).

**Path Parameters:**
- `trip_id` (int): Occurrence ID (treated as trip ID)

**Response Attributes:**
- `success` (boolean): Operation success status
- `data` (object): Trip object (formatted from occurrence)

**Functions:**
- Backward-compatible endpoint
- Returns occurrence formatted as old trip structure
- Includes all relations

---

#### `POST /api/v2/recommendations`
V2 Recommendation engine using TripOccurrence + TripTemplate.

**Request Body:**
- Preferences object (same format as V1)

**Response Attributes:**
- `success` (boolean): Operation success status
- `count` (int): Total number of results
- `primary_count` (int): Number of primary results
- `relaxed_count` (int): Number of relaxed results
- `total_candidates` (int): Total candidates evaluated
- `total_trips` (int): Total trips in database
- `data` (array): List of trip objects
- `has_relaxed_results` (boolean): Whether relaxed results are included
- `score_thresholds` (object): Score threshold configuration
- `show_refinement_message` (boolean): Whether to show refinement message
- `request_id` (string): Request ID for logging
- `search_type` (string): Classified search type
- `api_version` (string): API version ('v2')
- `message` (string): Success message

**Functions:**
- Full feature parity with V1 recommendations
- Request logging for analytics
- Search type classification
- Relaxed search with date expansion and difficulty tolerance
- Antarctica special case handling
- Legacy start_date support
- Uses recommendation service from `app.services.recommendation`

---

#### `GET /api/v2/schema-info`
Get information about the V2 schema.

**Response Attributes:**
- `success` (boolean): Operation success status
- `schema_version` (string): Schema version ('2.3')
- `statistics` (object): Database statistics
  - `companies` (int): Number of companies
  - `templates` (int): Number of active templates
  - `occurrences` (int): Number of non-cancelled occurrences
  - `active_occurrences` (int): Number of active upcoming occurrences
- `endpoints` (object): Available endpoint paths

**Functions:**
- Provides schema version information
- Returns database statistics
- Lists available endpoints

---

## Helper Functions

### `format_occurrence_as_trip(occurrence, include_relations=False)`
Formats a TripOccurrence as a legacy Trip object for backward compatibility.

**Parameters:**
- `occurrence` (TripOccurrence): The occurrence to format
- `include_relations` (boolean): Whether to include related objects

**Returns:**
- Dictionary with trip data in old format

**Functions:**
- Maps occurrence and template data to old trip structure
- Provides both camelCase and snake_case field names
- Includes template ID for new schema reference
- Handles all relations (country, guide, trip_type, company, tags)

---

## Error Handling

All endpoints follow consistent error handling patterns:

1. **Database Connection Errors (503):**
   - Returns: `{'success': False, 'error': 'Database connection unavailable...'}`

2. **Database Errors (503):**
   - Returns: `{'success': False, 'error': 'Database error occurred...'}`

3. **Not Found (404):**
   - Returns: `{'success': False, 'error': '<resource> not found'}`

4. **Validation Errors (400):**
   - Returns: `{'success': False, 'error': '<validation message>'}`

5. **Other Errors (500):**
   - Returns: `{'success': False, 'error': '<error message>'}`

---

## Authentication

- Events API and V2 API support optional JWT authentication
- Authentication is checked via `get_current_user()` from `app.core.auth`
- If authentication is available, authenticated users are prioritized over anonymous users
- Anonymous tracking is always supported

---

## CORS Configuration

- CORS is configured via `ALLOWED_ORIGINS` environment variable
- Default: `http://localhost:3000` (development)
- Production: Comma-separated list of allowed origins
- Supports credentials for authenticated requests

---

## Database Schema

The API uses V2 schema with the following key concepts:

- **TripTemplate**: The "what" of a trip (description, pricing, difficulty)
- **TripOccurrence**: The "when" of a trip (dates, guide, availability)
- **Company**: Trip operator/company
- **Country**: Destination countries
- **Guide**: Trip guides
- **TripType**: Trip styles (e.g., "Private Groups", "Group Tours")
- **Tag**: Theme tags (interests/themes)

---

## Version Information

- **API Version**: 2.0.0
- **Schema Version**: 2.3
- **Service Name**: SmartTrip API
