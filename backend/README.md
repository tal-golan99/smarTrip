# Backend - SmartTrip

Flask REST API backend for the SmartTrip trip recommendation platform.

## Overview

The backend is built with Flask 3.0, SQLAlchemy 2.0, and PostgreSQL. It provides REST API endpoints for trip recommendations, event tracking, analytics, and resource data management.

## Tech Stack

- **Flask 3.0** - Python web framework
- **SQLAlchemy 2.0** - ORM and database toolkit
- **PostgreSQL 12+** - Relational database (via Supabase)
- **Gunicorn** - Production WSGI server
- **Python 3.10+** - Programming language

## Project Structure

```
backend/
├── app/                      # Main application package
│   ├── main.py              # Flask app entry point
│   ├── core/                # Core functionality
│   │   ├── config.py        # Configuration management
│   │   ├── database.py      # Database connection
│   │   └── auth.py          # Authentication middleware
│   ├── models/              # SQLAlchemy models
│   │   ├── trip.py         # Trip models (V2 schema)
│   │   └── events.py        # Event tracking models
│   ├── services/            # Business logic
│   │   ├── recommendation.py # Recommendation algorithm
│   │   └── events.py        # Event processing
│   └── api/                 # API route handlers
│       ├── v2/             # V2 API endpoints
│       ├── events/         # Event tracking endpoints
│       ├── analytics/       # Analytics endpoints
│       ├── resources/      # Resource endpoints
│       └── system/         # System endpoints
├── analytics/              # Analytics and monitoring infrastructure
│   ├── logging.py          # Request logging
│   ├── metrics.py          # Performance metrics
│   └── evaluation.py       # Quality evaluation
├── migrations/              # Database migrations
├── scripts/                 # Utility scripts
│   ├── db/                 # Database scripts
│   ├── analytics/          # Analytics scripts
│   └── data_gen/           # Data generation
└── requirements.txt        # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 12+ (or Supabase account)
- pip

### Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create `backend/.env`:

```env
FLASK_APP=app.main:app
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-west-2.pooler.supabase.com:5432/postgres
ALLOWED_ORIGINS=http://localhost:3000
SUPABASE_JWT_SECRET=your-jwt-secret-here
```

**Important:**
- Use **Session pooler** connection string (port 5432) for local development
- Get connection string from Supabase Dashboard → Settings → Database

### Database Setup

```bash
# Initialize database schema (runs automatically on first start)
python -m app.main

# Optional: Seed database with test data
python scripts/db/seed.py
```

### Development

```bash
# Start development server
python -m app.main
# OR
python app/main.py

