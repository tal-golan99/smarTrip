# Post-Restructure Deployment Checklist

## Problem
After the restructure, production deployments might still be using the old file structure, causing connection/auth issues.

## Critical Changes After Restructure

### Backend Changes
- ✅ **Old:** `app.py` in root of `backend/`
- ✅ **New:** `backend/app/main.py` (Flask app)
- ✅ **Old:** `from api_v2 import api_v2_bp`
- ✅ **New:** `from app.api.v2.routes import api_v2_bp`
- ✅ **Old:** `gunicorn app:app`
- ✅ **New:** `gunicorn app.main:app` (already updated in render.yaml ✅)

### Frontend Changes
- ✅ **Old:** Files in `src/lib/` (api.ts, tracking.ts)
- ✅ **New:** Files moved to `src/services/` and `src/hooks/`
- ✅ **Old:** `.env.local` in root
- ✅ **New:** `.env.local` must be in `frontend/` directory

## Deployment Checklist

### 1. Backend (Render) - Verify Configuration

**Check `render.yaml` is correct:**
```yaml
startCommand: cd backend && gunicorn app.main:app  # ✅ Correct
```

**Verify in Render Dashboard:**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Select your backend service
3. Check "Settings" → "Build & Deploy"
4. Verify Start Command: `cd backend && gunicorn app.main:app`
5. If different, update it to match above

**Environment Variables (should be set in Render Dashboard):**
- ✅ `FLASK_ENV=production`
- ✅ `DATABASE_URL` (Supabase connection string)
- ✅ `SECRET_KEY` (auto-generated or custom)
- ✅ `ALLOWED_ORIGINS` (your Vercel frontend URL)
- ✅ `SUPABASE_JWT_SECRET` (from Supabase Settings → API → JWT Settings)

**Redeploy Backend:**
```bash
# Option 1: Push to GitHub (if auto-deploy enabled)
git push origin main

# Option 2: Manual redeploy in Render Dashboard
# Dashboard → Your Service → Manual Deploy → Deploy latest commit
```

**Test Backend:**
```bash
curl https://your-backend.onrender.com/api/health
# Should return: {"status": "ok"}
```

### 2. Frontend (Vercel) - Verify Configuration

**Check Environment Variables in Vercel Dashboard:**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to "Settings" → "Environment Variables"
4. Verify these are set:
   - ✅ `NEXT_PUBLIC_API_URL` = `https://your-backend.onrender.com`
   - ✅ `NEXT_PUBLIC_SUPABASE_URL` = `https://your-project-id.supabase.co`
   - ✅ `NEXT_PUBLIC_SUPABASE_ANON_KEY` = `your-anon-key`

**Important:** 
- These MUST be set in Vercel Dashboard (not just in local `.env.local`)
- Vercel reads env vars from Dashboard, not from `.env.local` file
- After adding/updating env vars, you MUST redeploy

**Redeploy Frontend:**
```bash
# Option 1: Push to GitHub (if auto-deploy enabled)
git push origin main

# Option 2: Manual redeploy in Vercel Dashboard
# Dashboard → Your Project → Deployments → Latest → "..." → Redeploy
```

**Test Frontend:**
1. Visit: `https://your-app.vercel.app/auth`
2. Check if auth forms are visible (email/password, Google button)
3. If not visible, check browser console for errors

### 3. Common Issues After Restructure

#### Issue 1: Backend 500 Errors
**Symptom:** Backend returns 500 errors, logs show import errors

**Fix:**
- Verify `render.yaml` has correct `startCommand`
- Check Render logs for import errors
- Ensure all new imports use `from app.xxx import ...` format

#### Issue 2: Frontend Can't Connect to Backend
**Symptom:** Frontend shows connection errors

**Fix:**
- Verify `NEXT_PUBLIC_API_URL` in Vercel Dashboard points to correct backend URL
- Check CORS settings in backend (`ALLOWED_ORIGINS` in Render)
- Verify backend is running: `curl https://your-backend.onrender.com/api/health`

#### Issue 3: Auth Not Available in Production
**Symptom:** Auth page shows "אימות לא מוגדר" in production

**Fix:**
- Verify `NEXT_PUBLIC_SUPABASE_URL` is set in Vercel Dashboard
- Verify `NEXT_PUBLIC_SUPABASE_ANON_KEY` is set in Vercel Dashboard
- **Redeploy frontend** after adding env vars (Vercel only reads env vars at build time)

#### Issue 4: Module Not Found Errors
**Symptom:** Frontend build fails with "Module not found" errors

**Fix:**
- Verify all imports use new paths:
  - `from '../services/api.service'` (not `from '../lib/api'`)
  - `from '../services/tracking.service'` (not `from '../lib/tracking'`)
  - `from '../lib/supabaseClient'` (correct - this didn't move)

### 4. Verification Steps

**Backend Verification:**
```bash
# 1. Health check
curl https://your-backend.onrender.com/api/health

# 2. Test recommendations endpoint
curl -X POST https://your-backend.onrender.com/api/v2/recommendations \
  -H "Content-Type: application/json" \
  -d '{"preferences": {}, "filters": {}}'
```

**Frontend Verification:**
1. Visit production URL
2. Check browser console for errors
3. Try auth page - should show email/password form
4. Try search - should work

### 5. Rollback Plan (If Needed)

If production breaks after restructure:

**Backend Rollback:**
1. In Render Dashboard → Deployments
2. Find last working commit (before restructure)
3. Click "..." → "Rollback to this deployment"

**Frontend Rollback:**
1. In Vercel Dashboard → Deployments
2. Find last working commit
3. Click "..." → "Promote to Production"

## Summary

**Most Common Issue:** Environment variables not set in Vercel Dashboard

**Quick Fix:**
1. Set `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` in Vercel Dashboard
2. Redeploy frontend
3. Auth should work

**Backend:** Usually works if `render.yaml` is correct (which it is ✅)
