# Production Environment Variables Guide

## Problem
After adding Supabase authentication, the frontend-backend connection broke in production (but works locally).

## Root Cause
The `ALLOWED_ORIGINS` environment variable in the backend needs to include your production frontend URL (Vercel).

## Required Environment Variables

### Frontend (Vercel)
Set these in Vercel Dashboard → Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Backend (Render)
Set these in Render Dashboard → Environment:

```
DATABASE_URL=postgresql://... (your Supabase DB connection string)
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
SUPABASE_JWT_SECRET=your-jwt-secret (from Supabase Dashboard → Settings → API)
FLASK_ENV=production
SECRET_KEY=your-secret-key
```

## Critical Fix: ALLOWED_ORIGINS

The backend CORS configuration uses `ALLOWED_ORIGINS` to allow requests from your frontend.

**Before adding auth:**
- `ALLOWED_ORIGINS` was probably set to `http://localhost:3000` only
- This worked locally but blocked production requests

**After adding auth:**
- You need to add your Vercel production URL to `ALLOWED_ORIGINS`
- Format: `https://your-app.vercel.app,http://localhost:3000` (comma-separated)

## How to Fix

1. **In Render Dashboard:**
   - Go to your backend service
   - Click "Environment"
   - Find `ALLOWED_ORIGINS`
   - Update it to: `https://your-frontend.vercel.app,http://localhost:3000`
   - Save and redeploy

2. **Verify in Vercel:**
   - Check that `NEXT_PUBLIC_API_URL` points to your Render backend URL
   - Should be: `https://your-backend.onrender.com` (not `http://localhost:5000`)

3. **Test:**
   - Open production frontend
   - Open browser console (F12)
   - Check for CORS errors
   - Check Network tab for failed requests

## Common Issues

### Issue 1: CORS Error
**Symptom:** `Access-Control-Allow-Origin` error in browser console

**Fix:** 
- Ensure `ALLOWED_ORIGINS` in Render includes your exact Vercel URL
- Check for trailing slashes (should be: `https://app.vercel.app` not `https://app.vercel.app/`)

### Issue 2: API URL Wrong
**Symptom:** Requests going to `http://localhost:5000` in production

**Fix:**
- Verify `NEXT_PUBLIC_API_URL` in Vercel is set to your Render backend URL
- Rebuild and redeploy frontend after changing env vars

### Issue 3: Supabase Not Working
**Symptom:** Auth features not working in production

**Fix:**
- Verify `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` are set in Vercel
- Check Supabase dashboard → Settings → API → Redirect URLs includes your Vercel URL

## Verification Checklist

- [ ] `ALLOWED_ORIGINS` in Render includes your Vercel URL
- [ ] `NEXT_PUBLIC_API_URL` in Vercel points to Render backend
- [ ] `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` set in Vercel
- [ ] `SUPABASE_JWT_SECRET` set in Render
- [ ] Backend redeployed after env var changes
- [ ] Frontend redeployed after env var changes
- [ ] No CORS errors in browser console
- [ ] API requests succeed in Network tab


