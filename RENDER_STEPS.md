# What to Do on Render - Simple Guide

## Step 1: Check if Your Backend Deployed Automatically

1. Go to https://dashboard.render.com/
2. You should see your backend service (probably named something like "smarttrip-backend" or "trip-recommendations")
3. Look at the status:
   - **Green "Live"** = Good, it's running
   - **Yellow "Deploying"** = Wait a few minutes
   - **Red "Deploy failed"** = Need to fix (see troubleshooting below)

## Step 2: Check if Database Has Data

Open a new browser tab and visit:
```
https://YOUR-BACKEND-URL.onrender.com/api/health
```

Replace `YOUR-BACKEND-URL` with your actual Render URL (find it in Render dashboard).

**What you should see:**
```json
{
  "status": "healthy",
  "database": {
    "trips": 587,
    "countries": 105,
    "guides": 12,
    "tags": 12,
    "trip_types": 10
  }
}
```

### If you see trips: 0, countries: 0, etc. OR errors about missing columns

Your database needs to be migrated and seeded.

**Run this command in your terminal (PowerShell):**
```powershell
curl -X POST https://YOUR-BACKEND-URL.onrender.com/api/migrate
```

This will:
1. Drop old tables (if they exist)
2. Create new tables with correct schema
3. Seed with 587 trips and all data

Wait 2-3 minutes (seeding takes time), then check `/api/health` again. Numbers should now show 587 trips, etc.

**Note:** This is safe to run - it will recreate all data fresh.

## Step 3: Update Environment Variable (if needed)

1. In Render dashboard, click on your backend service
2. Click "Environment" in the left sidebar
3. Look for `FRONTEND_URL`
4. Make sure it says: `https://YOUR-VERCEL-URL.vercel.app`
5. If it's wrong or missing:
   - Click "Add Environment Variable"
   - Key: `FRONTEND_URL`
   - Value: Your Vercel URL
   - Click "Save Changes" (this will trigger a redeploy)

## That's It!

You don't need to:
- Create a new service
- Upload files manually
- Use any shell/terminal in Render
- Do any complex configuration

Render automatically deploys when you push to GitHub.

## Troubleshooting

### "Deploy Failed" Error

1. Click on your service
2. Click "Logs" in the left sidebar
3. Look for red error messages
4. Common issues:
   - Missing environment variable (add it in Environment tab)
   - Database connection error (check DATABASE_URL is set)
   - Python version mismatch (should be 3.10+)

### Backend URL keeps sleeping (free tier)

This is normal for Render's free tier. The service:
- Spins down after 15 minutes of no activity
- Takes 30-60 seconds to wake up on first request
- This is expected behavior

### How to find your Backend URL

1. Go to Render dashboard
2. Click on your backend service
3. Look at the top - you'll see something like:
   ```
   https://smarttrip-backend-abc123.onrender.com
   ```
   This is your backend URL.

## Quick Check Checklist

- [ ] Backend shows "Live" in Render dashboard
- [ ] `/api/health` returns trips: 587
- [ ] `FRONTEND_URL` environment variable is set correctly
- [ ] Test a recommendation request works

That's all you need to do!

