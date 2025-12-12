# SmartTrip Database Setup Guide

## Architecture Overview

**Backend:** Python (Flask) + SQLAlchemy  
**Frontend:** Next.js  
**Database:** PostgreSQL (Port 5433)

The Next.js frontend **only** fetches data from the Flask API - no direct database access.

---

## Prerequisites

### 1. Install PostgreSQL
- Download from: https://www.postgresql.org/download/
- Or use Docker: `docker run --name smarttrip-db -e POSTGRES_PASSWORD=password -p 5433:5432 -d postgres`

### 2. Install Python 3.10+
- Download from: https://www.python.org/downloads/

### 3. Install Node.js 18+
- Download from: https://nodejs.org/

---

## Step-by-Step Setup

### Step 1: Create PostgreSQL Database

Choose one of these methods:

#### Method A: Using pgAdmin (GUI)
1. Open pgAdmin
2. Connect to PostgreSQL server (localhost:5433)
3. Right-click "Databases" → Create → Database
4. Name: `smarttrip`
5. Click Save



### Step 2: Set Up Python Backend

#### 2.1 Navigate to Backend Folder
```bash
cd backend
```

#### 2.2 Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

#### 2.3 Install Python Dependencies
```bash
# Make sure you're in the backend folder with venv activated
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- SQLAlchemy (database ORM)
- psycopg2 (PostgreSQL driver)
- Flask-CORS (for Next.js communication)
- python-dotenv (environment variables)

#### 2.4 Create Environment File

Create a file named `.env` in the `backend/` folder:

**File: `backend/.env`**
```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=change-this-secret-key-in-production

# Database Configuration
# IMPORTANT: Replace 'password' with YOUR PostgreSQL password
DATABASE_URL=postgresql://postgres:password@localhost:5433/smarttrip

# Server Configuration
PORT=5000
HOST=0.0.0.0

# CORS Configuration (Next.js frontend URL)
FRONTEND_URL=http://localhost:3000
```

**Important:** Replace `password` in DATABASE_URL with your actual PostgreSQL password!

---

### Step 3: Initialize and Seed the Database

```bash
# Make sure you're in the backend/ folder with venv activated
python seed.py
```

**What this does:**
- Creates all 5 database tables (countries, guides, tags, trips, trip_tags)
- Populates 115+ countries from Ayala Geographic website
- Adds 23 trip type tags (Safari, Trekking, Cultural, etc.)
- Creates 5 sample tour guides

**Expected Output:**
```
🌱 Starting database seed...
✅ Database tables created successfully!
📍 Seeding countries...
✅ Seeded 115 countries
🏷️  Seeding tags...
✅ Seeded 23 tags
👥 Seeding sample guides...
✅ Seeded 5 guides
✨ Database seeded successfully!
```

---

### Step 4: Start the Flask Backend

```bash
# Make sure you're in backend/ with venv activated
python app.py
```

**Expected Output:**
```
✅ Database tables created successfully!
🚀 SmartTrip API running on http://0.0.0.0:5000
📚 API Documentation: http://0.0.0.0:5000/api/health
```

**Test the API:**
- Open browser: http://localhost:5000/api/health
- You should see: `{"status":"healthy","service":"SmartTrip API","version":"1.0.0"}`

---

### Step 5: Set Up Next.js Frontend

Open a **new terminal** (keep Flask running in the other one).

#### 5.1 Navigate to Project Root
```bash
# If you're in backend/, go back to root
cd ..
```

#### 5.2 Create Frontend Environment File

Create a file named `.env.local` in the **project root**:

**File: `.env.local`**
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

#### 5.3 Start Next.js Development Server
```bash
npm run dev
```

**Expected Output:**
```
▲ Next.js 16.0.8 (Turbopack)
- Local:        http://localhost:3000
- Network:      http://10.x.x.x:3000

