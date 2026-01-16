# API Documentation

Complete API reference for the SmartTrip backend REST API, organized by blueprint modules.

## Base URL

- **Development**: `http://localhost:5000`
- **Production**: `https://your-backend.onrender.com`

## API Organization

The API is organized into Flask Blueprints, each handling a specific domain:

- **[System API](#system-api-appapisystem)** - Health checks and system operations
- **[Resources API](#resources-api-appapiresources)** - Read-only reference data
- **[V2 API](#v2-api-appapiv2)** - Trip recommendations and data (current schema)
- **[Events API](#events-api-appapievents)** - User event tracking and session management
- **[Analytics API](#analytics-api-appapianalytics)** - Metrics and evaluation endpoints

---

## System API (`app/api/system`)

**Blueprint:** `system_bp`  
**Purpose:** System health monitoring and database operations

### `GET /api/health`

Health check endpoint for monitoring system status.

**Response:**
```json
{
  "status": "healthy",
  "service": "smarttrip-api",
  "version": "2.0",
  "schema": "v2",
  "database": {
    "trip_occurrences": 150,
    "trip_templates": 50,
    "countries": 195,
    "guides": 25,
    "tags": 30,
    "trip_types": 8
  }
}
```

**Location:** `backend/app/api/system/routes.py`

---

## Resources API (`app/api/resources`)

**Blueprint:** `resources_bp`  
**Purpose:** Read-only endpoints for reference data (countries, guides, trip types, tags)

### `GET /api/locations`

Get all countries and continents for search dropdowns.

**Response:**
```json
{
  "success": true,
  "count": 195,
  "countries": [
    {
      "id": 1,
      "name": "Japan",
      "name_he": "יפן",
      "continent": "Asia"
    }
  ],
  "continents": [
    {
      "value": "Asia",
      "nameHe": "אסיה"
    }
  ]
}
```

**Location:** `backend/app/api/resources/routes.py`

### `GET /api/countries`

Get all countries (excludes Antarctica).

**Query Parameters:**
- `continent` (optional) - Filter by continent name

**Response:**
```json
{
  "success": true,
  "count": 194,
  "data": [...]
}
```

### `GET /api/countries/<id>`

Get specific country details.

### `GET /api/trip-types`

Get all trip type categories.

**Response:**
```json
{
  "success": true,
  "count": 8,
  "data": [
    {
      "id": 1,
      "name": "Adventure",
      "name_he": "הרפתקני"
    }
  ]
}
```

### `GET /api/tags`

Get all theme tags.

**Response:**
```json
{
  "success": true,
  "count": 30,
  "data": [
    {
      "id": 1,
      "name": "Wildlife",
      "name_he": "חיות בר"
    }
  ]
}
```

### `GET /api/guides`

Get all active tour guides.

**Response:**
```json
{
  "success": true,
  "count": 25,
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "description": "Experienced guide..."
    }
  ]
}
```

### `GET /api/guides/<id>`

Get specific guide details.

---

## V2 API (`app/api/v2`)

**Blueprint:** `api_v2_bp`  
**Purpose:** Trip recommendations and data using V2 schema (TripTemplate/TripOccurrence)

### `POST /api/v2/recommendations`

Get personalized trip recommendations based on user preferences.

**Request Body:**
```json
{
  "selected_countries": [1, 5],
  "selected_continents": ["Asia", "Europe"],
  "preferred_type_id": 3,
  "preferred_theme_ids": [10, 15],
  "budget": 12000,
  "min_duration": 7,
  "max_duration": 14,
  "difficulty": 2,
  "year": "2026",
  "month": "3"
}
```

**Response:**
```json
{
  "success": true,
  "count": 10,
  "primary_count": 7,
  "relaxed_count": 3,
  "data": [
    {
      "id": 517,
      "title": "Japan Cultural Discovery",
      "match_score": 88,
      "is_relaxed": false,
      "price": 11500,
      "duration": 10,
      "departure_date": "2026-03-15",
      ...
    }
  ]
}
```

**Location:** `backend/app/api/v2/routes.py`

### `GET /api/v2/trips`

Get all trips (templates + occurrences combined).

**Query Parameters:**
- `template_id` (optional) - Filter by template ID
- `country_id` (optional) - Filter by country ID
- `status` (optional) - Filter by status

### `GET /api/v2/trips/<id>`

Get specific trip details (combined template + occurrence).

### `GET /api/v2/templates`

Get all trip templates.

**Query Parameters:**
- `type_id` (optional) - Filter by trip type
- `country_id` (optional) - Filter by primary country

### `GET /api/v2/templates/<id>`

Get specific template details.

### `GET /api/v2/occurrences`

Get all trip occurrences.

**Query Parameters:**
- `template_id` (optional) - Filter by template ID
- `guide_id` (optional) - Filter by guide ID
- `status` (optional) - Filter by status
- `year` (optional) - Filter by year
- `month` (optional) - Filter by month

### `GET /api/v2/occurrences/<id>`

Get specific occurrence details.

### `GET /api/v2/companies`

Get all active companies.

**Response:**
```json
{
  "success": true,
  "count": 5,
  "data": [
    {
      "id": 1,
      "name": "Adventure Tours",
      "is_active": true
    }
  ]
}
```

### `GET /api/v2/companies/<id>`

Get specific company details.

### `GET /api/v2/schema-info`

Get schema version and metadata information.

---

## Events API (`app/api/events`)

**Blueprint:** `events_bp`  
**Purpose:** User event tracking and session management

### `POST /api/session/start`

Initialize user session for event tracking.

**Request Body:**
```json
{
  "device_type": "desktop",
  "user_agent": "Mozilla/5.0...",
  "screen_width": 1920,
  "screen_height": 1080,
  "referrer": "https://google.com"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "uuid",
  "user_id": "uuid",
  "anonymous_id": "uuid"
}
```

**Location:** `backend/app/api/events/routes.py`

### `POST /api/events`

Track a single user event.

**Request Body:**
```json
{
  "event_type": "click_trip",
  "trip_id": 517,
  "position": 1,
  "score": 88,
  "source": "search_results",
  "metadata": {
    "duration_seconds": 45
  },
  "client_timestamp": "2025-01-15T10:30:00Z",
  "page_url": "/search/results"
}
```

**Response:**
```json
{
  "success": true,
  "event_id": "uuid"
}
```

### `POST /api/events/batch`

Batch upload multiple events (max 100 per request).

**Request Body:**
```json
{
  "events": [
    {
      "event_type": "page_view",
      "page_url": "/search/results",
      "client_timestamp": "2025-01-15T10:30:00Z"
    },
    {
      "event_type": "impression",
      "trip_id": 517,
      "position": 1,
      "score": 88
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "processed": 2,
  "errors": []
}
```

### `POST /api/user/identify`

Link anonymous user to authenticated user.

**Request Body:**
```json
{
  "supabase_user_id": "uuid",
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "uuid",
  "linked_events": 15
}
```

### `GET /api/events/types`

Get all available event types.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "page_view",
      "description": "Page view event"
    },
    {
      "id": 2,
      "name": "click_trip",
      "description": "Trip card click"
    }
  ]
}
```

---

## Analytics API (`app/api/analytics`)

**Blueprint:** `analytics_bp`  
**Purpose:** Metrics, analytics, and algorithm evaluation

### `GET /api/metrics`

Get current recommendation metrics (last 7 days by default).

**Query Parameters:**
- `days` (optional) - Number of days to aggregate (1-90, default: 7)

**Response:**
```json
{
  "success": true,
  "period_days": 7,
  "total_requests": 1250,
  "unique_sessions": 850,
  "avg_response_time_ms": 245,
  "avg_top_score": 72.5,
  "result_counts": {
    "avg_results": 8.5,
    "avg_primary": 6.2,
    "avg_relaxed": 2.3
  }
}
```

**Location:** `backend/app/api/analytics/routes.py`

### `GET /api/metrics/daily`

Get daily metrics breakdown.

**Query Parameters:**
- `start` (required) - Start date (YYYY-MM-DD)
- `end` (required) - End date (YYYY-MM-DD)
- Max range: 90 days

**Response:**
```json
{
  "success": true,
  "start_date": "2025-01-01",
  "end_date": "2025-01-07",
  "daily_metrics": [
    {
      "date": "2025-01-01",
      "total_requests": 180,
      "avg_response_time_ms": 230,
      "avg_top_score": 75.2
    }
  ]
}
```

### `GET /api/metrics/top-searches`

Get most common search criteria.

**Query Parameters:**
- `days` (optional) - Number of days (default: 7)
- `limit` (optional) - Result limit (default: 10)

**Response:**
```json
{
  "success": true,
  "top_continents": [
    {"continent": "Asia", "count": 450},
    {"continent": "Europe", "count": 320}
  ],
  "top_trip_types": [
    {"trip_type_id": 3, "name": "Cultural", "count": 280}
  ]
}
```

### `POST /api/evaluation/run`

Run algorithm evaluation scenarios.

**Request Body:**
```json
{
  "scenario_ids": ["all"]
}
```

Or specific scenarios:
```json
{
  "scenario_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "success": true,
  "scenarios_run": 10,
  "scenarios_passed": 9,
  "scenarios_failed": 1,
  "results": [...]
}
```

### `GET /api/evaluation/scenarios`

Get all available evaluation scenarios.

**Response:**
```json
{
  "success": true,
  "count": 10,
  "scenarios": [
    {
      "id": 1,
      "name": "Adventure Seeker",
      "description": "Tests adventure trip recommendations"
    }
  ]
}
```

---

## Development Endpoints

### `POST /api/seed`

Seed database with test data (disabled in production).

**Location:** `backend/app/api/system/routes.py`

**Note:** Only available in development environment.

## API Versioning

- **V2**: Current API using TripTemplate/TripOccurrence schema
- All endpoints under `/api/v2/` use the new schema
- Legacy V1 endpoints may exist but are deprecated

## Authentication

The API supports Supabase JWT authentication:

- **Optional Authentication**: Most endpoints work in guest mode
- **JWT Token**: Include in `Authorization: Bearer <token>` header
- **User Identification**: Anonymous users tracked via `anonymous_id`

**Example:**
```http
GET /api/v2/recommendations
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Response Format

### Success Response

Most endpoints return:
```json
{
  "success": true,
  "count": 10,
  "data": [...]
}
```

### Error Response

Error responses follow this format:
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable (database errors)

## Rate Limiting

Currently no rate limiting is implemented. Consider adding rate limiting for production use.

## CORS

CORS is configured to allow requests from:
- Development: `http://localhost:3000`
- Production: Configured via `ALLOWED_ORIGINS` environment variable

## API Organization Summary

The API is organized into 5 main blueprints:

| Blueprint | Location | Purpose | Key Endpoints |
|-----------|----------|---------|---------------|
| **System** | `app/api/system/` | Health checks | `/api/health`, `/api/seed` |
| **Resources** | `app/api/resources/` | Reference data | `/api/locations`, `/api/trip-types`, `/api/tags`, `/api/guides` |
| **V2** | `app/api/v2/` | Recommendations & trips | `/api/v2/recommendations`, `/api/v2/trips`, `/api/v2/templates` |
| **Events** | `app/api/events/` | Event tracking | `/api/session/start`, `/api/events/batch`, `/api/user/identify` |
| **Analytics** | `app/api/analytics/` | Metrics & evaluation | `/api/metrics`, `/api/metrics/daily`, `/api/evaluation/run` |

## Related Documentation

- [Architecture Overview](../architecture/ARCHITECTURE_OVERVIEW.md) - System architecture
- [API Structure](API_STRUCTURE.md) - Detailed API structure documentation with response attributes and functions
- [Data Pipelines](../architecture/DATA_PIPELINES.md) - Data flow documentation
- [Backend README](../../backend/README.md) - Backend setup guide