# Runs on http://localhost:5000
```

### Production

```bash
# Using Gunicorn
gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 2
```

## API Endpoints

### System

- `GET /api/health` - Health check endpoint

### Resources

- `GET /api/locations` - Get all countries and continents
- `GET /api/trip-types` - Get all trip type categories
- `GET /api/tags` - Get all theme tags
- `GET /api/guides` - Get all tour guides
- `GET /api/companies` - Get all trip providers

### Recommendations (V2)

- `POST /api/v2/recommendations` - Get personalized trip recommendations
  - Request body: User preferences (countries, types, themes, budget, duration, etc.)
  - Response: Ranked recommendations with match scores (0-100)

- `GET /api/v2/trips/<id>` - Get trip details
- `GET /api/v2/templates/<id>` - Get trip template details
- `GET /api/v2/occurrences/<id>` - Get trip occurrence details

### Event Tracking

- `POST /api/session/start` - Initialize user session
- `POST /api/events/batch` - Batch upload user events
- `POST /api/user/identify` - Link anonymous user to authenticated user

### Analytics

- `GET /api/metrics` - Get current recommendation metrics
- `GET /api/metrics/daily` - Get daily metrics breakdown
- `GET /api/metrics/top-searches` - Get most common search criteria

See `docs/api/README.md` for detailed API documentation.

## Core Components

### Database Models

**Trip Models** (`app/models/trip.py`):
- `TripTemplate` - Trip definition (what)
- `TripOccurrence` - Scheduled trip instance (when)
- `Company` - Trip provider
- `Country`, `Guide`, `TripType`, `Tag` - Reference data

**Event Models** (`app/models/events.py`):
- `User` - Anonymous and registered users
- `Session` - Browser sessions
- `Event` - User interaction events
- `TripInteraction` - Aggregated trip engagement metrics

### Services

**Recommendation Service** (`app/services/recommendation.py`):
- Multi-factor scoring algorithm
- Geographic, theme, budget, duration matching
- Relaxed search for expanded results
- Configurable scoring weights

**Event Service** (`app/services/events.py`):
- User resolution (anonymous/authenticated)
- Session management
- Event validation and storage
- Real-time counter updates

### API Routes

Routes are organized into Flask Blueprints:

- **V2 API** (`app/api/v2/routes.py`) - Current recommendation API
- **Events API** (`app/api/events/routes.py`) - Event tracking
- **Analytics API** (`app/api/analytics/routes.py`) - Metrics and evaluation
- **Resources API** (`app/api/resources/routes.py`) - Reference data
- **System API** (`app/api/system/routes.py`) - Health checks

## Recommendation Algorithm

The recommendation engine uses a multi-factor scoring algorithm:

### Scoring Factors

- **Base Score**: 25 points (all passing trips)
- **Theme Matching**: +25 (2+ themes), +12 (1 theme), -15 (none)
- **Difficulty**: +15 (exact match)
- **Duration**: +12 (ideal), +8 (good, ±4 days)
- **Budget**: +12 (within), +8 (110%), +5 (120%)
- **Status Bonuses**: +7 (Guaranteed), +15 (Last Places)
- **Departing Soon**: +7 (within 30 days)
- **Geography**: +15 (direct country), +5 (continent)

### Score Thresholds

- **High Match**: ≥70 (Turquoise)
- **Medium Match**: ≥50 (Orange)
- **Low Match**: <50 (Red)

### Relaxed Search

If primary results < 6, system expands criteria:
- Geography: Same continent
- Trip type: All types (with penalty)
- Date: ±2 months
- Difficulty: ±2 levels
- Budget: 50% over

See `app/services/recommendation.py` for implementation details.

## Database Schema

### V2 Schema (Current)

The database uses a normalized schema:

- **TripTemplate** - Trip definition (description, pricing, difficulty)
- **TripOccurrence** - Scheduled instances (dates, guide, availability)
- **Many-to-Many** - Templates ↔ Tags, Templates ↔ Countries

This allows multiple scheduled instances of the same trip template.

### Migrations

Database migrations are in `migrations/`:

- `_001_add_recommendation_logging.py` - Recommendation logging
- `_002_add_user_tracking.py` - User tracking tables
- `_003_add_companies.py` - Companies table
- `_004_refactor_trips_to_templates.py` - V2 schema migration
- `_005_normalize_events_and_load_scenarios.py` - Event normalization
- `_006_add_properties_jsonb.py` - JSONB properties

## Authentication

### JWT Verification

The backend verifies Supabase JWT tokens:

- Extracts token from `Authorization` header
- Verifies signature with Supabase JWT secret
- Extracts user info (email, user ID)
- Optional authentication (guest mode supported)

See `app/core/auth.py` for implementation.

## Event Tracking

### Event Types

- `page_view` - Page views
- `search_submit` - Search submissions
- `click_trip` - Trip card clicks
- `impression` - Viewport impressions
- `filter_change` - Filter modifications
- `save_trip` - Trip saves
- `contact_whatsapp` - WhatsApp contact
- `contact_phone` - Phone contact

### Session Management

- Sessions expire after 30 minutes of inactivity
- Device type detection (mobile/tablet/desktop)
- Anonymous and authenticated user support
- Cross-device tracking via user identification

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use type hints where appropriate
- No ternary operators (use if-else statements)
- Docstrings for functions and classes

### Error Handling

- Use try-except blocks for database operations
- Return appropriate HTTP status codes
- Provide meaningful error messages
- Log errors for debugging

### Database Queries

- Use SQLAlchemy ORM for type safety
- Eager loading (`joinedload`, `selectinload`) to avoid N+1 queries
- Index frequently queried columns
- Use connection pooling for performance

## Scripts

### Database Scripts (`scripts/db/`)

- `seed.py` - Seed database with test data
- `check_schema.py` - Validate database schema
- `check_db_state.py` - Inspect database state

### Analytics Scripts (`scripts/analytics/`)

- `aggregate_daily_metrics.py` - Daily metrics aggregation
- `analyze_scoring_v2.py` - Scoring analysis
- `export_data.py` - Data export utilities

### Data Generation (`scripts/data_gen/`)

- `generate_personas.py` - Generate test personas
- `generate_trips.py` - Generate test trip data
- `create_realistic_data.py` - Create realistic datasets

## Testing

### Manual Testing

- Use Postman or curl for API testing
- Check health endpoint: `GET /api/health`
- Test recommendation endpoint with various preferences

### Evaluation

- Run evaluation scenarios: `POST /api/evaluation/run`
- Compare results against expected outcomes
- Analyze scoring patterns

## Deployment

The backend is deployed on Render:

1. Connect repository to Render
2. Configure environment variables
3. Set build and start commands
4. Deploy automatically on push

See `docs/deployment/RENDER_STEPS.md` for detailed instructions.

## Performance Considerations

### Database

- Connection pooling (5-10 connections)
- Eager loading to avoid N+1 queries
- Indexes on foreign keys and filtered columns

### Caching

- No caching currently (future: Redis for reference data)
- On-demand metrics computation

### Scalability

- Stateless API (scales horizontally)
- Database read replicas for analytics
- Partitioning for large tables (future)

## Troubleshooting

### Common Issues

**Database Connection Errors**
- Check `DATABASE_URL` format
- Verify Supabase connection string uses Session pooler (port 5432)
- Ensure `?sslmode=require` is included

**Import Errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version (3.10+)

**CORS Errors**
- Verify `ALLOWED_ORIGINS` includes frontend URL
- Check CORS configuration in `main.py`

## Related Documentation

- [Main README](../README.md) - Project overview
- [Architecture Docs](../docs/architecture/) - System architecture
- [API Docs](../docs/api/) - API reference
- [Deployment Guide](../docs/deployment/) - Deployment instructions