✓ Ready in 645ms
```

---

## Verification & Testing

### Test Backend API Endpoints

Open your browser and visit these URLs:

1. **Health Check:**  
   http://localhost:5000/api/health

2. **View All Countries:**  
   http://localhost:5000/api/countries

3. **View Countries by Continent:**  
   http://localhost:5000/api/countries?continent=ASIA

4. **View Trip Tags:**  
   http://localhost:5000/api/tags

5. **View Guides:**  
   http://localhost:5000/api/guides

### Test Frontend

Visit: http://localhost:3000

---

## Database Schema

### Tables (Normalized to 3NF)

#### 1. **countries**
- `id` (Primary Key)
- `name` (English name)
- `name_he` (Hebrew name - עברית)
- `continent` (Enum: Africa, Asia, Europe, etc.)
- `created_at`, `updated_at`

#### 2. **guides**
- `id` (Primary Key)
- `name`, `email`, `phone`
- `gender` (Enum: Male, Female, Other)
- `age`
- `bio` (English), `bio_he` (Hebrew)
- `image_url`
- `is_active` (Boolean)
- `created_at`, `updated_at`

#### 3. **tags**
- `id` (Primary Key)
- `name` (English), `name_he` (Hebrew)
- `description`
- `created_at`, `updated_at`

#### 4. **trips**
- `id` (Primary Key)
- `title` (English), `title_he` (Hebrew)
- `description` (English), `description_he` (Hebrew)
- `image_url`
- `start_date`, `end_date`
- `price`, `single_supplement_price`
- `max_capacity`, `spots_left`
- `status` (Enum: Open, Guaranteed, Last Places, Full, Cancelled)
- `difficulty_level` (1=Easy, 2=Moderate, 3=Hard)
- `country_id` (Foreign Key → countries)
- `guide_id` (Foreign Key → guides)
- `created_at`, `updated_at`

#### 5. **trip_tags** (Junction Table)
- `trip_id` (Foreign Key → trips)
- `tag_id` (Foreign Key → tags)
- `created_at`
- Composite Primary Key: (trip_id, tag_id)

### Data Integrity Features
- ✅ Foreign Keys with referential integrity
- ✅ Enums for type safety
- ✅ Unique constraints (no duplicates)
- ✅ Cascade deletes where appropriate
- ✅ Indexes for query optimization

---

## Common Issues & Solutions

### Issue: "Module not found" in Python
**Solution:**
```bash
cd backend
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Issue: "Connection refused" to database
**Solutions:**
- Check PostgreSQL is running on port 5433
- Verify DATABASE_URL in `backend/.env`
- Confirm username/password are correct
- Test connection: `psql -U postgres -p 5433 -d smarttrip`

### Issue: "Port already in use" (5000)
**Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:5000 | xargs kill -9
```

### Issue: "psycopg2 installation failed"
**Windows:** Install Visual C++ Build Tools  
**Or use:** `pip install psycopg2-binary` (already in requirements.txt)

---

## Database Management Commands

### View Database Content
```bash
# Connect to database
psql -U postgres -p 5433 -d smarttrip

# List all tables
\dt

# View countries
SELECT * FROM countries LIMIT 10;

# View trips with relations
SELECT t.title, c.name as country, g.name as guide, t.status
FROM trips t
JOIN countries c ON t.country_id = c.id
JOIN guides g ON t.guide_id = g.id;

# Count records
SELECT 
  (SELECT COUNT(*) FROM countries) as countries,
  (SELECT COUNT(*) FROM tags) as tags,
  (SELECT COUNT(*) FROM guides) as guides,
  (SELECT COUNT(*) FROM trips) as trips;
```

### Reset Database (Warning: Deletes All Data!)
```bash
# Drop and recreate database
psql -U postgres -p 5433
DROP DATABASE smarttrip;
CREATE DATABASE smarttrip;
\q

# Re-run seed script
cd backend
python seed.py
```

---

## Next Steps

Now that your database is set up:

1. ✅ **Backend API is running** on port 5000
2. ✅ **Frontend is running** on port 3000
3. ✅ **Database has seed data**

### What to Build Next:

1. **Add Real Trips** - Insert actual tour data into the `trips` table
2. **Build Frontend UI** - Create search and listing pages
3. **Implement Recommendation Algorithm** - Complete the `/api/recommendations` endpoint
4. **Add i18n** - Set up Hebrew/English language switching
5. **Match Ayala Geographic Design** - Apply colors and branding

---

## Resources

- **Backend API Docs:** `backend/README.md`
- **API Client Usage:** `src/lib/api.ts`
- **Example Components:** `src/app/example-api-usage.tsx`
- **Full Project Docs:** `README.md`
- **Quick Start:** `QUICKSTART.md`

---

**Database setup complete! Happy coding! 🎉**

