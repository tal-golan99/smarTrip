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
    end

    subgraph Database["PostgreSQL"]
        DB[(SmartTrip Database<br/>Supabase)]
    end

    UI --> FE
    FE -->|"REST API"| BE
    BE --> DB

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
| Supabase | Authentication and database client |

### Backend
| Technology | Purpose |
|------------|---------|
| Flask 3.0 | Python web framework |
| SQLAlchemy 2.0 | ORM and database toolkit |
| PostgreSQL 12+ | Relational database (Supabase) |
| Gunicorn | Production WSGI server |

---

## Prerequisites

- **Node.js** 18+
- **Python** 3.10+
- **PostgreSQL** 12+ (or Supabase account)
- **npm** 9+ or **yarn**

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/tal-golan99/smarTrip.git
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
FLASK_APP=app.main:app
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require
ALLOWED_ORIGINS=http://localhost:3000
SUPABASE_JWT_SECRET=your-jwt-secret-here
```

**Important:** 
- Use **Session pooler** connection string (port 5432) for local development
- Add `?sslmode=require` at the end of the connection string
- Get the connection string from Supabase Dashboard → Settings → Database → Connection string → URI tab

Initialize database and start:

```bash
# For local development with empty database (optional)
python scripts/db/seed.py

# Start development server
python -m app.main
# OR
python app/main.py
```

**Note:** In production, the application connects directly to your Supabase database. The seed script is only for local development with an empty database.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

Create `frontend/.env.local` (in the frontend directory):

```env
# Backend API URL (required)
NEXT_PUBLIC_API_URL=http://localhost:5000

# Supabase Authentication (optional - app works without it in guest mode)
# Get these from: https://app.supabase.com → Your Project → Settings → API
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

**Important:** 
- The `.env.local` file must be in the `frontend/` directory (where `next.config.js` is located)
- Next.js only reads environment files from the directory where it runs
- This file is automatically gitignored and will not be committed

**Note:** Supabase authentication is optional. If not configured, the app operates in guest mode, allowing users to browse and search trips without authentication.

Start development server:

```bash
# From frontend directory
cd frontend
npm run dev    # Starts on :3000
```

---

## Usage

### Development

```bash
# Frontend (from frontend/ directory)
npm run dev          # Start Next.js dev server
npm run lint         # Run ESLint
npm run build        # Build for production

# Backend (from backend/ directory)
python -m app.main   # Start Flask dev server
python scripts/db/seed.py  # Seed database (optional)
```

### Production Build

```bash
# Frontend
cd frontend
npm run build
npm run start

# Backend (via Gunicorn)
cd backend
gunicorn app.main:app --bind 0.0.0.0:$PORT
```

---

## Project Structure

```
trip-recommendations/
├── frontend/                    # Next.js frontend application
│   ├── src/
│   │   ├── app/                # Next.js App Router pages
│   │   │   ├── auth/           # Authentication pages
│   │   │   │   └── callback/   # Auth callback handler
│   │   │   ├── search/         # Search UI
│   │   │   │   └── results/    # Search results page
│   │   │   ├── trip/[id]/      # Trip detail page
│   │   │   ├── error.tsx       # Error page
│   │   │   ├── not-found.tsx   # 404 page
│   │   │   ├── layout.tsx      # Root layout
│   │   │   └── page.tsx        # Home page
│   │   ├── components/         # React components
│   │   │   ├── features/       # Feature components
│   │   │   └── ui/             # UI components
│   │   ├── hooks/              # Custom React hooks
│   │   │   └── useTracking.ts  # Tracking hook
│   │   ├── lib/                # Client-side libraries
│   │   │   ├── dataStore.tsx   # Data store context
│   │   │   └── supabaseClient.ts  # Supabase client
│   │   └── services/           # API and tracking services
│   │       ├── api.service.ts  # API client
│   │       └── tracking.service.ts  # Tracking service
│   ├── public/                 # Static assets
│   │   ├── images/             # Image assets
│   │   │   ├── continents/     # Continent images
│   │   │   ├── logo/           # Logo images
│   │   │   └── trip status/    # Trip status icons
│   │   └── *.svg               # SVG icons
│   ├── .env.local             # Frontend environment variables
│   ├── CHECK_ENV.md           # Environment setup guide
│   ├── eslint.config.mjs      # ESLint configuration
│   ├── next.config.js         # Next.js configuration
│   ├── package.json           # Frontend dependencies
│   ├── postcss.config.mjs     # PostCSS configuration
│   ├── tailwind.config.ts     # Tailwind CSS configuration
│   └── tsconfig.json          # TypeScript configuration
│
├── backend/                    # Flask backend application
│   ├── app/                    # Main application package
│   │   ├── api/                # API routes
│   │   │   ├── analytics/      # Analytics endpoints
│   │   │   ├── events/         # Event tracking endpoints
│   │   │   ├── resources/      # Resource endpoints
│   │   │   ├── system/         # System endpoints
│   │   │   └── v2/             # API V2 endpoints
│   │   ├── core/               # Core functionality
│   │   │   ├── auth.py         # Authentication middleware
│   │   │   ├── config.py       # Configuration management
│   │   │   └── database.py     # Database connection
│   │   ├── models/             # Database models
│   │   │   ├── events.py       # Event models
│   │   │   └── trip.py         # Trip models (Templates/Occurrences)
│   │   ├── services/           # Business logic
│   │   │   ├── events.py       # Event processing
│   │   │   └── recommendation.py  # Recommendation algorithm
│   │   └── main.py             # Flask application entry point
│   ├── migrations/             # Database migrations
│   ├── recommender/            # Recommendation system
│   │   ├── logging.py          # Request logging
│   │   ├── metrics.py          # Performance metrics
│   │   └── evaluation.py       # Quality evaluation
│   ├── scenarios/              # Test scenarios and personas
│   │   └── generated_personas.json  # Generated persona data
│   ├── scripts/                # Development utilities
│   │   ├── _archive/           # Archived scripts
│   │   ├── analytics/          # Analytics scripts
│   │   ├── data_gen/           # Data generation scripts
│   │   └── db/                 # Database scripts
│   ├── .env                   # Backend environment variables
│   ├── .gitignore             # Backend gitignore
│   ├── Procfile               # Production process file
│   ├── requirements.txt       # Python dependencies
│   ├── requirements-dev.txt   # Development dependencies
│   └── runtime.txt            # Python runtime version
│
├── docs/                      # Documentation
├── .github/                   # GitHub configuration
│   └── workflows/             # CI/CD workflows
│       └── README.md          # Workflows documentation
├── .gitignore                 # Root gitignore
├── Procfile                   # Root Procfile
├── README.md                  # This file
├── render.yaml                # Render deployment config
└── vercel.json                # Vercel deployment config
```

