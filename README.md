# SmartTrip - Trip Recommendation System

A production-ready travel recommendation platform with intelligent matching algorithms, built with Next.js and Flask. The system processes 587+ trips across 105+ countries using a two-tier scoring algorithm to deliver personalized recommendations.

## Overview

SmartTrip is a full-stack web application that provides intelligent trip recommendations based on user preferences. The platform uses weighted scoring algorithms to match trips against multiple criteria including geography, budget, duration, difficulty, and themes.

### Development

This project was developed using Cursor AI to accelerate development while maintaining enterprise-level code quality and comprehensive test coverage.

## Technical Stack

### Frontend
- Next.js 14 (App Router)
- React 18
- TypeScript 5.x
- Tailwind CSS 3.4
- Lucide React (Icons)

### Backend
- Flask 3.x (Python 3.10+)
- SQLAlchemy 2.x (ORM)
- PostgreSQL 12+
- RESTful API

### Testing
- Custom Python test suite
- 255 automated tests
- 99.2% pass rate

## Core Features

### Two-Tier Recommendation Algorithm

**Primary Tier**
- Strict filtering based on user preferences
- Base score of 25 points
- Weighted scoring across 6 criteria
- Returns top 10 matches

**Relaxed Tier**
- Activated when primary results < 6 trips
- Expands geographic scope to continent level
- Extends date range by 2 months
- Applies penalty scoring for flexibility

### Search Capabilities
- Geographic filtering (continent, country)
- Trip type selection
- Multi-theme preferences (up to 3)
- Date filtering (year/month)
- Budget constraints
- Difficulty levels (1-5 scale)
- Duration ranges

### Security
- Input validation and sanitization
- XSS protection
- SQL injection prevention
- Type safety enforcement
- Boundary condition handling

### Internationalization
- Full Hebrew and English support
- RTL layout implementation
- Bilingual content across all entities

## Installation

### Prerequisites

- Node.js 18 or higher
- Python 3.10 or higher
- PostgreSQL 12 or higher
- pip (latest version)
- npm 9 or higher

### Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE smarttrip;
```

### Backend Installation

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create backend/.env with the following:
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:PASSWORD@localhost:5432/smarttrip
PORT=5000
HOST=0.0.0.0
FRONTEND_URL=http://localhost:3000

# Initialize database
python seed.py

# Start backend server
python app.py
```

Backend will be available at http://localhost:5000

### Frontend Installation

```bash
# From project root
npm install

# Configure environment variables
# Create .env.local with:
NEXT_PUBLIC_API_URL=http://localhost:5000

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

## Project Structure

```
trip-recommendations/
├── src/
│   ├── app/
│   │   ├── search/              # Search interface
│   │   │   ├── page.tsx         # Search form
│   │   │   └── results/         # Results display
│   │   ├── trip/[id]/           # Trip details
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Home page
│   └── lib/
│       └── api.ts               # API client
├── backend/
│   ├── app.py                   # Flask application
│   ├── models.py                # Database models
│   ├── database.py              # Database configuration
│   ├── seed.py                  # Database seeding
│   ├── requirements.txt         # Python dependencies
│   └── tests/                   # Test suite
│       ├── test_api_endpoints.py
│       ├── test_search_scenarios.py
│       └── run_all_tests.py
├── public/                      # Static assets
├── .env.local                   # Frontend environment
├── backend/.env                 # Backend environment
└── README.md
```

## API Documentation

### Base URL

Development: http://localhost:5000
Production: Configure via environment variables

### Endpoints

#### Health Check
```
GET /api/health
```

Returns system status and database statistics.

#### Countries
```
GET /api/countries
GET /api/countries?continent=Asia
```

Returns list of available countries with continent mapping.

#### Trips
```
GET /api/trips
GET /api/trips/:id
```

Query parameters:
- limit: Results per page (default: 50, max: 1000)
- offset: Starting position (default: 0)
- country_id: Filter by country
- guide_id: Filter by guide
- tag_id: Filter by tag
- status: Filter by status
- difficulty: Filter by difficulty level
- start_date: Filter trips after date
- end_date: Filter trips before date

#### Recommendations
```
POST /api/recommendations
Content-Type: application/json
```

Request body:
```json
{
  "selected_countries": [1, 5, 10],
  "selected_continents": ["Asia", "Europe"],
  "preferred_type_id": 5,
  "preferred_theme_ids": [3, 7, 10],
  "min_duration": 7,
  "max_duration": 14,
  "budget": 10000,
  "difficulty": 2,
  "year": "2026",
  "month": "3"
}
```

All parameters are optional.

Response:
```json
{
  "success": true,
  "count": 10,
  "primary_count": 6,
  "relaxed_count": 4,
  "total_candidates": 45,
  "total_trips": 587,
  "has_relaxed_results": true,
  "score_thresholds": {
    "HIGH": 70,
    "MID": 50
  },
  "data": [
    {
      "match_score": 87,
      "is_relaxed": false,
      "match_details": ["Theme Match [+25]", "Perfect Difficulty [+15]"],
      "trip": { /* trip object */ }
    }
  ]
}
```

#### Tags
```
GET /api/tags
```

Returns available trip types and themes for filtering.

#### Trip Types
```
GET /api/trip-types
```

Returns all trip type categories.

#### Guides
```
GET /api/guides
```

Returns all tour guide profiles.

## Recommendation Algorithm

### Scoring System

The algorithm uses a weighted point system with a base score of 25 points. Trips are evaluated across multiple criteria and can achieve a maximum score of 100 (scores are clamped).

**Scoring Weights:**

| Criterion | Weight | Condition |
|-----------|--------|-----------|
| Base Score | 25 | All trips |
| Theme Match (Full) | +25 | 2+ matching themes |
| Theme Match (Partial) | +12 | 1 matching theme |
| Theme Penalty | -15 | No matching themes |
| Difficulty Match | +15 | Exact difficulty level |
| Duration (Ideal) | +12 | Within specified range |
| Duration (Good) | +8 | Within 4 days of range |
| Budget (Perfect) | +12 | Within budget |
| Budget (Good) | +8 | Within 10% over budget |
| Budget (Acceptable) | +5 | Within 30% over budget |
| Status (Guaranteed) | +7 | Guaranteed departure |
| Status (Last Places) | +15 | Limited availability |
| Departing Soon | +7 | Within 60 days |
| Geography (Direct) | +15 | Direct country match |
| Geography (Continent) | +5 | Continent match |

**Score Ranges:**

- 70-100: High match (Turquoise indicator)
- 50-69: Medium match (Orange indicator)
- 0-49: Low match (Red indicator)

### Filtering Logic

**Primary Tier (Strict):**
- Geography: Selected countries or continents
- Dates: Exact year and month match
- Status: Available spots only
- Duration: Within 7 days of preference
- Difficulty: Within 1 level

**Relaxed Tier (Flexible):**
- Geography: Expands to full continent
- Dates: 2 months before and after selection
- Duration: Within 10 days of preference
- Difficulty: Within 2 levels
- Budget: Up to 50% over (vs 30% in primary)
- Trip Type: All types (with -10 penalty)
- Base Penalty: -20 points

The relaxed tier activates automatically when primary results return fewer than 6 trips.

## Testing

### Running Tests

```bash
cd backend

