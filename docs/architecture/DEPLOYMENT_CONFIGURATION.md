# Deployment Configuration Guide

## Vercel (Frontend) Configuration

### Option 1: Using vercel.json (Current Setup)
The `vercel.json` file in the root tells Vercel to build from the `frontend/` directory.

### Option 2: Vercel Dashboard Settings (Recommended)
1. Go to your Vercel project settings
2. Navigate to **Settings** → **General**
3. Under **Root Directory**, set it to `frontend`
4. Save changes

**Note:** If you use the dashboard setting, you can remove `vercel.json` or keep it as a backup.

### Build Settings
- **Framework Preset:** Next.js
- **Root Directory:** `frontend`
- **Build Command:** `npm run build` (runs from frontend directory)
- **Output Directory:** `.next` (relative to frontend directory)
- **Install Command:** `npm install` (runs from frontend directory)

---

## Render (Backend) Configuration

### Current Setup
The `render.yaml` file configures the backend service:

```yaml
services:
  - type: web
    name: smarttrip-backend
    env: python
    region: oregon
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app.main:app --bind 0.0.0.0:$PORT
```

### Important Settings
- **Root Directory:** `backend` (set in render.yaml)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app.main:app --bind 0.0.0.0:$PORT`
- **Python Version:** 3.10+ (set in `backend/runtime.txt`)

### Environment Variables (Set in Render Dashboard)
- `FLASK_ENV`: `production`
- `SECRET_KEY`: (auto-generated or set manually)
- `DATABASE_URL`: Your Supabase connection string (Session pooler, port 5432)
- `ALLOWED_ORIGINS`: Your Vercel frontend URL (e.g., `https://your-app.vercel.app`)
- `SUPABASE_JWT_SECRET`: From Supabase Settings → API → JWT Settings

### Troubleshooting Render Deployment

**Error: `Failed to find attribute 'app' in 'app'`**
- **Cause:** Render is not using the correct start command
- **Fix:** Ensure `render.yaml` has `rootDir: backend` and `startCommand: gunicorn app.main:app`
- **Alternative:** If Render is using Procfile instead, ensure `backend/Procfile` contains: `web: gunicorn app.main:app`

**Error: `ModuleNotFoundError: No module named 'app'`**
- **Cause:** Python can't find the app package
- **Fix:** Ensure `rootDir: backend` is set in render.yaml
- **Check:** The working directory should be `backend/` when gunicorn runs

---

## Deployment Checklist

### Before Deploying

#### Frontend (Vercel)
- [ ] Set root directory to `frontend` in Vercel dashboard (or use vercel.json)
- [ ] Ensure `frontend/.env.local` has production environment variables:
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - `NEXT_PUBLIC_API_URL` (your Render backend URL)
- [ ] Verify `frontend/package.json` has correct build script

#### Backend (Render)
- [ ] Verify `render.yaml` has correct `rootDir: backend`
- [ ] Set all required environment variables in Render dashboard
- [ ] Ensure `DATABASE_URL` uses Session pooler (port 5432) with `?sslmode=require`
- [ ] Set `ALLOWED_ORIGINS` to your Vercel frontend URL

### After Deploying

#### Verify Frontend
- [ ] Frontend loads without errors
- [ ] Authentication works (Supabase)
- [ ] API calls to backend succeed

#### Verify Backend
- [ ] Health check: `https://your-backend.onrender.com/api/health`
- [ ] CORS allows requests from frontend
- [ ] Database connection works
- [ ] API endpoints respond correctly

---

## Common Issues

### Vercel: "Couldn't find any `pages` or `app` directory"
**Solution:** Set root directory to `frontend` in Vercel dashboard settings.

### Render: "Failed to find attribute 'app' in 'app'"
**Solution:** Ensure `render.yaml` has `rootDir: backend` and correct `startCommand`.

### CORS Errors
**Solution:** Set `ALLOWED_ORIGINS` in Render to include your Vercel frontend URL.

### Database Connection Errors
**Solution:** Use Session pooler connection string (port 5432) with `?sslmode=require`.
