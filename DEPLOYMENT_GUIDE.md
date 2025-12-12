# Deployment Guide for SmartTrip

## Fixed Issues

### TypeScript Build Error
Fixed missing `category` property in Tag interface (`src/lib/api.ts`). This was causing the Vercel build to fail.

## GitHub Push Instructions

If Git is already installed, run these commands from your project directory:

```bash
# Check if git is initialized
git status

# If not initialized, run:
git init

# Add all files
git add .

# Commit the fix
git commit -m "Fix TypeScript error: Add category property to Tag interface"

# If you haven't connected to your repo yet:
git remote add origin https://github.com/tal-golan99/smarTrip.git
git branch -M main

# Push to GitHub
git push -u origin main
```

If Git is NOT installed:
1. Download Git from: https://git-scm.com/download/win
2. Install with default settings
3. Restart your terminal
4. Run the commands above

## Vercel Deployment Guide

### 1. Frontend (Next.js) Deployment

Your GitHub repo is: https://github.com/tal-golan99/smarTrip/

1. **Go to Vercel**: https://vercel.com
2. **Sign in** with your GitHub account
3. **Import Project**:
   - Click "Add New..." → "Project"
   - Find and select `tal-golan99/smarTrip`
4. **Configure Project**:
   - Framework Preset: Next.js (auto-detected)
   - Root Directory: `./` (leave default)
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`
5. **Environment Variables** (Add these):
   ```
   NEXT_PUBLIC_API_URL=YOUR_BACKEND_URL_HERE
   ```
   Note: Leave this empty for now, update after backend deployment
6. **Click "Deploy"**

### 2. Backend (Flask) Deployment

#### Option A: Render (Recommended - Free Tier Available)

1. **Go to Render**: https://render.com
2. **Sign up/Sign in** with GitHub
3. **Create PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - Name: `smarttrip-db`
   - Region: Choose closest to your users
   - Plan: Free or Starter
   - Click "Create Database"
   - Copy the "Internal Database URL" (you'll need this)

4. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `tal-golan99/smarTrip`
   - Configure:
     - Name: `smarttrip-api`
     - Region: Same as database
     - Root Directory: `backend`
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python app.py`
   
5. **Add Environment Variables**:
   ```
   DATABASE_URL=<paste-internal-database-url-from-step-3>
   FLASK_ENV=production
   ```

6. **Click "Create Web Service"**

7. **Initialize Database**:
   - Once deployed, go to your service → "Shell" tab
   - Run: `python seed.py`

8. **Copy your service URL** (e.g., `https://smarttrip-api.onrender.com`)

#### Option B: Railway

1. **Go to Railway**: https://railway.app
2. **Sign in with GitHub**
3. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `tal-golan99/smarTrip`
4. **Add PostgreSQL**:
   - Click "+ New" → "Database" → "PostgreSQL"
   - Railway auto-connects it
5. **Configure Service**:
   - Select your backend service
   - Settings → Root Directory: `backend`
   - Start Command: `python app.py`
6. **Seed Database**:
   - In the service view, click "..." → "Run Command"
   - Enter: `python seed.py`
7. **Get your service URL** from the "Settings" tab

### 3. Connect Frontend to Backend

1. **Update Vercel Environment Variables**:
   - Go to your Vercel project
   - Settings → Environment Variables
   - Add/Update:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend-url.com
     ```
   - Replace `https://your-backend-url.com` with your Render/Railway URL

2. **Redeploy Frontend**:
   - Vercel will automatically redeploy
   - Or go to "Deployments" → "Redeploy"

### 4. Update Backend CORS Settings

Make sure your backend (`backend/app.py`) allows requests from your Vercel domain:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "https://your-vercel-domain.vercel.app",  # Add your Vercel URL
            "https://smartrip.vercel.app"  # If you have a custom domain
        ]
    }
})
```

Commit and push this change to trigger a new backend deployment.

### 5. Test Your Deployment

1. Visit your Vercel URL (e.g., `https://smartrip-xyz.vercel.app`)
2. Navigate to `/search`
3. Try filtering and getting recommendations
4. Check browser console for any errors
5. Check backend logs in Render/Railway dashboard

## Troubleshooting

### Build Fails on Vercel
- Check the build logs for TypeScript errors
- Make sure all TypeScript types are properly defined
- Ensure `package.json` has all required dependencies

### Backend Not Responding
- Check Render/Railway logs for errors
- Verify DATABASE_URL is correct
- Make sure you ran `seed.py` to populate the database
- Check that the Flask app is listening on `0.0.0.0` not `127.0.0.1`

### CORS Errors
- Update backend CORS settings to include your Vercel domain
- Clear browser cache and try again

### Database Connection Issues
- Verify DATABASE_URL in environment variables
- Check that PostgreSQL service is running
- Ensure psycopg2-binary is in requirements.txt

## Custom Domain Setup (Optional)

### For Frontend (Vercel)
1. Go to Vercel project → Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

### For Backend (Render)
1. Go to service → Settings → Custom Domain
2. Add your domain
3. Update DNS records as instructed

## Environment Variables Reference

### Frontend (.env.local for development)
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### Frontend (Vercel Production)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Backend (.env for development)
```
DATABASE_URL=postgresql://username:password@localhost:5432/trip_recommendations
FLASK_ENV=development
```

### Backend (Render/Railway Production)
```
DATABASE_URL=<provided-by-hosting-service>
FLASK_ENV=production
```

## Monitoring and Maintenance

- Check Vercel Analytics for frontend performance
- Monitor Render/Railway logs for backend errors
- Set up uptime monitoring (e.g., UptimeRobot)
- Regularly update dependencies for security patches

## Need Help?

- Vercel Docs: https://vercel.com/docs
- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app

