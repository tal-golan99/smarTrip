# Troubleshooting Steps for Page Loading Issues

## Step 1: Clear Next.js Cache
Run these commands to completely clear the Next.js build cache:

```powershell
cd "C:\Users\talgo\Documents\smarTrip project\trip-recommendations"

# Stop the dev server (Ctrl+C in terminal 1)

# Remove Next.js cache
Remove-Item -Recurse -Force .next

# Remove node_modules and reinstall
Remove-Item -Recurse -Force node_modules
npm install

# Restart dev server
npm run dev
```

## Step 2: Clear Browser Cache
1. Open your browser
2. Press `Ctrl+Shift+Delete`
3. Select "All time" for time range
4. Check "Cached images and files"
5. Click "Clear data"

## Step 3: Hard Refresh
1. Go to `http://localhost:3000`
2. Press `Ctrl+Shift+R` (hard refresh)
3. Or press `F12` to open DevTools, then right-click the refresh button and select "Empty Cache and Hard Reload"

## Step 4: Check Browser Console
1. Press `F12` to open Developer Tools
2. Go to the **Console** tab
3. Try to navigate to `/search` or click the CTA button
4. Check for any red error messages

## Step 5: Test in Incognito
1. Press `Ctrl+Shift+N` for incognito mode
2. Go to `http://localhost:3000`
3. Try clicking the CTA button

## Common Issues

### Issue: "Module not found: Can't resolve 'uuid'"
**Solution**: The uuid package is installed, but Next.js needs to be restarted.

### Issue: Pages return 200 but don't display
**Solution**: This is usually a browser cache issue. Follow Steps 2-3 above.

### Issue: Blank white page
**Solution**: Check the browser console for JavaScript errors (Step 4).

## Quick Test
If the server is running, you should be able to open:
- `http://localhost:3000/` - Landing page
- `http://localhost:3000/search` - Search page
- `http://localhost:5000/` - Backend API

If you see "Cannot GET /" on the backend, that's normal - it means the backend is running.
