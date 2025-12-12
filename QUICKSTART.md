# 🚀 SmartTrip Quick Start Guide

Get the SmartTrip system running in 5 minutes!

## Step 1: Install Prerequisites

Make sure you have:
- ✅ **Node.js 18+** - [Download](https://nodejs.org/)
- ✅ **Python 3.10+** - [Download](https://www.python.org/)
- ✅ **PostgreSQL 12+** - [Download](https://www.postgresql.org/)

## Step 2: Create Database

```sql
-- Open PostgreSQL (pgAdmin, psql, or any client)
CREATE DATABASE smarttrip;
```

## Step 3: Set Up Backend

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy and edit this)
# Create backend/.env with:
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=my-secret-key
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5433/smarttrip
PORT=5000
HOST=0.0.0.0
FRONTEND_URL=http://localhost:3000

# Seed the database (creates tables + data)
python seed.py

# Start Flask server
python app.py
```

✅ Backend running at: http://localhost:5000

## Step 4: Set Up Frontend

```bash
# Open a new terminal, go to project root
cd ..

# Install dependencies
npm install

# Create .env.local file with:
NEXT_PUBLIC_API_URL=http://localhost:5000

# Start Next.js
npm run dev
```

✅ Frontend running at: http://localhost:3000

## Step 5: Test It!

Open your browser and visit:

1. **Backend API Health Check:**  
   http://localhost:5000/api/health

2. **View Countries:**  
   http://localhost:5000/api/countries

3. **View Trip Tags:**  
   http://localhost:5000/api/tags

4. **View Guides:**  
   http://localhost:5000/api/guides

5. **Frontend:**  
   http://localhost:3000

## 🎉 You're Ready!

The database now has:
- ✅ 115+ countries from Ayala Geographic
- ✅ 23 trip type tags
- ✅ 5 sample guides
- ✅ Full API endpoints ready to use

## Next Steps

1. **Add trips** - Use the API or directly in the database
2. **Build the frontend UI** - Check `src/app/example-api-usage.tsx` for examples
3. **Implement recommendation algorithm** - In `backend/app.py` at `/api/recommendations`
4. **Design the interface** - Match Ayala Geographic's branding

## Need Help?

- 📖 See `README.md` for full documentation
- 🗄️ See `DATABASE_SETUP.md` for database details
- 🐍 See `backend/README.md` for API documentation
- 💻 See `src/lib/api.ts` for frontend API client usage

## Common Issues

### "Module not found" errors in Python
```bash
# Make sure virtual environment is activated
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### "Connection refused" to database
- Check PostgreSQL is running
- Verify DATABASE_URL in `backend/.env`
- Check username/password is correct

### CORS errors in browser
- Make sure Flask backend is running on port 5000
- Check `FRONTEND_URL` in `backend/.env` is set to `http://localhost:3000`

### "Port already in use"
```bash
# Windows - kill process on port 5000:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

---

**Happy coding! 🎉**


