# Deployment Guide - Update Existing Deployments

This guide is for updating your EXISTING Render and Vercel deployments with the latest changes.

## Quick Update Steps

### 1. Update Backend on Render

Your backend will automatically redeploy when you push to GitHub (if auto-deploy is enabled).

**Manual Redeploy:**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Select your backend service
3. Click "Manual Deploy" → "Deploy latest commit"
4. Wait for deployment to complete (2-3 minutes)

**Check deployment:**
```bash
curl https://your-backend.onrender.com/api/health
```

### 2. Update Frontend on Vercel

Your frontend will automatically redeploy when you push to GitHub.

**Manual Redeploy:**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to "Deployments" tab
4. Click "..." on latest commit → "Redeploy"

**Check deployment:**
Visit: `https://your-app.vercel.app`

## Database Seeding (For Free Tier Users)

Since Render's free tier doesn't have Shell access, you need to trigger seeding through the API.

### Option 1: Add a Seed Endpoint (Recommended)

I've added a `/api/seed` endpoint that you can call to seed the database:

```bash
curl -X POST https://your-backend.onrender.com/api/seed
```

This will seed the database if it's empty or needs updating.

### Option 2: Manual Database Update

If you need to update the database manually:

1. Use a PostgreSQL client (e.g., DBeaver, pgAdmin)
2. Get connection string from Render:
   - Go to your database in Render
   - Copy "External Database URL"
3. Connect and run SQL scripts manually

### Check if Database is Seeded

```bash
curl https://your-backend.onrender.com/api/health
```

Should show:
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

If counts are 0, the database needs seeding.

## Environment Variables

### Backend (Render)

Check that these are set in Render:
- `FLASK_ENV`: production
- `DATABASE_URL`: (auto-set by Render PostgreSQL)
- `SECRET_KEY`: (should already be set)
- `FRONTEND_URL`: Update to match your Vercel URL if it changed
- `PORT`: 5000
- `HOST`: 0.0.0.0

**To update:**
1. Go to your service in Render
2. Click "Environment" in left sidebar
3. Update variables
4. Click "Save Changes" (triggers redeploy)

### Frontend (Vercel)

Check that this is set in Vercel:
- `NEXT_PUBLIC_API_URL`: Your Render backend URL

**To update:**
1. Go to your project in Vercel
2. Click "Settings" → "Environment Variables"
3. Update `NEXT_PUBLIC_API_URL`
4. Redeploy for changes to take effect

## Troubleshooting

### Backend Issues

**Issue: 500 errors after deployment**
- Check Render logs: Service → Logs tab
- Verify DATABASE_URL is correct
- Try manual seed: `curl -X POST https://your-backend.onrender.com/api/seed`

**Issue: CORS errors**
- Update FRONTEND_URL in Render environment variables
- Make sure it matches your Vercel URL exactly
- Redeploy after changing

**Issue: Database connection fails**
- Check if database is running in Render dashboard
- Verify DATABASE_URL is set correctly
- Check if database is on same region as backend

### Frontend Issues

**Issue: API calls failing**
- Check NEXT_PUBLIC_API_URL in Vercel settings
- Test backend health endpoint directly
- Make sure backend is deployed and running

**Issue: 404 errors on routes**
- Redeploy frontend after adding new files
- Check build logs in Vercel for errors
- Verify all required files are committed to Git

**Issue: Changes not appearing**
- Clear Vercel cache: Settings → Clear Cache
- Force redeploy: Deployments → Redeploy
- Check correct branch is deployed

## Auto-Deploy Setup

### Render
1. Go to your service
2. Settings → "Build & Deploy"
3. Enable "Auto-Deploy: Yes"
4. Select branch: main

### Vercel
Auto-deploy is enabled by default for connected repos.

## Monitoring

### Check Backend Health
```bash
curl https://your-backend.onrender.com/api/health
```

### Check Frontend
Visit: https://your-app.vercel.app

### View Logs

**Render:**
- Dashboard → Your Service → Logs

**Vercel:**
- Dashboard → Your Project → Deployments → Click deployment → Runtime Logs

## Performance Notes

### Render Free Tier
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds (cold start)
- No persistent shell access
- 512 MB RAM limit

### Solutions for Cold Starts
1. Use Render's paid plan (no sleep)
2. Set up a ping service (e.g., UptimeRobot) to keep it awake
3. Accept the cold start delay (acceptable for development/testing)

## Database Backup

### Render PostgreSQL
1. Go to database in Render dashboard
2. Click "Backups" tab
3. Download latest backup
4. Free tier: Manual backups only
5. Paid tier: Automatic daily backups

## Rollback

### Backend (Render)
1. Go to Deployments tab
2. Find previous successful deployment
3. Click "..." → "Redeploy"

### Frontend (Vercel)
1. Go to Deployments tab
2. Find previous successful deployment
3. Click "..." → "Promote to Production"

## Testing After Deployment

Run these checks after each deployment:

**Backend:**
```bash
# Health check
curl https://your-backend.onrender.com/api/health

# Test recommendations
curl -X POST https://your-backend.onrender.com/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{"budget": 10000}'
```

**Frontend:**
1. Visit home page
2. Go to /search
3. Submit a search
4. Verify results display
5. Click on a trip
6. Verify trip details load

## Support

If you encounter issues:
1. Check logs in Render/Vercel dashboards
2. Verify environment variables
3. Test backend health endpoint
4. Check CORS settings
5. Review deployment logs for errors
