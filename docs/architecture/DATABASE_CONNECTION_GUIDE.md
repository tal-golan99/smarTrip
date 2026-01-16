# Database Connection Guide

## Port 6543 vs 5432 - Which to Use?

### Port 6543 (Connection Pooler)
- **What it is:** Supabase's connection pooler service
- **When to use:** Production environments (Render, Heroku, etc.)
- **Pros:** Better for handling many concurrent connections
- **Cons:** May not work from localhost due to network restrictions
- **Format:** `postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-west-2.pooler.supabase.com:6543/postgres`

### Port 5432 (Direct Connection)
- **What it is:** Direct connection to PostgreSQL database
- **When to use:** Local development
- **Pros:** More reliable from localhost, simpler setup
- **Cons:** Limited concurrent connections
- **Format:** `postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-west-2.pooler.supabase.com:5432/postgres`

## Current Issue: Connection Refused on Port 6543

If you're seeing:
```
connection to server at "aws-0-us-west-2.pooler.supabase.com" (port 6543) failed: Connection refused
```

**This means:** The pooler (port 6543) is not accessible from your local machine.

## Solution: Switch to Direct Connection (Port 5432)

### Step 1: Get Direct Connection String

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Go to **Settings** → **Database**
4. Scroll to **Connection string**
5. Select **"URI"** tab (NOT "Connection pooling")
6. Copy the connection string

It should look like:
```
postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-west-2.pooler.supabase.com:5432/postgres
```

**Note:** Even though it says "pooler.supabase.com", port 5432 is the direct connection.

### Step 2: Update `backend/.env`

Open `backend/.env` and update `DATABASE_URL`:

```env
# Change from port 6543 to 5432
DATABASE_URL=postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require
```

**Important:**
- Change port from `:6543` to `:5432`
- Add `?sslmode=require` at the end (if not already present)
- Replace `[PASSWORD]` with your actual database password

### Step 3: Restart Backend

After updating `backend/.env`, restart the backend:

```bash
cd backend
python -m app.main
```

You should see:
```
SmartTrip API running on http://0.0.0.0:5000
```

No connection errors!

## When to Use Each Port

### Use Port 5432 (Direct) When:
- ✅ Local development
- ✅ Testing on your machine
- ✅ Port 6543 doesn't work

### Use Port 6543 (Pooler) When:
- ✅ Production deployment (Render, Heroku)
- ✅ Need to handle many concurrent connections
- ✅ Port 6543 works from your network

## Quick Fix Summary

**If you have port 6543 in your `DATABASE_URL`:**

1. **Change it to 5432** in `backend/.env`
2. **Add `?sslmode=require`** if missing
3. **Restart backend**

**Example:**
```env
# Before (not working):
DATABASE_URL=postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-west-2.pooler.supabase.com:6543/postgres

# After (should work):
DATABASE_URL=postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require
```

## Verify Connection

After updating, test the connection:

```bash
# Backend should start without errors
cd backend
python -m app.main

# In another terminal, test API:
curl http://localhost:5000/api/health
```

If you still get connection errors, check:
1. Password is correct in connection string
2. `?sslmode=require` is at the end
3. No extra spaces or characters in the connection string
