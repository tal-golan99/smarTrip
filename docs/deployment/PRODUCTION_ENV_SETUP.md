# Production Environment Variables Setup

## Problem
After adding Supabase authentication, the frontend-backend connection broke in production (but works locally).

## Root Cause
The issue is likely related to:
1. **CORS configuration** - Backend needs to allow your Vercel frontend URL
2. **Missing environment variables** - New Supabase variables may not be set in production
3. **API URL mismatch** - Frontend may be using wrong backend URL in production

## Required Environment Variables

### Frontend (Vercel)
Set these in Vercel Dashboard → Your Project → Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

**Important:**
- `NEXT_PUBLIC_API_URL` must point to your Render backend URL (not localhost!)
- All `NEXT_PUBLIC_*` variables are exposed to the browser
- Redeploy frontend after adding/changing variables

### Backend (Render)
Set these in Render Dashboard → Your Service → Environment:

```
DATABASE_URL=postgresql://... (your Supabase connection string)
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-frontend.vercel.app
SUPABASE_JWT_SECRET=your-jwt-secret-from-supabase
FLASK_ENV=production
SECRET_KEY=your-secret-key
```

**Critical for CORS:**
- `ALLOWED_ORIGINS` must include your **exact Vercel URL** (with `https://`)
- If you have multiple domains, separate with commas: `https://app1.vercel.app,https://app2.vercel.app`
- **No trailing slashes** in URLs
- Case-sensitive - must match exactly

## How to Find Your URLs

### Frontend URL (Vercel)
1. Go to Vercel Dashboard
2. Select your project
3. Go to "Deployments"
4. Copy the production URL (e.g., `https://your-app.vercel.app`)

### Backend URL (Render)
1. Go to Render Dashboard
2. Select your web service
3. Copy the URL (e.g., `https://smarttrip-backend.onrender.com`)

### Supabase Credentials
1. Go to Supabase Dashboard
2. Select your project
3. Go to Settings → API
4. Copy:
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **anon/public key** → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **JWT Secret** → `SUPABASE_JWT_SECRET` (in Settings → API → JWT Settings)

## Verification Steps

### 1. Check Frontend Environment Variables
In Vercel:
- Settings → Environment Variables
- Verify all `NEXT_PUBLIC_*` variables are set
- **Redeploy** after adding/changing variables

### 2. Check Backend Environment Variables
In Render:
- Environment tab
- Verify `ALLOWED_ORIGINS` includes your Vercel URL
- Verify `SUPABASE_JWT_SECRET` is set (if using auth)
- **Restart service** after changing variables

### 3. Test CORS
Open browser console on your production site and check:
```javascript
fetch('https://your-backend.onrender.com/api/health', {
  method: 'GET',
  mode: 'cors'
})
.then(r => r.json())
.then(console.log)
.catch(console.error)
```

If you see CORS errors, the `ALLOWED_ORIGINS` in Render is wrong.

### 4. Check API URL
In browser console on production:
```javascript
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL)
```

Should show your Render backend URL, not `http://localhost:5000`.

## Common Issues

### Issue 1: CORS Error
**Symptom:** `Access-Control-Allow-Origin` error in browser console

**Fix:**
1. Check `ALLOWED_ORIGINS` in Render includes your exact Vercel URL
2. Make sure URL has `https://` (not `http://`)
3. No trailing slash
4. Restart Render service after changing

### Issue 2: API URL is localhost
**Symptom:** Frontend tries to connect to `http://localhost:5000` in production

**Fix:**
1. Set `NEXT_PUBLIC_API_URL` in Vercel to your Render backend URL
2. **Redeploy** frontend (variables are baked into build)

### Issue 3: Supabase Auth Not Working
**Symptom:** Auth page shows "אימות לא מוגדר"

**Fix:**
1. Set `NEXT_PUBLIC_SUPABASE_URL` in Vercel
2. Set `NEXT_PUBLIC_SUPABASE_ANON_KEY` in Vercel
3. **Redeploy** frontend

### Issue 4: Backend Can't Verify JWT
**Symptom:** Backend logs show JWT verification errors

**Fix:**
1. Set `SUPABASE_JWT_SECRET` in Render
2. Get the secret from Supabase Dashboard → Settings → API → JWT Settings
3. Restart Render service

## Quick Checklist

- [ ] `NEXT_PUBLIC_API_URL` in Vercel = Render backend URL
- [ ] `ALLOWED_ORIGINS` in Render = Vercel frontend URL (with https://)
- [ ] `NEXT_PUBLIC_SUPABASE_URL` in Vercel = Supabase project URL
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY` in Vercel = Supabase anon key
- [ ] `SUPABASE_JWT_SECRET` in Render = Supabase JWT secret
- [ ] Frontend redeployed after env var changes
- [ ] Backend restarted after env var changes

## Testing After Setup

1. **Open production frontend** in browser
2. **Open browser console** (F12)
3. **Check for errors:**
   - CORS errors → Check `ALLOWED_ORIGINS`
   - Network errors → Check `NEXT_PUBLIC_API_URL`
   - Auth errors → Check Supabase variables

4. **Test API connection:**
   - Navigate to search page
   - Check console for `[SearchPage] API_URL: ...`
   - Should show Render URL, not localhost

5. **Test backend directly:**
   - Open `https://your-backend.onrender.com/api/health` in browser
   - Should return JSON, not error