# Run all tests
python tests/run_all_tests.py

# Run API endpoint tests
python tests/test_api_endpoints.py

# Run search scenario tests
python tests/test_search_scenarios.py
```

### Test Coverage

- API Endpoint Tests: 40 tests
- Search Scenarios: 215 tests
- Total: 255 tests
- Pass Rate: 99.2%

Test categories include:
- Health checks
- CRUD operations
- Recommendations algorithm
- Input validation
- Boundary conditions
- Security (XSS, SQL injection)
- Error handling
- Performance benchmarks

## Database Schema

### Tables

**countries**
- 105+ destinations with continent mapping
- Bilingual names (English/Hebrew)

**guides**
- Tour guide profiles
- Contact information and specializations
- Bilingual biographies

**tags**
- Trip categorization
- Categories: Type and Theme

**trip_types**
- Trip style definitions (Safari, Train Tours, Cruise, etc.)

**trips**
- Core trip data with pricing and dates
- Difficulty levels (1-5)
- Status tracking (Open, Guaranteed, Last Places, Full, Cancelled)
- Foreign keys: country_id, guide_id, trip_type_id

**trip_tags**
- Many-to-many relationship between trips and tags

### Indexes

Performance indexes are applied on:
- trips.start_date
- trips.country_id
- trips.trip_type_id
- trips.status
- trip_tags.trip_id
- trip_tags.tag_id

## Deployment

### Environment Configuration

Production environment variables should be configured with secure values. Never commit environment files to version control.

### Deployment Platforms

**Frontend:**
- Vercel (recommended)
- Netlify
- AWS Amplify

**Backend:**
- Render (recommended)
- Railway
- Heroku
- AWS Elastic Beanstalk

**Database:**
- Render PostgreSQL
- AWS RDS
- Heroku Postgres

### CORS Configuration

Update allowed origins in backend/app.py for production:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "https://your-production-domain.com"
        ]
    }
})
```

## Development

### Backend Scripts

```bash
python app.py              # Start development server
python seed.py             # Seed database
python tests/run_all_tests.py  # Run test suite
```

### Frontend Scripts

```bash
npm run dev      # Development server
npm run build    # Production build
npm run start    # Production server
npm run lint     # Run ESLint
```

## Troubleshooting

### Database Connection Issues

Verify PostgreSQL is running and DATABASE_URL is correctly configured in backend/.env.

### Port Conflicts

If ports 3000 or 5000 are in use:

Windows:
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

Mac/Linux:
```bash
lsof -ti:5000 | xargs kill -9
```

### Module Not Found Errors

Ensure virtual environment is activated and dependencies are installed:

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### CORS Errors

Verify FRONTEND_URL in backend/.env matches the frontend URL and CORS origins are properly configured in app.py.

## Performance Considerations

Current average response time is approximately 2 seconds per request. This is primarily due to database connection overhead. Recommended optimizations:

- Implement connection pooling
- Add Redis caching for static data
- Optimize database queries
- Add database indexes on frequently filtered columns

## Contributing

This is a proprietary project. For collaboration inquiries, contact the development team.

## License

All Rights Reserved

## Support

For issues or questions, refer to the troubleshooting section or contact the development team.
