# Frontend Overview & Refactoring Guide

## Table of Contents
1. [Current Structure](#current-structure)
2. [Issues Identified](#issues-identified)
3. [Refactoring Recommendations (PRAGMATIC APPROACH)](#refactoring-recommendations-pragmatic-approach)
4. [Implementation Checklist](#implementation-checklist-pragmatic-approach)
5. [Component Extraction Plan](#component-extraction-plan)
6. [Hook Extraction Plan](#hook-extraction-plan)
7. [Utility Functions to Create](#utility-functions-to-create)
8. [File Organization](#file-organization)
9. [Manual Verification Guide](#manual-verification-guide)
10. [Additional Analysis](#additional-analysis-comprehensive-code-review)

---

## Current Structure

### Directory Layout
```
frontend/src/
├── app/                    # Next.js App Router pages
│   ├── auth/              # Authentication pages
│   ├── search/            # Search and results pages
│   ├── trip/              # Trip detail pages
│   └── page.tsx           # Home page
├── components/            # React components (mostly empty)
│   ├── features/          # Feature-specific components (empty)
│   └── ui/                # UI components (empty)
├── hooks/                 # Custom React hooks
│   └── useTracking.ts    # Tracking hooks
├── lib/                   # Library/utility code
│   ├── dataStore.tsx      # Centralized data store (616 lines)
│   └── supabaseClient.ts  # Supabase auth client
└── services/              # API and service layers
    ├── api.service.ts     # API client (634 lines)
    └── tracking.service.ts # Tracking service (609 lines)
```

### File-by-File Analysis

#### `app/layout.tsx` (29 lines)
**Status:** Clean, minimal
**Issues:**
- **CRITICAL:** Does NOT wrap app with `DataStoreProvider`
- Should include `DataStoreProvider` wrapper

**Uses:**
- None (just layout structure)

**Creates:**
- None

---

#### `app/page.tsx` (Home - 384 lines)
**Status:** Mostly clean, some duplication
**Uses:**
- ✅ `supabaseClient` for auth
- ❌ Does NOT use DataStore (doesn't need it)
- ❌ Does NOT use API services (doesn't need it)

**Creates:**
- Inline logout confirmation modal logic (duplicated in search/page.tsx)
- User loading logic (duplicated in search/page.tsx)

**Issues:**
- User loading logic duplicated (should use `useUser` hook)
- Logout modal logic duplicated (should be component)

---

#### `app/auth/page.tsx` (402 lines)
**Status:** Clean, well-organized
**Uses:**
- ✅ `supabaseClient` for auth
- ❌ Does NOT use DataStore (doesn't need it)
- ❌ Does NOT use API services (doesn't need it)

**Creates:**
- None (all logic is appropriate for auth page)

**Issues:**
- None significant

---

#### `app/auth/callback/page.tsx` (179 lines)
**Status:** Clean, well-organized
**Uses:**
- ✅ `supabaseClient` for auth
- ❌ Does NOT use DataStore (doesn't need it)
- ❌ Does NOT use API services (doesn't need it)

**Creates:**
- None (all logic is appropriate for callback)

**Issues:**
- None significant

---

#### `app/search/page.tsx` (1,460 lines) ⚠️ LARGE FILE
**Status:** Too large, duplicates DataStore functionality
**Uses:**
- ✅ `getLocations()`, `getTripTypes()`, `getTags()` from `api.service.ts`
- ✅ Constants from `dataStore.tsx` (CONTINENTS, icons, flags)
- ❌ **CRITICAL:** Does NOT use DataStore hooks (`useCountries`, `useTripTypes`, `useThemeTags`)
- ✅ Tracking hooks from `useTracking.ts`
- ✅ `supabaseClient` for auth

**Creates:**
- ❌ Local state for countries, tripTypes, themeTags (duplicates DataStore)
- ❌ `fetchCountries()` function (duplicates DataStore)
- ❌ `fetchTypesAndTags()` function (duplicates DataStore)
- ❌ `SelectionBadge` component (should be extracted)
- ❌ `TagCircle` component (should be extracted)
- ❌ `DualRangeSlider` component (should be extracted)
- ❌ `SearchPageLoading` component (should be extracted)
- ❌ Logout confirmation modal (duplicated)
- ❌ User loading logic (duplicated)
- ❌ Helper functions: `getAvailableMonths()`, `getAvailableYears()`

**Issues:**
- **CRITICAL:** Duplicates DataStore functionality instead of using it
- Too many inline components
- Duplicate user loading logic
- Duplicate logout modal

---

#### `app/search/results/page.tsx` (685 lines) ⚠️ LARGE FILE
**Status:** Too large, has inline components and hooks
**Uses:**
- ✅ `getRecommendations()` from `api.service.ts`
- ✅ Tracking hooks from `useTracking.ts`
- ✅ Types from `api.service.ts`
- ❌ Does NOT use DataStore (doesn't need it for this page)

**Creates:**
- ❌ `TripResultCard` component (should be extracted)
- ❌ `useScrollDepthTracking` hook (should be in hooks folder)
- ❌ `ResultsPageLoading` component (should be extracted)
- ❌ Helper functions: `getScoreColor()`, `getScoreBgClass()`, `getStatusLabel()`, `getStatusIconUrl()`, `getStatusIcon()`, `getTripField()`

**Issues:**
- Inline hook should be in hooks folder
- Inline components should be extracted
- Duplicate helper functions (also in trip/[id]/page.tsx)

---

#### `app/trip/[id]/page.tsx` (396 lines)
**Status:** Uses direct fetch instead of service
**Uses:**
- ✅ Types from `api.service.ts`
- ✅ Tracking hooks from `useTracking.ts`
- ❌ **CRITICAL:** Uses direct `fetch()` instead of `getTrip()` from `api.service.ts`
- ❌ Does NOT use DataStore (doesn't need it)

**Creates:**
- ❌ `RegistrationModal` component (should be extracted)
- ❌ Helper functions: `getTripField()`, `formatDate()`, `calculateDuration()`, `getDifficultyLabel()`, `getStatusLabel()`

**Issues:**
- **CRITICAL:** Direct fetch missing retry logic and error handling
- Duplicate helper functions (also in results/page.tsx)
- Inline component should be extracted

---

#### `app/error.tsx` (40 lines)
**Status:** Clean, simple error page
**Uses:**
- None

**Creates:**
- None

**Issues:**
- None

---

#### `app/not-found.tsx` (33 lines)
**Status:** Clean, simple 404 page
**Uses:**
- None

**Creates:**
- None

**Issues:**
- None

---

#### `app/search/error.tsx` (47 lines)
**Status:** Clean, simple error page
**Uses:**
- ✅ `useRouter` from Next.js

**Creates:**
- None

**Issues:**
- None

---

#### `app/search/results/error.tsx` (47 lines)
**Status:** Clean, simple error page
**Uses:**
- ✅ `useRouter` from Next.js

**Creates:**
- None

**Issues:**
- None

---

#### `app/search/results/loading.tsx` (13 lines)
**Status:** Clean, simple loading component
**Uses:**
- None

**Creates:**
- None

**Issues:**
- None

---

### Key Files Analysis

#### Large Files (>500 lines)
1. **`app/search/page.tsx`** (1,460 lines)
   - Contains: Search form, filters, data fetching, UI components
   - Issues: Too large, mixed concerns, inline components

2. **`app/search/results/page.tsx`** (685 lines)
   - Contains: Results display, tracking, inline components
   - Issues: Should extract components, move hooks

3. **`lib/dataStore.tsx`** (616 lines)
   - Contains: Data store context, hooks, icon mappings, constants
   - Status: Well-organized but could split constants

4. **`services/api.service.ts`** (634 lines)
   - Contains: API client, type definitions, all API functions
   - Status: Well-organized, appropriate size

5. **`services/tracking.service.ts`** (609 lines)
   - Contains: Tracking service, event management
   - Status: Well-organized, appropriate size

---

## Critical Finding: DataStore Not Being Used

### DataStore Provider Status
**CRITICAL ISSUE:** The `DataStoreProvider` and its hooks (`useCountries`, `useTripTypes`, `useThemeTags`) are **NOT being used** by any pages!

**Current State:**
- `lib/dataStore.tsx` exists (616 lines) with full implementation
- `DataStoreProvider` is defined but **never wrapped around the app** in `layout.tsx`
- No pages use `useCountries()`, `useTripTypes()`, or `useThemeTags()` hooks
- `search/page.tsx` imports constants from dataStore (CONTINENTS, icons) but creates its own state and fetch functions

**Impact:**
- Duplicate data fetching logic in `search/page.tsx` (lines 546-664)
- DataStore was built but never integrated
- Wasted effort and code duplication

**Recommendation:**
- **Option 1:** Wrap app with `DataStoreProvider` in `layout.tsx` and refactor `search/page.tsx` to use hooks
- **Option 2:** Remove DataStore if not needed (but it seems well-designed and should be used)

---

## Issues Identified

### 1. Duplicate Functions

#### `getTripField` - Duplicated in 2 files
- **Location 1:** `app/search/results/page.tsx:145`
- **Location 2:** `app/trip/[id]/page.tsx:23`
- **Purpose:** Helper to get trip fields with both snake_case and camelCase support
- **Recommendation:** Move to `lib/utils/tripUtils.ts`

#### `getStatusLabel` - Duplicated in 2 files
- **Location 1:** `app/search/results/page.tsx:53`
- **Location 2:** `app/trip/[id]/page.tsx:54`
- **Purpose:** Translate trip status to Hebrew
- **Recommendation:** Move to `lib/utils/tripUtils.ts`

#### `formatDate` - Duplicated in 1 file (but reusable)
- **Location:** `app/trip/[id]/page.tsx:29`
- **Purpose:** Format date to DD.MM.YYYY
- **Recommendation:** Move to `lib/utils/dateUtils.ts`

#### `calculateDuration` - Duplicated in 1 file (but reusable)
- **Location:** `app/trip/[id]/page.tsx:35`
- **Purpose:** Calculate duration in days between dates
- **Recommendation:** Move to `lib/utils/dateUtils.ts`

#### `getDifficultyLabel` - Duplicated in 1 file (but reusable)
- **Location:** `app/trip/[id]/page.tsx:44`
- **Purpose:** Get difficulty label in Hebrew
- **Recommendation:** Move to `lib/utils/tripUtils.ts`

#### User Loading Logic - Duplicated in 2 files
- **Location 1:** `app/page.tsx:17-71`
- **Location 2:** `app/search/page.tsx:425-482`
- **Purpose:** Load user name from Supabase metadata
- **Recommendation:** Extract to `hooks/useUser.ts`

### 2. Long Files Doing Too Much

#### `app/search/page.tsx` (1,460 lines)
**Issues:**
- **CRITICAL:** Does NOT use DataStore hooks - creates own state and fetch functions (lines 374-382, 546-664)
- Contains data fetching logic that duplicates DataStore functionality
- Contains inline UI components (should be extracted)
- Contains complex state management
- Contains helper functions (should be utilities)

**Components to Extract:**
- `SelectionBadge` (lines 116-178)
- `TagCircle` (lines 180-215)
- `DualRangeSlider` (lines 221-363)
- `SearchPageLoading` (lines 1431-1451)
- Logout confirmation modal (lines 980-1004)

**Data Fetching:**
- `fetchCountries` (lines 546-588) - Uses `getLocations()` from API service (GOOD, but should use DataStore)
- `fetchTypesAndTags` (lines 592-664) - Uses `getTripTypes()` and `getTags()` (GOOD, but should use DataStore)
- **Should be replaced with:** `useCountries()`, `useTripTypes()`, `useThemeTags()` from DataStore

#### `app/search/results/page.tsx` (685 lines)
**Issues:**
- Contains inline hook `useScrollDepthTracking` (lines 157-211) - should be in hooks folder
- Contains inline component `TripResultCard` (lines 107-142) - should be in components
- Contains helper functions that should be utilities

**Components to Extract:**
- `TripResultCard` wrapper (lines 107-142)
- Status badge rendering logic (lines 550-581)
- Score badge rendering logic (lines 536-548)

**Hooks to Extract:**
- `useScrollDepthTracking` (lines 157-211)

#### `app/trip/[id]/page.tsx` (396 lines)
**Issues:**
- **CRITICAL:** Uses direct `fetch()` instead of API service (line 153)
- Contains inline component `RegistrationModal` (lines 68-112)
- Contains helper functions that should be utilities

**Components to Extract:**
- `RegistrationModal` (lines 68-112)
- Status badge (could be shared component)
- Quick info cards section (lines 273-312)

**API Issues:**
- Line 153: Direct `fetch()` instead of using `getTrip()` from `api.service.ts`
- **Impact:** Missing retry logic, error handling, and authentication headers

### 3. Missing Component Organization

**Current State:**
- `components/features/` - Empty (only README.md)
- `components/ui/` - Empty (only README.md)

**Should Contain:**
- Reusable UI components (buttons, badges, modals, cards)
- Feature-specific components (trip cards, search filters, etc.)

### 4. Missing Hook Organization

**Current State:**
- `hooks/useTracking.ts` - Well organized
- Missing: `useUser.ts`, `useScrollDepth.ts`, `useSearchFilters.ts`, etc.

### 5. Missing Utility Organization

**Current State:**
- No dedicated utilities folder
- Helper functions scattered across page files

**Should Create:**
- `lib/utils/tripUtils.ts` - Trip-related utilities
- `lib/utils/dateUtils.ts` - Date formatting utilities
- `lib/utils/formatUtils.ts` - General formatting utilities

---

## Refactoring Recommendations (PRAGMATIC APPROACH)

> **Note:** This plan follows a pragmatic, high-impact approach. We focus on eliminating critical issues and major duplications, avoiding over-engineering for a personal project. Keep it simple and maintainable.

### Quick Summary

**What We're Doing:**
1. ✅ DataStore integration (eliminates ~120 lines of duplicate fetching)
2. ✅ User hook (eliminates ~50 lines × 2 files = 100 lines)
3. ✅ Fix API service usage (better error handling)
4. ✅ Extract only 4 complex components (not 10+)
5. ✅ Single `utils.ts` file (not multiple files)

**What We're NOT Doing:**
- ❌ Creating atomic UI component library
- ❌ Multiple utility files (keeping it simple)
- ❌ Extracting simple components
- ❌ Over-engineering the structure

**Expected Results:**
- Reduce `search/page.tsx` from 1,460 → ~1,200 lines
- Reduce `results/page.tsx` from 685 → ~450 lines  
- Reduce `trip/[id]/page.tsx` from 396 → ~350 lines
- Eliminate ~170 lines of duplicate code
- Better code organization without over-engineering

---

### Execution Plan (Priority Order)

> **Focus on Steps 1-3 first (most critical).** Steps 4-5 can be done later.

#### Priority 1: DataStore Integration (CRITICAL)

**Goal:** Eliminate duplicate data fetching in `search/page.tsx` by using the existing DataStore.

**Step 1.1: Wrap App with DataStoreProvider**

**File: `app/layout.tsx`**
```typescript
import type { Metadata } from "next";
import { Assistant } from "next/font/google";
import "./globals.css";
import { DataStoreProvider } from '@/lib/dataStore';

const assistant = Assistant({
  subsets: ['latin', 'hebrew'],
  weight: ['200', '300', '400', '500', '600', '700', '800'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: "SmarTrip - מערכת המלצות טיולים",
  description: "מערכת המלצות חכמה לטיולים מאורגנים - איילה גיאוגרפית",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="he" dir="rtl">
      <body className={`${assistant.className} antialiased`}>
        <DataStoreProvider>
          {children}
        </DataStoreProvider>
      </body>
    </html>
  );
}
```

**Step 1.2: Refactor `app/search/page.tsx` to Use DataStore Hooks**

**Remove:**
- Lines 374-382: Local state for countries, tripTypes, themeTags
- Lines 385-386: Cold start detection state (handled by DataStore)
- Lines 546-588: `fetchCountries` function
- Lines 592-664: `fetchTypesAndTags` function
- Lines 667-674: useEffect hooks that call fetch functions
- Lines 677-680: `retryFetchData` function

**Replace with:**
```typescript
// At the top, replace the import
// OLD: import { getLocations, getTripTypes, getTags } from '@/services/api.service';
// NEW:
import { useCountries, useTripTypes, useThemeTags } from '@/lib/dataStore';

// Inside SearchPageContent component, replace state declarations:
// OLD:
// const [countries, setCountries] = useState<Country[]>([]);
// const [isLoadingCountries, setIsLoadingCountries] = useState(true);
// const [countriesError, setCountriesError] = useState(false);
// const [tripTypes, setTripTypes] = useState<SearchTag[]>([]);
// const [themeTags, setThemeTags] = useState<SearchTag[]>([]);
// const [isLoadingTypes, setIsLoadingTypes] = useState(true);
// const [typesError, setTypesError] = useState(false);
// const [isColdStart, setIsColdStart] = useState(false);
// const [retryAttempt, setRetryAttempt] = useState(0);

// NEW:
const { countries, isLoading: isLoadingCountries, error: countriesError } = useCountries();
const { tripTypes, isLoading: isLoadingTripTypes, error: tripTypesError } = useTripTypes();
const { themeTags, isLoading: isLoadingThemeTags, error: themeTagsError } = useThemeTags();

// Remove all fetch functions (fetchCountries, fetchTypesAndTags)
// Remove all useEffect hooks that call fetch functions
// Remove retryFetchData function

// Update error handling:
const isLoading = isLoadingCountries || isLoadingTripTypes;
const hasError = countriesError || tripTypesError;
const hasData = countries.length > 0 && tripTypes.length > 0;

// Update retry button to use DataStore refresh methods:
// In the error UI, replace retryFetchData() with:
// const { refreshAll } = useDataStore();
// onClick={() => refreshAll()}
```

**Expected Impact:**
- Remove ~120 lines of duplicate fetching logic
- Eliminate duplicate API calls
- Consistent error handling via DataStore

---

#### Priority 2: Deduplicate User Logic

**Goal:** Create a single hook to eliminate user loading logic duplication.

**Step 2.1: Create `hooks/useUser.ts`**

**New File: `hooks/useUser.ts`**
```typescript
'use client';

import { useState, useEffect } from 'react';
import { getCurrentUser, supabase, isAuthAvailable } from '@/lib/supabaseClient';

export function useUser() {
  const [userName, setUserName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<any | null>(null);

  useEffect(() => {
    const loadUser = async () => {
      if (!isAuthAvailable() || !supabase) {
        setIsLoading(false);
        return;
      }
      
      try {
        const user = await getCurrentUser();
        if (user) {
          setUser(user);
          // Extract full name from user metadata or email
          const metadata = user.user_metadata || {};
          let fullName = null;
          if (metadata.full_name) {
            fullName = metadata.full_name;
          } else if (metadata.name) {
            fullName = metadata.name;
          } else if (metadata.first_name && metadata.last_name) {
            fullName = `${metadata.first_name} ${metadata.last_name}`;
          } else if (metadata.first_name) {
            fullName = metadata.first_name;
          } else if (metadata.last_name) {
            fullName = metadata.last_name;
          } else if (user.email && user.email.split('@')[0]) {
            fullName = user.email.split('@')[0];
          }
          setUserName(fullName);
        } else {
          setUserName(null);
        }
      } catch (error) {
        console.error('[useUser] Error loading user:', error);
        setUserName(null);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadUser();
    
    // Listen for auth state changes
    if (supabase) {
      const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
        if (session?.user) {
          loadUser();
        } else {
          setUserName(null);
          setUser(null);
          setIsLoading(false);
        }
      });
      
      return () => {
        subscription.unsubscribe();
      };
    }
  }, []);

  return { userName, isLoading, user };
}
```

**Step 2.2: Update `app/page.tsx`**

**Remove:**
- Lines 12-13: `userName` and `isLoadingUser` state
- Lines 17-71: Entire `useEffect` with `loadUser` function

**Replace with:**
```typescript
import { useUser } from '@/hooks/useUser';

export default function Home() {
  const { userName, isLoading: isLoadingUser } = useUser();
  // ... rest of component
}
```

**Step 2.3: Update `app/search/page.tsx`**

**Remove:**
- Lines 417-419: `userName`, `isLoadingUser`, `showLogoutConfirm` state
- Lines 425-482: Entire `useEffect` with `loadUser` function

**Replace with:**
```typescript
import { useUser } from '@/hooks/useUser';

function SearchPageContent() {
  const { userName, isLoading: isLoadingUser } = useUser();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  // ... rest of component
}
```

**Expected Impact:**
- Remove ~50 lines of duplicate code from each file
- Single source of truth for user state

---

#### Priority 3: Fix API Service Usage

**Goal:** Replace direct fetch with service function for consistent error handling.

**Step 3.1: Update `app/trip/[id]/page.tsx`**

**Remove:**
- Line 20: `const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';`
- Lines 142-181: Entire `fetchTrip` function with direct fetch

**Replace with:**
```typescript
import { getTrip } from '@/services/api.service';

export default function TripPage() {
  // ... existing code ...
  
  // Replace the entire fetchTrip useEffect:
  useEffect(() => {
    const fetchTrip = async () => {
      if (!tripId) return;
      
      setIsLoading(true);
      setError(null);

      try {
        const response = await getTrip(tripIdNum);
        
        if (!response.success || !response.data) {
          if (response.error?.includes('404') || response.error?.includes('not found')) {
            throw new Error('הטיול לא נמצא');
          }
          throw new Error(response.error || 'שגיאה בטעינת פרטי הטיול');
        }

        setTrip(response.data);
      } catch (err) {
        console.error('Error fetching trip:', err);
        setError(err instanceof Error ? err.message : 'שגיאה בטעינת פרטי הטיול');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrip();
  }, [tripId, tripIdNum]);
  
  // ... rest of component
}
```

**Expected Impact:**
- Consistent error handling with retry logic
- Automatic authentication headers
- Better timeout handling

---

### Priority 4: Selective Component Extraction (ONLY Complex Ones)

**Goal:** Extract only the most massive/complex components to reduce file size.

#### 4.1 Extract `DualRangeSlider` (from search page)

**Extract:** `app/search/page.tsx:221-363` → `components/features/DualRangeSlider.tsx`

**Reason:** Complex component with drag handling, RTL support, and state management (~140 lines)

#### 4.2 Extract `TripResultCard` (from results page)

**Extract:** `app/search/results/page.tsx:107-142, 520-628` → `components/features/TripResultCard.tsx`

**Reason:** Complex component with impression tracking, multiple badges, hover effects (~200 lines)

#### 4.3 Extract `RegistrationModal` (from trip page)

**Extract:** `app/trip/[id]/page.tsx:68-112` → `components/features/RegistrationModal.tsx`

**Reason:** Reusable modal component (~45 lines)

#### 4.4 Extract `LogoutConfirmModal` (shared)

**Extract:** From `app/page.tsx` and `app/search/page.tsx` → `components/features/LogoutConfirmModal.tsx`

**Reason:** Duplicated in 2 files, reusable component

**DO NOT extract:**
- Simple badge components (keep inline)
- Simple loading spinners (keep inline)
- Simple button components (keep inline)
- Generic UI components (no atomic component library)

---

### Priority 5: Simplified Utilities (Single File)

**Goal:** Create one utility file instead of multiple files for simplicity.

**Create: `lib/utils.ts`** (single file, not multiple files)

```typescript
import type { Trip } from '@/services/api.service';
import { CheckCircle, AlertCircle, Clock, XCircle } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

// ============================================
// TRIP UTILITIES
// ============================================

export function getTripField(trip: Trip, snakeCase: string, camelCase: string): any {
  return (trip as any)[snakeCase] || (trip as any)[camelCase];
}

export function getStatusLabel(status?: string): string {
  const statusMap: Record<string, string> = {
    'GUARANTEED': 'יציאה מובטחת',
    'LAST_PLACES': 'מקומות אחרונים',
    'OPEN': 'הרשמה פתוחה',
    'FULL': 'מלא',
    'CANCELLED': 'בוטל',
  };
  const statusNormalized = status?.toUpperCase().replace(/\s+/g, '_');
  return statusNormalized ? statusMap[statusNormalized] || 'הרשמה פתוחה' : 'הרשמה פתוחה';
}

export function getDifficultyLabel(level?: number): string {
  switch (level) {
    case 1: return 'קל';
    case 2: return 'בינוני';
    case 3: return 'מאתגר';
    default: return 'בינוני';
  }
}

export function getStatusIconUrl(status?: string): string | null {
  const statusNormalized = status?.toUpperCase().replace(/\s+/g, '_');
  switch (statusNormalized) {
    case 'GUARANTEED': return '/images/trip status/guaranteed.svg';
    case 'LAST_PLACES': return '/images/trip status/last places.svg';
    case 'OPEN': return '/images/trip status/open.svg';
    case 'FULL': return '/images/trip status/full.png';
    default: return null;
  }
}

export function getStatusIcon(status?: string): LucideIcon {
  const statusNormalized = status?.toUpperCase().replace(/\s+/g, '_');
  switch (statusNormalized) {
    case 'GUARANTEED': return CheckCircle;
    case 'LAST_PLACES': return AlertCircle;
    case 'OPEN': return Clock;
    case 'FULL': return XCircle;
    default: return Clock;
  }
}

// ============================================
// DATE UTILITIES
// ============================================

export function formatDate(dateString?: string): string {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('en-GB').replace(/\//g, '.');
}

export function calculateDuration(startDate?: string, endDate?: string): number {
  if (!startDate || !endDate) return 0;
  const start = new Date(startDate);
  const end = new Date(endDate);
  const diffTime = Math.abs(end.getTime() - start.getTime());
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

const MONTHS_HE = [
  'ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני',
  'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר'
];

export function getAvailableMonths(selectedYear: string): { index: number; name: string }[] {
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth();

  if (selectedYear === 'all' || parseInt(selectedYear) > currentYear) {
    return MONTHS_HE.map((name, index) => ({ index: index + 1, name }));
  }

  if (parseInt(selectedYear) === currentYear) {
    return MONTHS_HE
      .map((name, index) => ({ index: index + 1, name }))
      .filter(m => m.index > currentMonth);
  }

  return [];
}

export function getAvailableYears(): string[] {
  const currentYear = new Date().getFullYear();
  return [currentYear.toString(), (currentYear + 1).toString(), (currentYear + 2).toString()];
}

// ============================================
// SCORE UTILITIES
// ============================================

export interface ScoreThresholds {
  HIGH: number;
  MID: number;
}

export function getScoreColor(score: number, thresholds: ScoreThresholds): 'high' | 'mid' | 'low' {
  if (score >= thresholds.HIGH) return 'high';
  if (score >= thresholds.MID) return 'mid';
  return 'low';
}

export function getScoreBgClass(colorLevel: 'high' | 'mid' | 'low'): string {
  switch (colorLevel) {
    case 'high': return 'bg-[#12acbe]';  // Turquoise
    case 'mid': return 'bg-[#f59e0b]';   // Orange
    case 'low': return 'bg-[#ef4444]';   // Red
  }
}
```

**Update all imports:**
- Replace `from '@/lib/utils/tripUtils'` → `from '@/lib/utils'`
- Replace `from '@/lib/utils/dateUtils'` → `from '@/lib/utils'`
- Replace `from '@/lib/utils/scoreUtils'` → `from '@/lib/utils'`

**Expected Impact:**
- Simpler file structure (one file instead of three)
- Easier to maintain
- All utilities in one place

---

### Summary of Pragmatic Approach

**What We're Doing:**
1. ✅ DataStore integration (eliminates ~120 lines)
2. ✅ User hook (eliminates ~50 lines × 2 files)
3. ✅ Fix API service usage (better error handling)
4. ✅ Extract only 4 complex components
5. ✅ Single utils.ts file (simpler structure)

**What We're NOT Doing:**
- ❌ Creating atomic UI component library
- ❌ Multiple utility files (keeping it simple)
- ❌ Extracting simple components
- ❌ Over-engineering the structure
- ❌ Creating hooks for everything

**Expected Results:**
- Reduce `search/page.tsx` from 1,460 → ~1,200 lines
- Reduce `results/page.tsx` from 685 → ~450 lines
- Reduce `trip/[id]/page.tsx` from 396 → ~350 lines
- Eliminate ~170 lines of duplicate code
- Better code organization without over-engineering

#### Create `lib/utils/tripUtils.ts`
```typescript
// Extract all trip-related utilities
export function getTripField(trip: Trip, snakeCase: string, camelCase: string): any
export function getStatusLabel(status?: string): string
export function getDifficultyLabel(level?: number): string
export function getStatusIconUrl(status?: string): string | null
export function getStatusIcon(status?: string): LucideIcon
```

#### Create `lib/utils/dateUtils.ts`
```typescript
// Extract all date-related utilities
export function formatDate(dateString?: string): string
export function calculateDuration(startDate?: string, endDate?: string): number
export function getAvailableMonths(selectedYear: string): { index: number; name: string }[]
export function getAvailableYears(): string[]
```

### Priority 4: Selective Component Extraction (ONLY Complex Ones)

> **Note:** Following pragmatic approach - only extract the most massive/complex components. Skip simple components.

#### Extract ONLY These 4 Components:

1. **`DualRangeSlider.tsx`** (from search page)
   - **Reason:** Complex component with drag handling, RTL support (~140 lines)
   - **Location:** `components/features/DualRangeSlider.tsx`

2. **`TripResultCard.tsx`** (from results page)
   - **Reason:** Complex component with impression tracking, multiple badges (~200 lines)
   - **Location:** `components/features/TripResultCard.tsx`

3. **`RegistrationModal.tsx`** (from trip page)
   - **Reason:** Reusable modal component (~45 lines)
   - **Location:** `components/features/RegistrationModal.tsx`

4. **`LogoutConfirmModal.tsx`** (shared)
   - **Reason:** Duplicated in 2 files, reusable component
   - **Location:** `components/features/LogoutConfirmModal.tsx`

#### DO NOT Extract (Keep Inline):
- ❌ Simple badge components (SelectionBadge, TagCircle - keep inline)
- ❌ Simple loading spinners (keep inline)
- ❌ Simple button components (keep inline)
- ❌ Generic UI components (no atomic component library)
- ❌ QuickInfoCards (simple enough to keep inline)

### Priority 2: Deduplicate User Logic (Already Covered Above)

See Priority 2 in the "Execution Plan" section above for full details.

### Priority 3: Fix API Service Usage (Already Covered Above)

See Priority 3 in the "Execution Plan" section above for full details.

---

## Simplified File Structure (After Refactoring)

```
frontend/src/
├── app/                          # Next.js pages
│   ├── layout.tsx               # ✅ Wrapped with DataStoreProvider
│   ├── page.tsx                  # ✅ Uses useUser hook
│   ├── search/
│   │   ├── page.tsx             # ✅ Uses DataStore hooks, useUser hook
│   │   └── results/
│   │       └── page.tsx         # ✅ Uses utils, extracted components
│   └── trip/
│       └── [id]/
│           └── page.tsx         # ✅ Uses api.service, utils, extracted components
│
├── components/
│   └── features/                 # ✅ Only 4 complex components
│       ├── DualRangeSlider.tsx
│       ├── TripResultCard.tsx
│       ├── RegistrationModal.tsx
│       └── LogoutConfirmModal.tsx
│
├── hooks/
│   ├── useTracking.ts           # ✅ Existing
│   └── useUser.ts               # ✅ NEW: User management
│
├── lib/
│   ├── dataStore.tsx            # ✅ Existing (now integrated)
│   ├── supabaseClient.ts        # ✅ Existing
│   └── utils.ts                 # ✅ NEW: Single file with all utilities
│
└── services/
    ├── api.service.ts           # ✅ Existing
    └── tracking.service.ts      # ✅ Existing
```

**Key Changes:**
- ✅ Single `utils.ts` file (not multiple files)
- ✅ Only 4 extracted components (not 10+)
- ✅ Only 1 new hook (`useUser`)
- ✅ Flat, simple structure
- ✅ No generic UI component library

#### Split `app/search/page.tsx` (1,460 lines)
**Strategy:**
1. Extract components to `components/features/`
2. Extract hooks to `hooks/`
3. Extract utilities to `lib/utils/`
4. Keep only page logic and composition

**Target:** Reduce to ~400-500 lines

#### Split `app/search/results/page.tsx` (685 lines)
**Strategy:**
1. Extract `TripResultCard` component
2. Extract `useScrollDepthTracking` hook
3. Extract helper functions to utilities
4. Keep only page logic

**Target:** Reduce to ~300-400 lines

---

## Component Extraction Plan

### UI Components (`components/ui/`)

#### 1. `Badge.tsx`
**Purpose:** Generic badge component
**Props:**
- `children: ReactNode`
- `variant?: 'default' | 'success' | 'warning' | 'error' | 'info'`
- `size?: 'sm' | 'md' | 'lg'`
- `className?: string`

#### 2. `Modal.tsx`
**Purpose:** Reusable modal component
**Props:**
- `isOpen: boolean`
- `onClose: () => void`
- `title?: string`
- `children: ReactNode`
- `size?: 'sm' | 'md' | 'lg' | 'xl'`

#### 3. `StatusBadge.tsx`
**Purpose:** Trip status badge with icon
**Props:**
- `status: string`
- `showIcon?: boolean`
- `className?: string`

**Extract from:**
- `app/search/results/page.tsx:550-581`
- `app/trip/[id]/page.tsx:254-258`

#### 4. `ScoreBadge.tsx`
**Purpose:** Match score badge with color coding
**Props:**
- `score: number`
- `thresholds?: { HIGH: number; MID: number }`
- `className?: string`

**Extract from:**
- `app/search/results/page.tsx:536-548`

### Feature Components (`components/features/`)

#### 1. `SelectionBadge.tsx`
**Extract from:** `app/search/page.tsx:116-178`
**Props:**
- `selection: LocationSelection`
- `onRemove: () => void`

#### 2. `TagCircle.tsx`
**Extract from:** `app/search/page.tsx:180-215`
**Props:**
- `tag: SearchTag`
- `isSelected: boolean`
- `onClick: () => void`
- `iconMap: Record<string, LucideIcon>`

#### 3. `DualRangeSlider.tsx`
**Extract from:** `app/search/page.tsx:221-363`
**Props:**
- `min: number`
- `max: number`
- `minValue: number`
- `maxValue: number`
- `step?: number`
- `minGap?: number`
- `onChange: (min: number, max: number) => void`
- `label: string`

#### 4. `TripResultCard.tsx`
**Extract from:** `app/search/results/page.tsx:107-142, 520-628`
**Props:**
- `trip: Trip`
- `matchScore: number`
- `position: number`
- `source: ClickSource`
- `onClick: () => void`
- `scoreThresholds?: ScoreThresholds`

#### 5. `RegistrationModal.tsx`
**Extract from:** `app/trip/[id]/page.tsx:68-112`
**Props:**
- `isOpen: boolean`
- `onClose: () => void`

#### 6. `LogoutConfirmModal.tsx`
**Extract from:** Multiple files (home, search)
**Props:**
- `isOpen: boolean`
- `onConfirm: () => void`
- `onCancel: () => void`

#### 7. `QuickInfoCards.tsx`
**Extract from:** `app/trip/[id]/page.tsx:273-312`
**Props:**
- `trip: Trip`
- `startDate?: string`
- `endDate?: string`
- `duration: number`
- `difficultyLevel?: number`

---

## Hook Extraction Plan

### 1. `hooks/useUser.ts`
**Extract from:**
- `app/page.tsx:17-71`
- `app/search/page.tsx:425-482`

**Implementation:**
```typescript
export function useUser() {
  const [userName, setUserName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Load user logic
  }, []);

  return { userName, isLoading, user };
}
```

### 2. `hooks/useScrollDepth.ts`
**Extract from:** `app/search/results/page.tsx:157-211`

**Implementation:**
```typescript
export function useScrollDepthTracking(
  totalResults: number,
  isLoading: boolean
): void {
  // Existing implementation
}
```

### 3. `hooks/useSearchFilters.ts` (Optional)
**Extract from:** `app/search/page.tsx`
**Purpose:** Centralize filter state management

**Implementation:**
```typescript
export function useSearchFilters() {
  // Filter state and handlers
  return {
    filters,
    updateFilter,
    clearFilters,
    hasActiveFilters,
  };
}
```

---

## Utility Functions to Create (SIMPLIFIED - Single File)

> **Note:** Following pragmatic approach - create single `lib/utils.ts` file instead of multiple files for simplicity.

### `lib/utils.ts` (Single File - All Utilities)

**Complete file content:** (See Priority 5 section above for full implementation)

This single file contains:
- Trip utilities (getTripField, getStatusLabel, getDifficultyLabel, etc.)
- Date utilities (formatDate, calculateDuration, getAvailableMonths, etc.)
- Score utilities (getScoreColor, getScoreBgClass, ScoreThresholds)

**Benefits of single file:**
- Simpler structure (one file instead of three)
- Easier to find utilities (all in one place)
- Less file navigation
- Still organized with comments/sections

---

## File Organization

### Proposed Structure After Refactoring

```
frontend/src/
├── app/                          # Next.js pages (simplified)
│   ├── auth/
│   │   ├── page.tsx             # Auth page (keep as is)
│   │   └── callback/
│   │       └── page.tsx
│   ├── search/
│   │   ├── page.tsx             # Search page (~400-500 lines after refactoring)
│   │   ├── results/
│   │   │   └── page.tsx         # Results page (~300-400 lines after refactoring)
│   │   ├── error.tsx
│   │   └── loading.tsx
│   ├── trip/
│   │   └── [id]/
│   │       └── page.tsx         # Trip detail (~200-300 lines after refactoring)
│   └── page.tsx                 # Home page (keep as is)
│
├── components/
│   ├── features/                 # Feature-specific components
│   │   ├── search/
│   │   │   ├── SelectionBadge.tsx
│   │   │   ├── TagCircle.tsx
│   │   │   └── DualRangeSlider.tsx
│   │   ├── trips/
│   │   │   ├── TripResultCard.tsx
│   │   │   └── QuickInfoCards.tsx
│   │   └── auth/
│   │       └── LogoutConfirmModal.tsx
│   └── ui/                       # Reusable UI components
│       ├── Badge.tsx
│       ├── Modal.tsx
│       ├── StatusBadge.tsx
│       ├── ScoreBadge.tsx
│       └── Button.tsx (if needed)
│
├── hooks/
│   ├── useTracking.ts            # Keep as is
│   ├── useUser.ts                # NEW: User management
│   ├── useScrollDepth.ts         # NEW: Scroll tracking
│   └── useSearchFilters.ts       # NEW: Filter management (optional)
│
├── lib/
│   ├── dataStore.tsx             # Keep as is (could split constants later)
│   ├── supabaseClient.ts         # Keep as is
│   └── utils/                    # NEW: Utility functions
│       ├── tripUtils.ts          # Trip-related utilities
│       ├── dateUtils.ts          # Date formatting utilities
│       └── formatUtils.ts        # General formatting (if needed)
│
└── services/
    ├── api.service.ts             # Keep as is
    └── tracking.service.ts       # Keep as is
```

---

## Implementation Checklist (PRAGMATIC APPROACH)

### Phase 1: Critical Fixes (HIGH PRIORITY - Do These First)

#### Step 1: DataStore Integration
- [ ] Create `lib/utils/tripUtils.ts`
  - [ ] Move `getTripField`
  - [ ] Move `getStatusLabel`
  - [ ] Move `getDifficultyLabel`
  - [ ] Move `getStatusIconUrl`
  - [ ] Move `getStatusIcon`
- [ ] Create `lib/utils/dateUtils.ts`
  - [ ] Move `formatDate`
  - [ ] Move `calculateDuration`
  - [ ] Move `getAvailableMonths`
  - [ ] Move `getAvailableYears`
- [ ] Update all imports in affected files

### Phase 2: Extract Hooks (High Priority)
- [ ] Create `hooks/useUser.ts`
  - [ ] Extract user loading logic
  - [ ] Extract logout logic
- [ ] Create `hooks/useScrollDepth.ts`
  - [ ] Extract scroll depth tracking
- [ ] Update all imports in affected files

### Phase 3: Extract UI Components (Medium Priority)
- [ ] Create `components/ui/StatusBadge.tsx`
- [ ] Create `components/ui/ScoreBadge.tsx`
- [ ] Create `components/ui/Modal.tsx`
- [ ] Create `components/ui/Badge.tsx` (if needed)
- [ ] Update all imports in affected files

### Phase 2: Component Extraction (ONLY Complex Ones - See Priority 4 Above)
- [ ] Update `app/trip/[id]/page.tsx` to use `getTrip()` from `api.service.ts`
- [ ] Remove direct `fetch()` call
- [ ] Test error handling and retry logic

### Phase 5: Testing & Verification
- [ ] Test all pages after refactoring:
  - [ ] Home page loads correctly
  - [ ] Search page loads with DataStore data
  - [ ] Search functionality works
  - [ ] Results page displays correctly
  - [ ] Trip detail page loads with API service
- [ ] Verify no broken imports
- [ ] Verify no duplicate functions (run grep checks)
- [ ] Verify DataStore integration (check Network tab for single API calls)
- [ ] Run TypeScript compiler: `npx tsc --noEmit`
- [ ] Run linter: `npm run lint`
- [ ] Test user flows end-to-end:
  - [ ] User login/logout
  - [ ] Search → Results → Trip Detail
  - [ ] Error handling (stop backend, test error states)

---

## Benefits of Refactoring

1. **Code Reusability**: Components and utilities can be reused across pages
2. **Maintainability**: Easier to find and update code
3. **Testability**: Smaller, focused files are easier to test
4. **Readability**: Pages focus on composition, not implementation
5. **Consistency**: Shared utilities ensure consistent behavior
6. **Performance**: Better code splitting with smaller components
7. **Developer Experience**: Easier onboarding and navigation

---

## Notes

- All refactoring should maintain existing functionality
- Use TypeScript for all new files
- Follow existing code style and patterns
- Update imports carefully to avoid breaking changes
- Test thoroughly after each phase
- Consider creating a shared types file if needed (`lib/types/`)

---

## Manual Verification Guide

### Step-by-step manual checks to ensure integration is performed without duplications and errors

> **Note:** These are manual verification steps only. No automated testing or CI/CD. Run these checks manually after completing each phase to verify everything works correctly.

##### 1.1 Check for Code Duplications
```bash
# Search for duplicate functions
grep -r "getTripField" frontend/src/app --include="*.tsx" --include="*.ts"
grep -r "getStatusLabel" frontend/src/app --include="*.tsx" --include="*.ts"
grep -r "formatDate" frontend/src/app --include="*.tsx" --include="*.ts"
grep -r "calculateDuration" frontend/src/app --include="*.tsx" --include="*.ts"
grep -r "getDifficultyLabel" frontend/src/app --include="*.tsx" --include="*.ts"

# Expected result: Each function should appear only once (in utils file)
```

##### 1.2 Check DataStore Usage
```bash
# Check if DataStoreProvider appears in layout
grep -r "DataStoreProvider" frontend/src/app/layout.tsx

# Check if DataStore hooks are being used
grep -r "useCountries\|useTripTypes\|useThemeTags" frontend/src/app --include="*.tsx"

# Expected before integration: No usage
# Expected after integration: Usage in search/page.tsx
```

##### 1.3 Check API Service Usage
```bash
# Check for direct fetch calls instead of service usage
grep -r "fetch\(.*api/v2" frontend/src/app --include="*.tsx" --include="*.ts"

# Check api.service usage
grep -r "from '@/services/api.service'" frontend/src/app --include="*.tsx"

# Expected result: All API calls through api.service.ts
```

#### After Each Phase: Manual Verification

##### After Step 1 (DataStore Integration)
- [ ] Open browser and navigate to `/search`
- [ ] Check browser console - should have no errors
- [ ] Verify page loads and shows search form
- [ ] Open DevTools > Network tab
- [ ] Verify only 3 API calls: `/api/locations`, `/api/trip-types`, `/api/tags`
- [ ] Verify no duplicate calls (should see each endpoint called once)
- [ ] Test location dropdown - should show countries and continents
- [ ] Test trip type selection - should show trip types
- [ ] Test theme selection - should show theme tags

##### After Step 2 (User Hook)
- [ ] Test home page - should show user name if logged in
- [ ] Test search page - should show user name if logged in
- [ ] Test logout functionality on both pages
- [ ] Verify no console errors related to user loading

##### After Step 3 (API Service Fix)
- [ ] Navigate to a trip detail page (e.g., `/trip/1`)
- [ ] Verify trip details load correctly
- [ ] Check Network tab - should use `/api/v2/trips/1` endpoint
- [ ] Test error handling - try invalid trip ID
- [ ] Verify error message displays correctly

#### Complete Manual Verification Checklist

**Run this checklist after completing all refactoring steps:**

##### DataStore Integration Verification

- [ ] Open browser and navigate to `/search`
- [ ] Check browser console - should have no errors
- [ ] Verify page loads and shows search form
- [ ] Open DevTools > Network tab
- [ ] Verify only 3 API calls: `/api/locations`, `/api/trip-types`, `/api/tags`
- [ ] Verify no duplicate calls (should see each endpoint called once)
- [ ] Test location dropdown - should show countries and continents
- [ ] Test trip type selection - should show trip types
- [ ] Test theme selection - should show theme tags
- [ ] Open `app/search/page.tsx` in editor
- [ ] Search for `fetchCountries` - should NOT exist
- [ ] Search for `fetchTypesAndTags` - should NOT exist
- [ ] Search for `useCountries()` - should exist
- [ ] Search for `useTripTypes()` - should exist
- [ ] Search for `useThemeTags()` - should exist

##### User Hook Verification

- [ ] Test home page - should show user name if logged in
- [ ] Test search page - should show user name if logged in
- [ ] Test logout functionality on both pages
- [ ] Verify no console errors related to user loading
- [ ] Verify `hooks/useUser.ts` exists
- [ ] Open `app/page.tsx` - should import and use `useUser()` hook
- [ ] Open `app/search/page.tsx` - should import and use `useUser()` hook

##### API Service Usage Verification

- [ ] Navigate to a trip detail page (e.g., `/trip/1`)
- [ ] Verify trip details load correctly
- [ ] Check Network tab - should use `/api/v2/trips/1` endpoint
- [ ] Test error handling - try invalid trip ID
- [ ] Verify error message displays correctly
- [ ] Open `app/trip/[id]/page.tsx` in editor
- [ ] Search for `fetch(` - should NOT exist (except in comments)
- [ ] Search for `getTrip` - should be imported from `@/services/api.service`

##### Utilities Verification

- [ ] Verify `lib/utils.ts` exists (single file)
- [ ] Open `app/search/results/page.tsx`
- [ ] Search for `getTripField` - should NOT be defined
- [ ] Verify it's imported from `@/lib/utils`
- [ ] Search for `getStatusLabel` - should NOT be defined
- [ ] Verify it's imported from `@/lib/utils`
- [ ] Open `app/trip/[id]/page.tsx`
- [ ] Search for `formatDate` - should NOT be defined
- [ ] Verify it's imported from `@/lib/utils`
- [ ] Search for `calculateDuration` - should NOT be defined
- [ ] Verify it's imported from `@/lib/utils`

##### Component Extraction Verification (If Completed)

- [ ] Verify `components/features/DualRangeSlider.tsx` exists (if extracted)
- [ ] Verify `components/features/TripResultCard.tsx` exists (if extracted)
- [ ] Verify `components/features/RegistrationModal.tsx` exists (if extracted)
- [ ] Verify `components/features/LogoutConfirmModal.tsx` exists (if extracted)

##### Functional Testing

- [ ] Perform full search (destination + style + dates)
- [ ] Verify results are displayed
- [ ] Click on a trip in results
- [ ] Verify trip detail page loads
- [ ] Verify all information is displayed (dates, price, guide, etc.)
- [ ] Return to search
- [ ] Verify search still works
- [ ] Test user login/logout flow
- [ ] Test error states (stop backend, verify error messages)

##### Code Quality Checks

- [ ] Run TypeScript check: `cd frontend && npx tsc --noEmit`
- [ ] Run linter: `cd frontend && npm run lint`
- [ ] Check for duplicate functions (use grep commands below)
- [ ] Verify no broken imports

#### Manual Verification Scripts (Optional Helpers)

> **Note:** These are simple bash scripts to help with manual verification. They are NOT part of CI/CD - run them manually when needed.

##### Verification Script (Optional Helper)

**File: `scripts/verify-integration.sh`** (Optional - for manual use)

```bash
#!/bin/bash

# Complete verification script for integration

echo "🔍 Starting Integration Verification..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Check 1: DataStore Provider in layout
echo "1. Checking DataStore Provider in layout..."
if grep -q "DataStoreProvider" frontend/src/app/layout.tsx; then
    echo -e "${GREEN}✅ DataStoreProvider found in layout${NC}"
else
    echo -e "${RED}❌ DataStoreProvider NOT found in layout${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 2: DataStore hooks usage in search/page
echo "2. Checking DataStore hooks usage in search page..."
if grep -q "useCountries\|useTripTypes\|useThemeTags" frontend/src/app/search/page.tsx; then
    echo -e "${GREEN}✅ DataStore hooks used in search page${NC}"
else
    echo -e "${RED}❌ DataStore hooks NOT used in search page${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 3: No fetchCountries in search/page
echo "3. Checking for removed fetchCountries function..."
if grep -q "const fetchCountries\|function fetchCountries" frontend/src/app/search/page.tsx; then
    echo -e "${RED}❌ fetchCountries still exists (should be removed)${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ fetchCountries removed${NC}"
fi

# Check 4: getTrip usage instead of direct fetch
echo "4. Checking API service usage in trip detail page..."
if grep -q "getTrip.*from '@/services/api.service'" frontend/src/app/trip/\[id\]/page.tsx; then
    echo -e "${GREEN}✅ getTrip imported from api.service${NC}"
else
    echo -e "${RED}❌ getTrip NOT imported from api.service${NC}"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "fetch.*api/v2/trips" frontend/src/app/trip/\[id\]/page.tsx; then
    echo -e "${RED}❌ Direct fetch still exists (should use getTrip)${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No direct fetch calls${NC}"
fi

# Check 5: Utilities exist (single file approach)
echo "5. Checking utility file..."
if [ -f "frontend/src/lib/utils.ts" ]; then
    echo -e "${GREEN}✅ utils.ts exists${NC}"
else
    echo -e "${RED}❌ utils.ts NOT found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 6: No duplicate functions
echo "6. Checking for duplicate functions..."
DUPLICATES=0

# Check getTripField
COUNT=$(grep -r "function getTripField\|const getTripField" frontend/src/app --include="*.tsx" --include="*.ts" | wc -l)
if [ "$COUNT" -gt 0 ]; then
    echo -e "${RED}❌ getTripField found in app files (should only be in utils)${NC}"
    DUPLICATES=$((DUPLICATES + 1))
fi

# Check getStatusLabel
COUNT=$(grep -r "function getStatusLabel\|const getStatusLabel" frontend/src/app --include="*.tsx" --include="*.ts" | wc -l)
if [ "$COUNT" -gt 0 ]; then
    echo -e "${RED}❌ getStatusLabel found in app files (should only be in utils)${NC}"
    DUPLICATES=$((DUPLICATES + 1))
fi

if [ "$DUPLICATES" -eq 0 ]; then
    echo -e "${GREEN}✅ No duplicate functions found${NC}"
else
    ERRORS=$((ERRORS + DUPLICATES))
fi

# Check 7: Extracted components (only complex ones)
echo "7. Checking extracted components..."
MISSING_COMPONENTS=0

if [ ! -f "frontend/src/components/features/DualRangeSlider.tsx" ]; then
    echo -e "${YELLOW}⚠️  DualRangeSlider not found (optional - Phase 4)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

if [ ! -f "frontend/src/components/features/TripResultCard.tsx" ]; then
    echo -e "${YELLOW}⚠️  TripResultCard not found (optional - Phase 4)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

if [ ! -f "frontend/src/components/features/LogoutConfirmModal.tsx" ]; then
    echo -e "${YELLOW}⚠️  LogoutConfirmModal not found (optional - Phase 4)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo ""
echo "=========================================="
echo "Verification Summary:"
echo "=========================================="
echo -e "Errors: ${RED}${ERRORS}${NC}"
echo -e "Warnings: ${YELLOW}${WARNINGS}${NC}"

if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}✅ All critical checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Please fix the errors above.${NC}"
    exit 1
fi
```

##### TypeScript Check (Manual)

**Command to run manually:**
```bash
cd frontend
npx tsc --noEmit
```

**Expected:** No TypeScript errors

##### Linter Check (Manual)

**Command to run manually:**
```bash
cd frontend
npm run lint
```

**Expected:** No linting errors

---

### Quick Verification Commands

**Run these commands manually after refactoring to verify everything is correct:**

```bash
# 1. Check for duplicate functions (should only find in utils.ts)
grep -r "function getTripField\|const getTripField" frontend/src/app --include="*.tsx" --include="*.ts"
grep -r "function getStatusLabel\|const getStatusLabel" frontend/src/app --include="*.tsx" --include="*.ts"

# 2. Verify DataStore is integrated
grep -r "DataStoreProvider" frontend/src/app/layout.tsx
grep -r "useCountries\|useTripTypes\|useThemeTags" frontend/src/app/search/page.tsx

# 3. Verify API service is used (no direct fetch)
grep -r "fetch.*api/v2/trips" frontend/src/app/trip --include="*.tsx"
grep -r "getTrip.*from '@/services/api.service'" frontend/src/app/trip --include="*.tsx"

# 4. Check TypeScript
cd frontend && npx tsc --noEmit

# 5. Check Linter
cd frontend && npm run lint
```

---

### Manual Browser Testing

After completing all refactoring steps, manually test in browser:

1. **Start the application:**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Test each page:**
   - Home page (`/`)
   - Search page (`/search`)
   - Search results (`/search/results?countries=1`)
   - Trip detail (`/trip/1`)

3. **Verify functionality:**
   - All pages load without errors
   - Data loads correctly (countries, trip types, themes)
   - Search works end-to-end
   - Trip details display correctly
   - User login/logout works
   - Error states display correctly

---

## Additional Analysis: Comprehensive Code Review

### Extended Findings Beyond Initial Analysis

This section provides a comprehensive review of all files to identify additional issues, duplicates, and opportunities for improvement.

#### Files That Should Use DataStore

**Current Status:**
- ✅ **Only `app/search/page.tsx` needs DataStore** - This is correctly identified
- ✅ No other files fetch countries, trip types, or theme tags independently
- ✅ `dataStore.tsx` itself correctly uses internal fetch (as it should)

**Conclusion:** The initial analysis correctly identified that only `search/page.tsx` needs DataStore integration.

---

#### Additional Duplicate Functions Found

##### 1. Date/Time Utility Functions

**Location:** `app/search/page.tsx:77-111`
- `MONTHS_HE` constant (line 77)
- `getAvailableMonths()` function (line 86)
- `getAvailableYears()` function (line 107)

**Status:** 
- ✅ Already identified for extraction to `lib/utils/dateUtils.ts`
- ⚠️ **Note:** These are currently only used in one file, but should still be extracted for reusability

**Recommendation:** Extract to `lib/utils/dateUtils.ts` as planned.

---

##### 2. User Management Logic (DUPLICATE)

**Locations:**
- `app/page.tsx:17-71` (Home page)
- `app/search/page.tsx:425-482` (Search page)

**Duplicated Code:**
```typescript
// Same logic in both files:
const [userName, setUserName] = useState<string | null>(null);
const [isLoadingUser, setIsLoadingUser] = useState(true);

useEffect(() => {
  const loadUser = async () => {
    if (!isAuthAvailable() || !supabase) {
      setIsLoadingUser(false);
      return;
    }
    
    try {
      const user = await getCurrentUser();
      if (user) {
        const metadata = user.user_metadata || {};
        let fullName = null;
        // ... same extraction logic in both files
      }
    } catch (error) {
      // ... same error handling
    }
  };
  
  loadUser();
  // ... same auth state change listener
}, []);
```

**Impact:** ~50 lines duplicated across 2 files

**Recommendation:** 
- ✅ Already identified for extraction to `hooks/useUser.ts`
- **Priority:** HIGH - This is a clear duplication

---

##### 3. Logout Confirmation Logic (DUPLICATE)

**Locations:**
- `app/page.tsx:74-98` (Home page)
- `app/search/page.tsx:485-509` (Search page)

**Duplicated Code:**
```typescript
// Same logic in both files:
const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

const handleLogout = () => {
  setShowLogoutConfirm(true);
};

const confirmLogout = async () => {
  if (!isAuthAvailable() || !supabase) {
    return;
  }
  try {
    await supabase.auth.signOut();
    setUserName(null);
    setShowLogoutConfirm(false);
    router.push('/auth?redirect=/search');
  } catch (error) {
    // ... same error handling
  }
};

const cancelLogout = () => {
  setShowLogoutConfirm(false);
};
```

**Impact:** ~30 lines duplicated + JSX modal code duplicated

**Recommendation:**
- ✅ Already identified for extraction to `components/features/auth/LogoutConfirmModal.tsx`
- ⚠️ **Additional:** Should also extract logout logic to `hooks/useUser.ts` or `hooks/useAuth.ts`

---

##### 4. Score Calculation Functions (NEW FINDING)

**Location:** `app/search/results/page.tsx:29-50`

**Functions:**
- `ScoreThresholds` interface (line 29)
- `getScoreColor()` function (line 35)
- `getScoreBgClass()` function (line 41)

**Status:** 
- ❌ **NOT identified in initial analysis**
- Currently only used in one file, but should be extracted for:
  - Reusability if scores are shown elsewhere
  - Testability
  - Maintainability

**Recommendation:** Extract to `lib/utils/scoreUtils.ts`

**New File to Create:**
```typescript
// lib/utils/scoreUtils.ts

export interface ScoreThresholds {
  HIGH: number;
  MID: number;
}

export function getScoreColor(
  score: number, 
  thresholds: ScoreThresholds
): 'high' | 'mid' | 'low' {
  if (score >= thresholds.HIGH) return 'high';
  if (score >= thresholds.MID) return 'mid';
  return 'low';
}

export function getScoreBgClass(
  colorLevel: 'high' | 'mid' | 'low'
): string {
  switch (colorLevel) {
    case 'high':
      return 'bg-[#12acbe]';  // Turquoise - excellent
    case 'mid':
      return 'bg-[#f59e0b]';  // Orange - medium
    case 'low':
      return 'bg-[#ef4444]';  // Red - low
  }
}
```

---

#### Functions That Should Be Externalized (Not Duplicates, But Should Be Shared)

##### 1. Event Handlers That Could Be Hooks

**Location:** `app/search/page.tsx`

**Functions:**
- `handleClickOutside` (line 684) - Click outside detection
- `addLocation` (line 814) - Location management
- `removeLocation` (line 842) - Location management
- `toggleTheme` (line 847) - Theme selection
- `handleDurationChange` (line 856) - Duration filter
- `handleSearch` (line 862) - Search submission
- `handleClearSearch` (line 920) - Filter clearing

**Status:** These are page-specific handlers, but some could be extracted:
- `handleClickOutside` → Could be `hooks/useClickOutside.ts`
- Location/theme management → Could be `hooks/useSearchFilters.ts`

**Recommendation:** 
- ✅ `useSearchFilters` hook already identified (optional)
- ⚠️ **Additional:** Consider `hooks/useClickOutside.ts` for reusability

---

##### 2. Loading Components

**Locations:**
- `app/search/page.tsx:1431-1451` - `SearchPageLoading`
- `app/search/results/page.tsx:656-676` - `ResultsPageLoading`

**Status:**
- ✅ `SearchPageLoading` already identified for extraction
- ✅ `ResultsPageLoading` already identified for extraction

**Recommendation:** Extract to `components/ui/LoadingSpinner.tsx` or keep as page-specific if they have unique designs.

---

#### Additional Misuses and Issues

##### 1. Direct API URL Construction

**Location:** `app/trip/[id]/page.tsx:153`

**Issue:**
```typescript
const response = await fetch(`${API_URL}/api/v2/trips/${tripId}`);
```

**Problem:**
- Uses direct `fetch()` instead of `getTrip()` from `api.service.ts`
- Missing retry logic
- Missing authentication headers
- Missing error handling consistency

**Status:** ✅ Already identified in initial analysis

---

##### 2. Inline Constants

**Location:** `app/search/page.tsx:77-80`

**Issue:**
```typescript
const MONTHS_HE = [
  'ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני',
  'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר'
];
```

**Status:** Should be moved to `lib/utils/dateUtils.ts` along with `getAvailableMonths()`

---

##### 3. Type Definitions in Page Files

**Locations:**
- `app/search/page.tsx:56-68` - `SearchTag`, `LocationSelection` interfaces
- `app/search/results/page.tsx:22-33` - `SearchResult`, `ScoreThresholds` interfaces

**Recommendation:** 
- Move shared types to `lib/types/` or keep in page files if truly page-specific
- `ScoreThresholds` should move to `lib/utils/scoreUtils.ts` (as identified above)

---

#### Summary of Additional Findings

| Category | Count | Files Affected | Priority |
|----------|-------|----------------|----------|
| **New Duplicates Found** | 2 | page.tsx, search/page.tsx | HIGH |
| - User loading logic | 1 | 2 files | HIGH |
| - Logout logic | 1 | 2 files | HIGH |
| **Functions to Extract** | 3 | results/page.tsx | MEDIUM |
| - Score utilities | 2 | 1 file | MEDIUM |
| - Click outside hook | 1 | 1 file | LOW |
| **Constants to Extract** | 1 | search/page.tsx | MEDIUM |
| - MONTHS_HE | 1 | 1 file | MEDIUM |

---

#### Updated Refactoring Checklist

Add these items to the existing checklist:

##### Phase 1.5: Extract Score Utilities (NEW)
- [ ] Create `lib/utils/scoreUtils.ts`
  - [ ] Move `ScoreThresholds` interface
  - [ ] Move `getScoreColor()` function
  - [ ] Move `getScoreBgClass()` function
- [ ] Update `app/search/results/page.tsx` to import from `scoreUtils.ts`
- [ ] Remove inline score utility functions

##### Phase 2.5: Extract User Hook (ENHANCED)
- [ ] Create `hooks/useUser.ts`
  - [ ] Extract user loading logic from `page.tsx`
  - [ ] Extract user loading logic from `search/page.tsx`
  - [ ] Include logout functionality (or create separate `useAuth.ts`)
- [ ] Update `app/page.tsx` to use `useUser()` hook
- [ ] Update `app/search/page.tsx` to use `useUser()` hook
- [ ] Remove duplicate user loading code

##### Phase 3.5: Extract Logout Logic (ENHANCED)
- [ ] Create `hooks/useAuth.ts` (or add to `useUser.ts`)
  - [ ] Extract logout confirmation logic
  - [ ] Extract logout handlers
- [ ] Update `app/page.tsx` to use logout hook
- [ ] Update `app/search/page.tsx` to use logout hook
- [ ] Remove duplicate logout code

##### Phase 4.5: Extract Additional Utilities (NEW)
- [ ] Move `MONTHS_HE` constant to `lib/utils/dateUtils.ts`
- [ ] Create `hooks/useClickOutside.ts` (optional, for reusability)
- [ ] Consider extracting shared types to `lib/types/`

---

#### Files Requiring Updates

**High Priority:**
1. `app/page.tsx` - Remove user loading + logout duplication
2. `app/search/page.tsx` - Remove user loading + logout duplication, use DataStore
3. `app/trip/[id]/page.tsx` - Use `getTrip()` from service

**Medium Priority:**
4. `app/search/results/page.tsx` - Extract score utilities, extract hook

**Low Priority:**
5. All page files - Consider extracting shared types

---

#### Code Quality Metrics

**Before Refactoring:**
- Duplicate code: ~80 lines (user loading + logout)
- Inline utilities: ~50 lines (score, date functions)
- Functions that should be external: ~15 functions
- Total code that should be extracted: ~130 lines

**After Refactoring:**
- Duplicate code: 0 lines
- Inline utilities: 0 lines (all in utils)
- Functions that should be external: 0 (all extracted)
- Code reduction in page files: ~130 lines
- New reusable utilities: ~200 lines (but shared across files)

**Net Improvement:**
- Better code organization
- Improved reusability
- Easier testing
- Better maintainability

---

## Summary

### Usage Patterns Summary Table

| File | Uses DataStore? | Uses API Service? | Uses Direct Fetch? | Creates Components? | Creates Hooks? | Creates Utilities? | Issues |
|------|----------------|------------------|-------------------|-------------------|---------------|-------------------|--------|
| `layout.tsx` | ❌ No Provider | ❌ N/A | ❌ N/A | ❌ None | ❌ None | ❌ None | Missing DataStoreProvider |
| `page.tsx` (Home) | ❌ No | ❌ No | ❌ No | ⚠️ Logout modal logic | ❌ No | ❌ No | Duplicate user loading |
| `auth/page.tsx` | ❌ No | ❌ No | ❌ No | ❌ None | ❌ No | ❌ No | ✅ Clean |
| `auth/callback/page.tsx` | ❌ No | ❌ No | ❌ No | ❌ None | ❌ No | ❌ No | ✅ Clean |
| `search/page.tsx` | ❌ **NO** (should!) | ✅ Yes | ❌ No | ⚠️ 5 components | ❌ No | ⚠️ 2 functions | **CRITICAL: Duplicates DataStore** |
| `search/results/page.tsx` | ❌ No | ✅ Yes | ❌ No | ⚠️ 2 components | ⚠️ 1 hook | ⚠️ 6 functions | Inline hook, duplicate utils |
| `trip/[id]/page.tsx` | ❌ No | ❌ **NO** | ⚠️ **YES** | ⚠️ 1 component | ❌ No | ⚠️ 5 functions | **CRITICAL: Direct fetch** |
| Error pages | ❌ No | ❌ No | ❌ No | ❌ None | ❌ No | ❌ No | ✅ Clean |

**Legend:**
- ✅ = Correct usage
- ❌ = Not used / Not needed
- ⚠️ = Issue / Should be extracted

---

### Current State Summary

**Critical Issues:**
1. **DataStore NOT integrated** - Provider never added to layout, hooks never used
2. **`search/page.tsx` duplicates DataStore** - Creates own state/fetch instead of using hooks
3. **`trip/[id]/page.tsx` uses direct fetch** - Missing retry logic and error handling
4. **5+ duplicate utility functions** across files
5. **8+ inline components** that should be extracted
6. **1 inline hook** that should be in hooks folder

**File Statistics:**
- 3 large page files (>500 lines each)
- 0 organized UI components (folders empty)
- 1 hook file (useTracking) - but missing useUser, useScrollDepth
- No utility organization (functions scattered)
- DataStore exists (616 lines) but unused

**Target State:**
- DataStore integrated and used by `search/page.tsx`
- All page files < 500 lines
- 0 duplicate functions (all in utilities)
- 10+ reusable UI/feature components
- 4+ organized hook files
- Well-organized utility functions
- All API calls go through services (no direct fetch)

**Estimated Impact:**
- Reduce code duplication by ~40% (including DataStore integration)
- Eliminate duplicate data fetching (~120 lines in search/page.tsx)
- Improve maintainability significantly
- Enable better code reuse
- Faster development for new features
- Consistent error handling and retry logic across all API calls