---

## API Reference

Base URL: `http://localhost:5000/api`

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check endpoint |
| `POST` | `/v2/recommendations` | Get personalized trip recommendations |

### Resource Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v2/locations` | List all countries |
| `GET` | `/v2/trip-types` | List trip type categories |
| `GET` | `/v2/tags` | List theme tags |
| `GET` | `/v2/guides` | List tour guides |
| `GET` | `/v2/companies` | List trip providers |

### Event Tracking Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/events/batch` | Batch upload user events |
| `GET` | `/events/stats` | Get event statistics |

### Recommendations

```http
POST /api/v2/recommendations
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

## Deployment

### Backend (Render)

1. Connect your repository to Render
2. Create a new Web Service using the `render.yaml` configuration
3. Set environment variables in Render dashboard:
   - `DATABASE_URL` - Your Supabase PostgreSQL connection string (Session pooler, port 5432)
   - `SECRET_KEY` - Flask secret key
   - `ALLOWED_ORIGINS` - Your frontend domain (e.g., `https://your-app.vercel.app`)
   - `SUPABASE_JWT_SECRET` - From Supabase Settings → API → JWT Settings
   - `FLASK_ENV=production`
4. Deploy

The backend will automatically initialize the database schema on first deployment.

**Important:** Use the **Session pooler** connection string (port 5432) with `?sslmode=require` for production.

### Frontend (Vercel)

1. Import repository to Vercel
2. **Set Root Directory to `frontend`** in Vercel project settings:
   - Go to Settings → General → Root Directory
   - Set to `frontend`
3. Set environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
   ```
4. Deploy

**Note:** The `vercel.json` file is configured, but you may also need to set the root directory in the Vercel dashboard.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Required |
|---------|-------------|----------|
| `FLASK_APP` | Flask application entry point | Yes (`app.main:app`) |
| `FLASK_ENV` | Environment (development/production) | Yes |
| `SECRET_KEY` | Flask secret key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | Yes |
| `SUPABASE_JWT_SECRET` | Supabase JWT secret for auth | Optional |

### Frontend (`frontend/.env.local`)

| Variable | Description | Required |
|---------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | Optional |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key | Optional |

---

## Database Connection

### Supabase Connection Strings

**For Local Development:**
- Use **Session pooler** (port 5432)
- Format: `postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require`

**For Production:**
- Use **Session pooler** (port 5432)
- Same format as local development

**Important:** 
- Get the connection string from Supabase Dashboard → Settings → Database → Connection string → **URI** tab

---

## Documentation

Comprehensive documentation is available in the `docs/` folder:

- `DATABASE_CONNECTION_GUIDE.md` - Database connection troubleshooting
- `SUPABASE_CONNECTION_STRING_CHOICE.md` - Which connection string to use
- `DEPLOYMENT_CONFIGURATION.md` - Deployment setup guide
- `PYTHON_PACKAGE_STRUCTURE.md` - Understanding `__init__.py` files

---

## License

All Rights Reserved

---

## Author

Developed as a portfolio project demonstrating full-stack development, algorithm design, and production deployment practices.
