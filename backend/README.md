# SmartTrip Backend API

Flask + SQLAlchemy backend for the SmartTrip intelligent recommendation engine.

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

### 2. Installation

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE smarttrip;
```

### 4. Environment Configuration

Create a `.env` file in the `backend/` directory:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5433/smarttrip

# Server Configuration
PORT=5000
HOST=0.0.0.0

# CORS Configuration
FRONTEND_URL=http://localhost:3000
```

### 5. Initialize Database & Seed Data

```bash
# Run seed script to create tables and populate initial data
python seed.py
```

### 6. Run Development Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## 📚 API Endpoints

### Health Check
- `GET /api/health` - Server health check

### Countries
- `GET /api/countries` - Get all countries (filter by `?continent=ASIA`)
- `GET /api/countries/:id` - Get specific country

### Guides
- `GET /api/guides` - Get all active guides
- `GET /api/guides/:id` - Get specific guide

### Tags
- `GET /api/tags` - Get all trip tags/types

### Trips
- `GET /api/trips` - Get all trips (with filters)
  - Query params: `country_id`, `guide_id`, `tag_id`, `status`, `difficulty`, `start_date`, `end_date`, `include_relations`
- `GET /api/trips/:id` - Get specific trip with full details

### Recommendations
- `POST /api/recommendations` - Get personalized trip recommendations (coming soon)

## 🗄️ Database Schema

### Tables
1. **countries** - Destination countries with continent classification
2. **guides** - Tour guides with contact info and specializations
3. **tags** - Trip categories/types (Safari, Trekking, Cultural, etc.)
4. **trips** - Organized tours with dates, pricing, capacity
5. **trip_tags** - Many-to-Many junction table

### Enums
- `TripStatus`: Open, Guaranteed, Last Places, Full, Cancelled
- `Gender`: Male, Female, Other
- `Continent`: Africa, Asia, Europe, North America, South America, Oceania, Middle East, Antarctica

## 🔧 Development

### Project Structure

```
backend/
├── app.py              # Flask application and API routes
├── models.py           # SQLAlchemy database models
├── database.py         # Database configuration and session management
├── seed.py             # Database seeding script
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
└── README.md          # This file
```

### Adding New Data

To add countries, guides, tags, or trips, you can either:
1. Modify `seed.py` and re-run it
2. Use PostgreSQL client to insert data directly
3. Create API endpoints for admin panel (future feature)

## 🌐 CORS Configuration

The API allows requests from the Next.js frontend running on `http://localhost:3000` by default.

To change this, update the `FRONTEND_URL` in your `.env` file.

## 📝 Notes

- All API responses follow the format: `{ success: bool, data: any, error?: string }`
- Hebrew (עברית) is supported with `name_he`, `title_he`, `description_he` fields
- Database uses normalized 3NF schema with foreign keys and constraints
- Real-time inventory management through `spots_left` field


