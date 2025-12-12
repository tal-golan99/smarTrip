# Trip Recommendations System

A sophisticated trip recommendation system with a Next.js frontend and Flask backend, featuring personalized trip matching based on user preferences.

## Features

- Advanced filtering by continent, country, trip type, themes, dates, budget, and difficulty
- Context-aware trip descriptions in both Hebrew and English
- Premium image-based result cards with hover effects
- Real-time availability status tracking
- Personalized recommendations with scoring algorithm
- RTL (Right-to-Left) support for Hebrew interface

## Tech Stack

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Lucide Icons

### Backend
- Flask (Python)
- SQLAlchemy ORM
- PostgreSQL
- Faker (for seed data generation)

## Project Structure

```
trip-recommendations/
├── src/
│   ├── app/
│   │   ├── search/          # Search and filter page
│   │   └── results/         # Results display page
│   └── components/          # Reusable React components
├── backend/
│   ├── app.py              # Flask API routes
│   ├── models.py           # SQLAlchemy models
│   └── seed.py             # Database seeding script
└── public/
    └── images/             # Static images (logos, continents, trip statuses)
```

## Database Schema

The system uses 5 main tables:
- **Countries**: Geographic locations with continent mapping
- **Guides**: Tour guides with Hebrew and English names
- **Tags**: Trip categorization (Type, Theme, Difficulty)
- **Trips**: Core trip data with pricing, dates, and descriptions
- **TripTags**: Many-to-many relationship between trips and tags

## Setup Instructions

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- PostgreSQL

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install flask flask-cors sqlalchemy psycopg2-binary faker python-dotenv
```

4. Create a `.env` file in the backend directory:
```
DATABASE_URL=postgresql://username:password@localhost:5432/trip_recommendations
```

5. Seed the database:
```bash
python seed.py
```

6. Start the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the project root directory

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Usage

1. Navigate to `http://localhost:3000/search`
2. Select your preferences:
   - Continents or specific countries
   - Trip types (Geographic Depth, African Safari, Multi-Country, etc.)
   - Themes (Culture, Nature, Desert, etc.)
   - Date range
   - Budget range
   - Difficulty level
3. Click "Find My Trip" to see personalized recommendations
4. View detailed results with match scores, pricing, and guide information

## API Endpoints

### POST `/api/recommendations`
Returns personalized trip recommendations based on user preferences.

**Request Body:**
```json
{
  "continents": ["Asia", "Europe"],
  "countries": [1, 5, 10],
  "types": [1, 2],
  "themes": [3, 4],
  "startDate": "2025-01-01",
  "endDate": "2025-12-31",
  "minBudget": 3000,
  "maxBudget": 10000,
  "minDuration": 7,
  "maxDuration": 21,
  "difficulty": "Moderate"
}
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "title": "Trip Title",
      "titleHe": "כותרת הטיול",
      "description": "Trip description",
      "descriptionHe": "תיאור הטיול",
      "price": 5000,
      "duration": 14,
      "startDate": "2025-03-15",
      "endDate": "2025-03-29",
      "difficulty": "Moderate",
      "availabilityStatus": "Open",
      "matchScore": 95.5,
      "country": {...},
      "guide": {...},
      "tags": [...]
    }
  ],
  "total_candidates": 45,
  "count": 10
}
```

## Deployment

### Vercel (Frontend)
1. Push code to GitHub
2. Import repository in Vercel
3. Configure build settings:
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`

### Backend Hosting
Options include:
- Heroku
- Railway
- Render
- AWS EC2

Ensure environment variables are properly configured in your hosting platform.

## License

Proprietary - All Rights Reserved

## Contact

For questions or support, please contact the development team.
