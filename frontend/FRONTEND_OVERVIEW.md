# Frontend Overview

This document provides an overview of the current frontend structure after the project restructure, including identified issues with file organization.

## Current Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── auth/              # Authentication pages
│   │   ├── search/            # Search functionality
│   │   ├── trip/              # Trip detail pages
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   └── globals.css        # Global styles
│   ├── components/
│   │   ├── ui/                # Generic UI components (EMPTY - only README.md)
│   │   └── features/          # Feature-specific components (EMPTY - only README.md)
│   ├── hooks/
│   │   └── useTracking.ts     # Tracking hooks (single file with multiple hooks)
│   ├── lib/
│   │   ├── dataStore.tsx      # Centralized data store (React Context + hooks)
│   │   └── supabaseClient.ts  # Supabase authentication client
│   ├── services/
│   │   ├── api.service.ts     # API client for backend communication
│   │   └── tracking.service.ts # Event tracking service
│   └── types/                 # Type definitions (if exists)
├── public/                    # Static assets
└── ...config files
```

## Detailed Breakdown

### Pages (`src/app/`)

#### Home Page (`page.tsx`)
- Landing page with marketing content
- User authentication state management
- Navigation to search page
- **Inline Components**: None (pure page component)

#### Search Page (`search/page.tsx`)
- Main search interface with filters
- Location, trip type, theme selection
- Date, duration, budget, difficulty filters
- **Inline Components**:
  - `SelectionBadge` - Badge for selected locations
  - `TagCircle` - Tag selection button
  - `DualRangeSlider` - Range slider for duration
  - `SearchPageContent` - Main component
  - `SearchPageLoading` - Loading state

#### Search Results (`search/results/page.tsx`)
- Displays search results with trip cards
- Score-based color coding
- Filter refinement suggestions
- **Inline Components**:
  - `TripResultCard` - Trip card wrapper with impression tracking
  - `SearchResultsPageContent` - Main component
  - `ResultsPageLoading` - Loading state
  - `useScrollDepthTracking` - Custom hook (should be in hooks/)

#### Trip Detail Page (`trip/[id]/page.tsx`)
- Individual trip detail view
- Registration modal
- **Inline Components**:
  - `RegistrationModal` - Modal for registration action

#### Authentication Pages
- `auth/page.tsx` - Login/signup page
- `auth/callback/page.tsx` - OAuth callback handler

### Components

#### UI Components (`src/components/ui/`)
**Status**: EMPTY - Only contains `README.md`

**Expected Purpose**: Generic, reusable UI components
- Buttons
- Inputs
- Cards
- Modals
- Loading spinners
- Form elements

**Current Issue**: All UI components are inline in page files. Should be extracted here.

#### Feature Components (`src/components/features/`)
**Status**: EMPTY - Only contains `README.md`

**Expected Purpose**: Business-domain specific components
- Trip cards
- Search filters
- Recommendation displays
- Booking forms

**Current Issue**: Feature components are inline in page files. Should be extracted here.

### Hooks (`src/hooks/`)

#### `useTracking.ts`
**Status**: SINGLE FILE with multiple hooks

**Contains**:
- `usePageView` - Track page views
- `useTripDwellTime` - Track time on trip pages
- `useImpressionTracking` - Track visible trip cards
- `useResultsTracking` - Track search results display
- `useFilterTracking` - Track filter changes
- `useTrackingIds` - Get tracking IDs
- Re-exports from `tracking.service`

**Assessment**: This is acceptable as all hooks are related to tracking. Could potentially split into separate files for better organization, but current structure is reasonable.

**Missing from hooks**: `useScrollDepthTracking` is defined in `search/results/page.tsx` and should be moved to `hooks/`.

### Libraries (`src/lib/`)

#### `dataStore.tsx`
**Status**: React Context + Provider + Custom Hooks

**Purpose**: Centralized data store for reference data (countries, trip types, theme tags)
- Provides caching
- Loading and error states
- Cold start detection
- Icon mappings
- Continent data

**Assessment**: Functionality is appropriate, but location may be incorrect.
- Could belong in `services/` since it handles data fetching
- Or could stay in `lib/` if considered a utility/library

**Recommendation**: Keep in `lib/` as it provides reusable hooks and utilities, not just API calls.

#### `supabaseClient.ts`
**Status**: Supabase client configuration

**Purpose**: Authentication client setup
- Singleton Supabase client
- Session management functions
- User access functions

**Assessment**: Correctly placed in `lib/` as a client library.

### Services (`src/services/`)

#### `api.service.ts`
**Status**: API client service

**Purpose**: HTTP client for backend communication
- Authentication headers
- Retry logic for cold starts
- Type definitions for API responses
- All API endpoint functions

**Assessment**: Correctly placed in `services/`.

#### `tracking.service.ts`
**Status**: Event tracking service

**Purpose**: Low-level event tracking implementation
- Event queue management
- Batching logic
- Session initialization
- Device detection
- High-level tracking functions

**Assessment**: Correctly placed in `services/`.

## Issues and Recommendations

### Critical Issues

#### 1. Empty Component Folders
**Problem**: `components/ui/` and `components/features/` only contain README files with no actual components.

**Components to Extract**:

**To `components/ui/`**:
- `SelectionBadge` (from `search/page.tsx`)
- `TagCircle` (from `search/page.tsx`)
- `DualRangeSlider` (from `search/page.tsx`)
- `RegistrationModal` (from `trip/[id]/page.tsx`)
- Generic loading spinners
- Generic error states

**To `components/features/`**:
- `TripResultCard` (from `search/results/page.tsx`)
- Search filters (location, date, budget, etc.)
- Trip detail sections
- Result list components

**Action Required**: Extract inline components from pages to appropriate component folders.

#### 2. Hook in Wrong Location
**Problem**: `useScrollDepthTracking` is defined in `search/results/page.tsx` but should be in `src/hooks/`.

**Action Required**: Move `useScrollDepthTracking` from `search/results/page.tsx` to `src/hooks/useScrollDepthTracking.ts` or add it to `src/hooks/useTracking.ts`.

### Minor Issues

#### 3. Hook Organization
**Current**: All tracking hooks in single file `useTracking.ts`

**Recommendation**: Current structure is acceptable. Consider splitting only if file becomes too large (>500 lines). Current file is ~384 lines, which is manageable.

#### 4. Component Reusability
**Problem**: Some components are duplicated across pages (e.g., loading states, error states).

**Recommendation**: Create shared UI components for:
- Loading spinners with text
- Error states with retry
- Empty states

### File Organization Assessment

| File/Folder | Current Location | Should Be | Status |
|------------|-----------------|-----------|---------|
| `SelectionBadge` | `search/page.tsx` (inline) | `components/ui/` | ❌ Wrong location |
| `TagCircle` | `search/page.tsx` (inline) | `components/ui/` | ❌ Wrong location |
| `DualRangeSlider` | `search/page.tsx` (inline) | `components/ui/` | ❌ Wrong location |
| `TripResultCard` | `search/results/page.tsx` (inline) | `components/features/` | ❌ Wrong location |
| `RegistrationModal` | `trip/[id]/page.tsx` (inline) | `components/ui/` | ❌ Wrong location |
| `useScrollDepthTracking` | `search/results/page.tsx` (inline) | `hooks/` | ❌ Wrong location |
| `dataStore.tsx` | `lib/` | `lib/` or `services/` | ⚠️ Debatable |
| `api.service.ts` | `services/` | `services/` | ✅ Correct |
| `tracking.service.ts` | `services/` | `services/` | ✅ Correct |
| `supabaseClient.ts` | `lib/` | `lib/` | ✅ Correct |
| `useTracking.ts` | `hooks/` | `hooks/` | ✅ Correct |

## Recommendations Summary

1. **Extract inline components** from pages to `components/ui/` and `components/features/`
2. **Move `useScrollDepthTracking`** hook to `hooks/` folder
3. **Create shared UI components** for loading/error/empty states
4. **Keep current hook organization** (single file is acceptable for now)
5. **Keep `dataStore.tsx` in `lib/`** (provides hooks and utilities, not just API calls)

## Next Steps

1. Create component files in `components/ui/` and `components/features/`
2. Extract inline components from pages
3. Move `useScrollDepthTracking` to hooks folder
4. Update imports in all affected files
5. Test that all functionality still works after refactoring
