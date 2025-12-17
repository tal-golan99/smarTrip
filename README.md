# SmarTrip

> An intelligent trip recommendation platform that matches travelers with personalized travel experiences using a transparent, rule-based scoring algorithm.

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

- **Explainable Recommendations** - Every trip includes a match score (0-100) and human-readable explanations for why it was recommended
- **Two-Tier Search Algorithm** - Primary tier applies strict filters; relaxed tier automatically expands criteria when results are sparse
- **Bilingual Support** - Full Hebrew and English content with RTL layout support
- **Event Analytics** - Built-in tracking for search behavior, impressions, and user interactions

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
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/smarttrip
ALLOWED_ORIGINS=http://localhost:3000
```

Initialize database and start:

```bash
python scripts/seed.py    # Seed initial data
python app.py             # Start dev server on :5000
```

### 3. Frontend Setup

```bash
# From project root
npm install
```

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

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
| `GET` | `/health` | Health check with DB stats |

### Trip Resources

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/trips` | List all trips |
| `GET` | `/trips/:id` | Get trip by ID |
| `GET` | `/countries` | List all countries |
| `GET` | `/trip-types` | List trip categories |
| `GET` | `/tags` | List theme tags |
| `GET` | `/guides` | List tour guides |

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
  "score_thresholds": { "HIGH": 70, "MID": 50 },
  "data": [
    {
      "id": 517,
      "title": "Japan Cultural Discovery",
      "match_score": 88,
      "match_details": [
        "Excellent Theme Match [+25]",
        "Perfect Difficulty [+15]",
        "Country Match [+15]"
      ],
      "is_relaxed": false
    }
  ]
}
```

---

## Recommendation Algorithm

The scoring engine uses weighted signals to rank trips:

| Signal | Points | Condition |
|--------|--------|-----------|
| Base Score | +35 | Passes hard filters |
| Theme Match (2+) | +25 | Multiple theme overlap |
| Theme Match (1) | +12 | Single theme overlap |
| Theme Penalty | -15 | No theme overlap |
| Difficulty | +15 | Exact match |
| Duration | +12 / +8 | Ideal / Good fit |
| Budget | +12 / +8 / +5 | Perfect / Good / Acceptable |
| Geography | +15 / +5 | Country / Continent match |
| Status Bonus | +15 / +7 | Last Places / Guaranteed |
| Departing Soon | +7 | Within 30 days |

Scores are clamped to 0-100. When primary results are fewer than 6, relaxed search expands filters with a -20 base penalty.

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
|   +-- app.py                  # Flask application + scoring config
|   +-- models.py               # SQLAlchemy ORM models
|   +-- database.py             # DB session management
|   +-- scripts/                # Seeding, evaluation, analytics
|   +-- events/                 # Event tracking module
|   +-- scheduler.py            # Background jobs
+-- tests/
|   +-- backend/                # API and algorithm tests
|   +-- integration/            # End-to-end scenarios
|   +-- e2e/                    # Playwright UI tests
+-- docs/                       # Technical documentation
+-- render.yaml                 # Render deployment config
```

---

## Deployment

### Render (Backend)

The `render.yaml` configures:
- Python web service with Gunicorn
- PostgreSQL database
- Environment variables

Set `ALLOWED_ORIGINS` in the Render dashboard to your Vercel domain.

### Vercel (Frontend)

1. Import repository to Vercel
2. Set environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
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
