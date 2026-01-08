# SmarTrip

> An intelligent trip recommendation platform that matches travelers with personalized travel experiences using a rule-based scoring algorithm.

[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00)](https://www.sqlalchemy.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)

---

## Key Features

- **Intelligent Search** - Personalized trip recommendations based on user preferences
- **Flexible Filtering** - Advanced search with multiple criteria including location, budget, duration, and difficulty
- **User Analytics** - Comprehensive tracking and analytics for search behavior and user interactions
- **Bilingual Support** - Full support for Hebrew and English content

---

## Architecture

```mermaid
flowchart TB
    subgraph Client["Browser"]
        UI["Next.js 14 App Router"]
    end

    subgraph Vercel["Vercel"]
        FE["Frontend<br/>React 18 + TypeScript"]
    end

    subgraph Render["Render"]
        BE["Flask API<br/>Python 3.10+"]
        SCHED["APScheduler<br/>Background Jobs"]
    end

    subgraph Database["PostgreSQL"]
        DB[(SmartTrip Database)]
    end

    UI --> FE
    FE -->|"REST API"| BE
    BE --> DB
    SCHED --> DB

    style Client fill:#f5f5f5,stroke:#333
    style Vercel fill:#000,stroke:#333,color:#fff
    style Render fill:#46E3B7,stroke:#333
    style Database fill:#336791,stroke:#333,color:#fff
```

---

## Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| Next.js 14 | React framework with App Router |
| React 18 | UI library |
| TypeScript 5 | Type safety |
| Tailwind CSS 3.4 | Utility-first styling |
| Lucide React | Icon library |

### Backend
| Technology | Purpose |
|------------|---------|
| Flask 3.0 | Python web framework |
| SQLAlchemy 2.0 | ORM and database toolkit |
| PostgreSQL 12+ | Relational database |
| APScheduler | Background job scheduling |
| Gunicorn | Production WSGI server |

---

## Prerequisites

- **Node.js** 18+
- **Python** 3.10+
- **PostgreSQL** 12+
- **npm** 9+ or **yarn**

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/trip-recommendations.git
cd trip-recommendations
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create `backend/.env`:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/smarttrip
ALLOWED_ORIGINS=http://localhost:3000
```

**Note:** For production, use your Supabase PostgreSQL connection string as the `DATABASE_URL`. The application will connect directly to your Supabase database.

Initialize database and start:

```bash
# For local development with empty database (optional)
python scripts/seed.py

# Start development server
python app.py
```

**Note:** In production, the application connects directly to your Supabase database. The seed script is only for local development with an empty database.

### 3. Frontend Setup

```bash
# From project root
npm install
```

Create `.env.local`:

```env
# Backend API URL (required)
NEXT_PUBLIC_API_URL=http://localhost:5000

# Supabase Authentication (optional - app works without it in guest mode)
# Get these from: https://app.supabase.com → Your Project → Settings → API
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

**Note:** Supabase authentication is optional. If not configured, the app operates in guest mode, allowing users to browse and search trips without authentication.

Start development server:

```bash
npm run dev    # Starts on :3000
```

---

## Usage

### Development

```bash
# Frontend
npm run dev          # Start Next.js dev server
npm run lint         # Run ESLint

# Backend
python app.py        # Start Flask dev server
python -m pytest     # Run test suite
```

### Production Build

```bash
# Frontend
npm run build
npm run start

# Backend (via Gunicorn)
gunicorn app:app
```

---

## API Reference

Base URL: `http://localhost:5000/api`

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check endpoint |
| `POST` | `/recommendations` | Get personalized trip recommendations |

### Resource Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/trips` | List available trips |
| `GET` | `/trips/:id` | Get trip details by ID |
| `GET` | `/countries` | List all countries |
| `GET` | `/trip-types` | List trip type categories |
| `GET` | `/tags` | List theme tags |
| `GET` | `/guides` | List tour guides |
| `GET` | `/companies` | List trip providers |

### Recommendations

```http
POST /api/recommendations
Content-Type: application/json
```

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
      "is_relaxed": false
    }
  ]
}
```

---

## Recommendation Algorithm

The recommendation engine uses a multi-factor scoring algorithm to rank trips based on user preferences. The algorithm considers:

- **Geographic preferences** - Countries and continents
- **Trip characteristics** - Type, themes, difficulty level
- **Temporal constraints** - Duration, departure dates
- **Budget alignment** - Price matching within acceptable range
- **Availability status** - Guaranteed departures and limited availability

Results are presented with match scores ranging from 0-100. When initial results are limited, the system automatically expands search criteria to provide additional recommendations.

For detailed algorithm documentation, see `docs/RECOMMENDATION_ENGINE_COMPREHENSIVE.md`.

---

## Project Structure

```
trip-recommendations/
+-- src/
|   +-- app/                    # Next.js App Router pages
|   |   +-- search/             # Search UI
|   |   +-- trip/[id]/          # Trip detail page
|   +-- lib/
|       +-- api.ts              # API client
+-- backend/
|   +-- app.py                  # Flask application entry point
|   +-- api_v2.py               # REST API endpoints  
|   +-- models_v2.py            # Database models
|   +-- database.py             # Database connection management
|   +-- auth_supabase.py        # Authentication middleware
|   +-- scheduler.py            # Background job scheduler
|   +-- events/                 # User event tracking
|   |   +-- api.py              # Event endpoints
|   |   +-- models.py           # Event models
|   |   +-- service.py          # Event processing
|   +-- recommender/            # Recommendation system
|   |   +-- logging.py          # Request logging
|   |   +-- metrics.py          # Performance metrics
|   |   +-- evaluation.py       # Quality evaluation
|   +-- scenarios/              # Test scenarios
|   +-- scripts/                # Development utilities
|   |   +-- seed.py             # Database seeding
|   |   +-- generate_trips.py   # Test data generation
|   |   +-- export_data.py      # Data export
|   |   +-- verify_schema.py    # Schema validation
+-- docs/                       # Technical documentation
|   +-- archive/                # Archived migrations & backups
+-- render.yaml                 # Render deployment config
+-- pytest.ini                  # Pytest configuration 
```

---

## Deployment

### Backend (Render)

1. Connect your repository to Render
2. Create a new Web Service using the `render.yaml` configuration
3. Set environment variables in Render dashboard:
   - `DATABASE_URL` - Your Supabase PostgreSQL connection string
   - `SECRET_KEY` - Flask secret key
   - `ALLOWED_ORIGINS` - Your frontend domain (e.g., `https://your-app.vercel.app`)
   - `FLASK_ENV=production`
4. Deploy

The backend will automatically initialize the database schema on first deployment.

### Frontend (Vercel)

1. Import repository to Vercel
2. Set environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
   ```
3. Deploy

---

## Documentation

Comprehensive documentation is available in the `docs/` folder:

- `PROJECT_SUMMARY_COMPREHENSIVE.md` - Full project specification
- `RECOMMENDATION_ENGINE_COMPREHENSIVE.md` - Algorithm deep dive
- `MASTER_TEST_PLAN.md` - QA test strategy

Generate PDFs:

```bash
python docs/generate_comprehensive_pdfs.py
```

---

## License

All Rights Reserved

---

## Author

Developed as a portfolio project demonstrating full-stack development, algorithm design, and production deployment practices.
