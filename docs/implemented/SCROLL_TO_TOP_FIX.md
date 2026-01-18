# Fix: Prevent Scroll to Top on Filter Changes

## Issue

When users clicked on trip themes, selected a year, or changed any filter on the search page, the page would automatically scroll to the top. This created a poor user experience as users lost their place on the page.

## Root Cause

The issue was in `useSearchFilters.ts`. When updating URL parameters using Next.js router methods (`router.push()` and `router.replace()`), the default behavior is to scroll to the top of the page.

```typescript
// BEFORE (caused scroll to top)
router.replace(url);
router.push(url);
```

## Solution

Added the `scroll: false` option to all router navigation calls that update filters on the same page.

```typescript
// AFTER (prevents scroll)
router.replace(url, { scroll: false });
router.push(url, { scroll: false });
```

## Changes Made

### File: `frontend/src/hooks/useSearchFilters.ts`

1. **`updateUrl` function** (line 205-214):
   - Added `{ scroll: false }` to `router.replace()`
   - Added `{ scroll: false }` to `router.push()`

2. **`clearAllFilters` function** (line 322-324):
   - Added `{ scroll: false }` to `router.replace()`

## Why This Works

Next.js router methods accept an options object as the second parameter:
- `scroll: true` (default) - Scrolls to top of page after navigation
- `scroll: false` - Maintains current scroll position

For filter updates on the same page, we want to maintain scroll position. For actual page navigation (like `executeSearch` going to results page), we keep the default scroll behavior.

## User Experience Impact

**Before**:
- User scrolls down to theme section
- Clicks on a theme
- Page jumps to top
- User has to scroll back down
- Frustrating experience

**After**:
- User scrolls down to theme section
- Clicks on a theme
- Page stays in place
- User can continue selecting filters
- Smooth experience

## Related Code

The search page already had logic to prevent scroll on initial mount:

```typescript
// frontend/src/app/search/page.tsx (lines 136-141)
const isInitialMount = useRef(true);

useEffect(() => {
  if (isInitialMount.current) {
    window.scrollTo({ top: 0, behavior: 'instant' });
    isInitialMount.current = false;
  }
}, []);
```

This ensures:
- Initial page load scrolls to top (good UX)
- Filter changes don't scroll (good UX)

## Testing

To verify the fix:
1. Navigate to `/search`
2. Scroll down to the theme section
3. Click on a theme tag
4. Verify page stays in place (doesn't jump to top)
5. Try other filters (year, month, duration, etc.)
6. Verify scroll position is maintained for all filter changes

## Notes

- The `executeSearch` function still scrolls to top when navigating to results page (intentional)
- This is expected behavior as it's a new page
- Only filter updates on the same page prevent scroll
