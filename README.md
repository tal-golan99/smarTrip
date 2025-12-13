# SmartTrip - Intelligent Trip Recommendation System

A sophisticated trip recommendation platform with a Next.js frontend and Flask backend, featuring an AI-powered matching algorithm that personalizes trip suggestions based on user preferences.

## Features

- **Smart Recommendations**: Weighted scoring algorithm (0-100 points) matching trips to user preferences
- **Advanced Filtering**: By continent, country, trip type, themes, dates, budget, and difficulty
- **Bilingual Support**: Full Hebrew and English interface with RTL support
- **Real-time Availability**: Live tracking of trip status and available spots
- **Premium UI**: Modern, responsive design with image-based cards and smooth animations
- **RESTful API**: Well-documented endpoints for seamless frontend integration

## Tech Stack

### Frontend
- Next.js 14 with App Router
- React 18 with TypeScript
- Tailwind CSS for styling
- Lucide Icons

### Backend
- Flask (Python 3.10+)
- SQLAlchemy ORM
- PostgreSQL database
- RESTful API architecture

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL 12+

### 1. Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE smarttrip;
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy the following into backend/.env:
```

**`backend/.env`:**
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=change-this-secret-key-in-production
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/smarttrip
PORT=5000
HOST=0.0.0.0
FRONTEND_URL=http://localhost:3000
```

```bash
# Initialize database with seed data
python seed.py

# Start Flask server
python app.py
```

Backend runs at: `http://localhost:5000`

### 3. Frontend Setup

```bash
# Return to project root
cd ..

# Install dependencies
npm install

# Create .env.local file
```

**`.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

```bash
# Start development server
npm run dev
```

Frontend runs at: `http://localhost:3000`

## Project Structure

```
trip-recommendations/
├── src/
│   ├── app/
│   │   ├── search/              # Search page with filters
│   │   │   └── results/         # Results display with recommendations
│   │   ├── trip/[id]/           # Individual trip details
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Home page
│   └── lib/
│       └── api.ts               # API client functions
├── backend/
│   ├── app.py                   # Flask API routes
│   ├── models.py                # Database models
│   ├── database.py              # Database configuration
│   ├── seed.py                  # Database seeding script
│   └── requirements.txt         # Python dependencies
└── public/
    └── images/                  # Static assets
```

## Database Schema

The system uses 5 normalized tables:

### 1. Countries
- 115+ destinations with continent mapping
- Bilingual names (English/Hebrew)

### 2. Guides
- Tour guide profiles with contact information
- Bilingual bios and specializations

### 3. Tags
- Trip categorization (Type and Theme)
- **Type**: Trip style (Safari, Train Tours, Cruise, etc.)
- **Theme**: Trip content (Wildlife, Cultural, Adventure, etc.)

### 4. Trips
- Core trip data with pricing, dates, capacity
- Difficulty levels (1=Easy, 2=Moderate, 3=Hard)
- Status tracking (Open, Guaranteed, Last Places, Full, Cancelled)

### 5. Trip_Tags
- Many-to-many relationship between trips and tags

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### Get Countries
```http
GET /api/countries
GET /api/countries?continent=Asia
```

#### Get Tags
```http
GET /api/tags
```

Returns trip types and themes for filtering.

#### Get Guides
```http
GET /api/guides
```

#### Get Trips
```http
GET /api/trips
GET /api/trips/:id
```

Query parameters:
- `country_id`: Filter by country
- `guide_id`: Filter by guide
- `tag_id`: Filter by tag
- `status`: Filter by trip status
- `difficulty`: Filter by difficulty level
- `start_date`, `end_date`: Date range filtering

#### Get Recommendations
```http
POST /api/recommendations
Content-Type: application/json

{
  "selected_continents": ["Asia", "Europe"],
  "selected_countries": [1, 5, 10],
  "preferred_type_id": 5,
  "preferred_theme_ids": [3, 7, 10],
  "min_duration": 7,
  "max_duration": 14,
  "budget": 10000,
  "difficulty": 2,
  "start_date": "2025-03-01"
}
```

**Response:**
```json
{
  "success": true,
  "count": 10,
  "total_candidates": 45,
  "data": [
    {
      "id": 123,
      "title": "Safari Adventure in Kenya",
      "titleHe": "הרפתקת ספארי בקניה",
      "price": 12000,
      "duration": 10,
      "startDate": "2025-03-15",
      "difficulty": 2,
      "status": "Guaranteed",
      "match_score": 87,
      "match_details": [
        "Perfect Style Match",
        "Excellent Theme Match (2 interests)",
        "Perfect Difficulty Level",
        "Ideal Duration",
        "Guaranteed Departure"
      ],
      "country": {...},
      "guide": {...},
      "tags": [...]
    }
  ]
}
```

