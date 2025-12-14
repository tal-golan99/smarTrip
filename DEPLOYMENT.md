# Deployment Guide

## Quick Deploy

### Backend (Render)

1. Push code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your repository
5. Render will automatically detect `render.yaml`
6. Set environment variables:
   - `FRONTEND_URL`: Your Vercel URL
   - `DATABASE_URL`: Auto-configured from PostgreSQL
   - `SECRET_KEY`: Auto-generated
7. Click "Apply"
8. After deployment, run seed script in Shell:
   ```bash
   cd backend && python seed.py
   ```

### Frontend (Vercel)

1. Push code to GitHub
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "Add New" → "Project"
4. Import your repository
5. Configure:
   - Framework Preset: Next.js
   - Root Directory: ./
   - Build Command: npm run build
   - Output Directory: .next
6. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your Render backend URL
7. Click "Deploy"

## Manual Deployment

### Backend on Render

1. Create Web Service
2. Configure:
   - Name: smarttrip-backend
   - Environment: Python 3
   - Region: Oregon (or closest to you)
   - Branch: main
   - Root Directory: backend
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

3. Add Environment Variables:
   ```
   FLASK_ENV=production
   SECRET_KEY=<generate-secure-key>
   DATABASE_URL=<postgres-connection-string>
   FRONTEND_URL=<your-vercel-url>
   PORT=5000
   HOST=0.0.0.0
   ```

4. Create PostgreSQL Database:
   - In Render, create new PostgreSQL database
   - Name: smarttrip-db
   - Copy Internal Database URL
   - Add to backend as DATABASE_URL

5. Seed Database:
   - Go to backend Shell tab
   - Run: `python seed.py`

### Frontend on Vercel

1. Import Project
2. Configure:
   - Framework: Next.js (auto-detected)
   - Root Directory: ./
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

3. Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   ```

4. Deploy

## Troubleshooting

### Backend Issues

**Issue: Backend returns 500 errors**
- Check DATABASE_URL is correctly set
- Verify database is seeded: `python seed.py`
- Check logs in Render dashboard

**Issue: CORS errors**
- Update FRONTEND_URL in backend environment
- Verify CORS origins in app.py match your frontend URL

**Issue: Database connection fails**
- Ensure DATABASE_URL includes all parameters
- Check database is running in Render
- Verify PostgreSQL version compatibility (12+)

### Frontend Issues

**Issue: API calls fail**
- Verify NEXT_PUBLIC_API_URL is set correctly
- Check backend is running and accessible
- Test backend health: `https://your-backend.onrender.com/api/health`

**Issue: Build fails**
- Run `npm install` locally to check for dependency issues
- Check Node.js version matches (18+)
- Review build logs in Vercel

**Issue: Environment variables not working**
- Redeploy after adding/changing environment variables
- Ensure NEXT_PUBLIC_ prefix for client-side variables
- Check variables in Vercel project settings

## Environment Variables Reference

### Backend (.env for local, Render env vars for production)
```
FLASK_APP=app.py
FLASK_ENV=development|production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
PORT=5000
HOST=0.0.0.0
FRONTEND_URL=http://localhost:3000|https://your-app.vercel.app
```

### Frontend (.env.local for local, Vercel env vars for production)
```
NEXT_PUBLIC_API_URL=http://localhost:5000|https://your-backend.onrender.com
```

## Testing Production Deployment

### Backend
```bash
curl https://your-backend.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": {
    "trips": 587,
    "countries": 105,
    "guides": 12
  }
}
```

### Frontend
Visit: `https://your-app.vercel.app`

Should load home page and allow navigation to search.

## Post-Deployment Checklist

- [ ] Backend health check responds
- [ ] Frontend loads without errors
- [ ] Search form works
- [ ] Recommendations display correctly
- [ ] Trip details page loads
- [ ] Database has 587 trips
- [ ] Hebrew text displays correctly (RTL)
- [ ] CORS allows frontend to access backend

## Monitoring

### Backend
- Monitor logs in Render dashboard
- Set up health check alerts
- Check database connection pool

### Frontend
- Monitor Vercel Analytics
- Check build logs for warnings
- Review Runtime Logs for errors

## Scaling

### Backend
- Render automatically scales based on traffic
- Consider upgrading to paid plan for:
  - More memory (512MB → 2GB+)
  - Better CPU
  - No sleep on free tier

### Frontend
- Vercel handles scaling automatically
- No additional configuration needed

## Backup

### Database
1. In Render dashboard, go to PostgreSQL database
2. Download latest backup
3. Schedule regular backups (available on paid plans)

### Code
- Ensure GitHub repository is up to date
- Tag releases: `git tag -a v1.0.0 -m "Release 1.0.0"`
- Push tags: `git push origin --tags`

