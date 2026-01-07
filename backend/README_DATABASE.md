# Database Connection Setup

## Issue: Connection Refused Error

If you see `connection to server at "aws-0-us-west-2.pooler.supabase.com" (35.160.209.8), port 6543 failed: Connection refused`, this means the backend cannot connect to your Supabase database.

## Solutions

### Option 1: Use Direct Connection (Recommended for Local Dev)

The pooler (port 6543) might be blocked or unavailable. Use the direct connection (port 5432) instead:

1. Go to Supabase Dashboard → Settings → Database
2. Find "Connection string" → "Direct connection" (not "Transaction pooler")
3. Copy the connection string
4. Update your `backend/.env` file:
   ```
   DATABASE_URL=postgresql://postgres.xxxxx:password@aws-0-us-west-2.compute.amazonaws.com:5432/postgres?sslmode=require
   ```

### Option 2: Use SQLite for Local Development

For local development, you can use SQLite instead of Supabase:

1. Create or update `backend/.env`:
   ```
   DATABASE_URL=sqlite:///./smarttrip.db
   ```
2. The app will create a local SQLite database file
3. Use Supabase only in production (Render)

### Option 3: Check Supabase Database Status

1. Go to Supabase Dashboard
2. Check if your database is paused (free tier databases pause after inactivity)
3. If paused, click "Resume" to wake it up
4. Wait a few minutes for it to fully start

### Option 4: Verify Connection String

Make sure your `DATABASE_URL` in `backend/.env` is correct:

- Should start with `postgresql://` (not `postgres://`)
- Should include `?sslmode=require` for Supabase
- Should have correct password (not expired)
- Should use correct port (5432 for direct, 6543 for pooler)

## Testing Connection

After updating `.env`, test the connection:

```bash
cd backend
python -c "from database import engine; engine.connect(); print('Connection successful!')"
```

## App Behavior

The app will now start even if the database connection fails initially. It will:
- Show a warning message
- Continue running
- Try to connect when you make API calls
- Fail gracefully if database is unavailable

This allows you to:
- Develop frontend without backend database
- Start the app while database is starting up
- Handle temporary network issues