## Recommendation Algorithm

The SmartTrip engine uses a **Weighted Scoring System** (0-100 points):

### Scoring Breakdown

| Criterion | Max Points | Description |
|-----------|------------|-------------|
| **Type Match** | 25 pts | Exact trip style match (Safari, Cruise, etc.) |
| **Theme Match** | 15 pts | Interest alignment (Wildlife, Cultural, etc.) |
| **Difficulty** | 20 pts | Physical difficulty preference |
| **Duration** | 15 pts | Trip length fit within desired range |
| **Budget** | 15 pts | Price alignment with user budget |
| **Business Logic** | 10 pts | Guaranteed departures, urgency bonuses |

### How It Works

1. **Hard Filtering**: Eliminates trips that don't meet mandatory criteria (geography, dates, availability)
2. **Weighted Scoring**: Each remaining trip is scored across 6 dimensions
3. **Ranking**: Trips sorted by match score, top 10 returned with explanations

### Example High Score (95/100)

```
User wants: Safari in Africa, 7-14 days, $15k budget, Moderate difficulty
Perfect match: 25 (Type) + 15 (Themes) + 20 (Difficulty) + 15 (Duration) + 15 (Budget) + 5 (Business) = 95 points
```

## Frontend Integration

### Using the API Client

```typescript
import { getRecommendations, RecommendationPreferences } from '@/lib/api';

const preferences: RecommendationPreferences = {
  selected_continents: ['Asia'],
  preferred_type_id: 1,
  preferred_theme_ids: [3, 4, 7],
  min_duration: 10,
  max_duration: 16,
  budget: 10000,
  difficulty: 2,
  start_date: '2025-03-01'
};

const response = await getRecommendations(preferences);

if (response.success && response.data) {
  response.data.forEach(trip => {
    console.log(`${trip.title}: ${trip.match_score}/100`);
    console.log(`Match reasons: ${trip.match_details.join(', ')}`);
  });
}
```

### Fetching Tags for Filters

```typescript
import { getTags } from '@/lib/api';

const tagsResponse = await getTags();
if (tagsResponse.success && tagsResponse.data) {
  // Separate Type and Theme tags
  const typeTags = tagsResponse.data.filter(t => t.category === 'Type');
  const themeTags = tagsResponse.data.filter(t => t.category === 'Theme');
  
  // Display Type as radio buttons (single choice)
  // Display Themes as checkboxes (up to 3 selections)
}
```

## Deployment

### Frontend (Vercel)

1. Push code to GitHub
2. Import repository in [Vercel](https://vercel.com)
3. Configure:
   - Framework: Next.js (auto-detected)
   - Build Command: `npm run build`
   - Output Directory: `.next`
4. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=your-backend-url
   ```

### Backend (Render/Railway)

#### Option A: Render

1. Create PostgreSQL database on [Render](https://render.com)
2. Create Web Service:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
3. Add environment variables:
   ```
   DATABASE_URL=<postgres-url>
   FLASK_ENV=production
   FRONTEND_URL=<your-vercel-url>
   ```
4. Run seed script via Shell: `python seed.py`

#### Option B: Railway

1. Create project on [Railway](https://railway.app)
2. Add PostgreSQL database
3. Deploy from GitHub
4. Configure root directory: `backend`
5. Start command: `python app.py`
6. Run seed script via terminal

### CORS Configuration

Update `backend/app.py` to allow your production frontend:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "https://your-app.vercel.app"
        ]
    }
})
```

## Testing

### Test Backend API

```bash
# Health check
curl http://localhost:5000/api/health

# Get countries
curl http://localhost:5000/api/countries

# Get tags
curl http://localhost:5000/api/tags

# Test recommendations
curl -X POST http://localhost:5000/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "selected_continents": ["Asia"],
    "budget": 10000,
    "difficulty": 2
  }'
```

### Run Test Suite

```bash
cd backend
python test_recommendations.py
```

## Common Issues

### "Module not found" in Python
```bash
cd backend
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### "Connection refused" to database
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Confirm database name and credentials

### CORS errors in browser
- Ensure backend is running on port 5000
- Check `FRONTEND_URL` in `backend/.env`
- Verify CORS origins in `app.py`

### Port already in use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

## Development Scripts

### Backend
```bash
cd backend
python app.py              # Start server
python seed.py             # Seed database
python test_recommendations.py  # Run tests
```

### Frontend
```bash
npm run dev      # Development server
npm run build    # Production build
npm run start    # Production server
npm run lint     # Run linter
```

## Contributing

This is a proprietary project. For questions or collaboration inquiries, please contact the development team.

## License

All Rights Reserved

---

**Built with care for intelligent travel planning**
