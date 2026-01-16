# Frontend Architecture - SmartTrip

**Last Updated:** January 2026  
**Status:** Current Implementation

---

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Architecture Patterns](#architecture-patterns)
5. [Search Page Architecture](#search-page-architecture)
6. [State Management](#state-management)
7. [API Layer](#api-layer)
8. [Component Design](#component-design)
9. [Routing](#routing)
10. [Performance](#performance)
11. [Best Practices](#best-practices)

---

## Overview

The SmartTrip frontend is a modern, type-safe React application built with Next.js 14, featuring a fully refactored modular architecture with React Context for state management, Zod validation for runtime type safety, and a structured API layer mirroring the backend blueprint organization.

### Key Characteristics

- **Modular Architecture** - Component-based design with clear separation of concerns
- **Type Safety** - TypeScript + Zod for compile-time and runtime type checking
- **State Management** - React Context API for shared state
- **API Layer** - Structured client mirroring backend organization
- **Bilingual** - Full Hebrew and English support
- **Responsive** - Mobile-first design with Tailwind CSS

---

## Technology Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14 | React framework with App Router |
| React | 18 | UI library with Context API |
| TypeScript | 5 | Type safety |
| Tailwind CSS | 3.4 | Utility-first styling |
| Zod | 3.22 | Runtime schema validation |
| Lucide React | Latest | Icon library |
| Supabase | Latest | Authentication and database client |

### Development Tools

- **ESLint** - Code quality and linting
- **PostCSS** - CSS processing
- **tsx** - TypeScript execution for scripts

---

## Project Structure

```
frontend/src/
├── app/                        # Next.js App Router pages
│   ├── layout.tsx             # Root layout
│   ├── page.tsx               # Home page
│   ├── auth/                  # Authentication pages
│   ├── search/                # Search functionality
│   │   ├── page.tsx           # Search page (162 lines)
│   │   └── results/           # Search results page
│   └── trip/[id]/            # Trip detail pages
│
├── api/                       # API client layer
│   ├── client.ts              # Core utilities
│   ├── types.ts               # TypeScript types
│   ├── system.ts              # System API
│   ├── resources.ts           # Resources API
│   ├── events.ts              # Events API
│   └── v2.ts                  # V2 API
│
├── schemas/                   # Zod validation schemas
│   ├── base.ts                # Base schemas
│   ├── resources.ts           # Resource schemas
│   ├── trip.ts                # Trip schemas
│   ├── events.ts              # Event schemas
│   └── analytics.ts           # Analytics schemas
│
├── components/                # React components
│   ├── features/             # Feature components
│   │   ├── search/           # Search page components
│   │   │   ├── filters/      # Filter sections
│   │   │   ├── SearchPageHeader.tsx
│   │   │   ├── SearchActions.tsx
│   │   │   └── index.ts      # Barrel exports
│   │   ├── TripResultCard.tsx
│   │   ├── RegistrationModal.tsx
│   │   └── LogoutConfirmModal.tsx
│   └── ui/                   # Reusable UI components
│       ├── DualRangeSlider.tsx
│       ├── SelectionBadge.tsx
│       ├── TagCircle.tsx
│       └── ClearFiltersButton.tsx
│
├── contexts/                  # React Context providers
│   └── SearchContext.tsx     # Search state management
│
├── hooks/                     # Custom React hooks
│   ├── useSearch.ts          # Search state hook
│   ├── useSyncSearchQuery.ts # URL sync hook
│   ├── useTracking.ts        # Tracking hooks
│   └── useUser.ts            # User state hook
│
├── lib/                       # Utilities and state
│   ├── dataStore.tsx         # Data store context
│   ├── supabaseClient.ts     # Supabase client
│   └── utils.ts              # Utility functions
│
└── services/                  # Service layer
    └── tracking.service.ts   # Tracking service
```

---

## Architecture Patterns

### 1. Layered Architecture

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│     (Pages, Components, Hooks)      │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│         State Management            │
│      (React Context, Hooks)         │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│          Service Layer              │
│    (Business Logic, Orchestration)  │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│           API Layer                 │
│   (HTTP Client, Validation, Types)  │
└─────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────┐
│         Backend API                 │
│      (Flask REST API)               │
└─────────────────────────────────────┘
```

### 2. Component Hierarchy

```
App Layout
├── DataStoreProvider (Reference data)
├── SearchProvider (Search state)
└── Pages
    ├── Home
    ├── Auth
    ├── Search
    │   ├── SearchPageHeader
    │   ├── Filter Sections
    │   │   ├── LocationFilterSection
    │   │   ├── TripTypeFilterSection
    │   │   ├── ThemeFilterSection
    │   │   ├── DateFilterSection
    │   │   └── RangeFiltersSection
    │   └── SearchActions
    ├── Results
    │   └── TripResultCard (multiple)
    └── Trip Detail
```

### 3. Data Flow

```
User Action
    ↓
Component Event Handler
    ↓
Context Action (via useSearch)
    ↓
Context State Update
    ↓
Component Re-render (via useSearch)
    ↓
URL Update (via useSyncSearchQuery)
```

---

## Search Page Architecture

### Overview

The search page was refactored from a monolithic 1,079-line component to a modular architecture with 162-line main page and focused, reusable components.

### Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│                   SearchPage                         │
│              (Suspense Wrapper)                      │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│                SearchProvider                        │
│         (React Context - Shared State)               │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│              SearchPageContent                       │
│           (Main Component - 162 lines)               │
└──────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────┴───────────────┐
        ↓                               ↓
┌─────────────────┐         ┌─────────────────┐
│ SearchPageHeader│         │  Filter Sections│
└─────────────────┘         └─────────────────┘
                                      ↓
                    ┌─────────────────┼─────────────────┐
                    ↓                 ↓                 ↓
            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │   Location   │  │  Trip Type   │  │    Theme     │
            │    Filter    │  │    Filter    │  │    Filter    │
            └──────────────┘  └──────────────┘  └──────────────┘
                    ↓                 ↓                 ↓
            ┌──────────────┐  ┌──────────────┐
            │     Date     │  │    Ranges    │
            │    Filter    │  │    Filter    │
            └──────────────┘  └──────────────┘
                                      ↓
                            ┌─────────────────┐
                            │  SearchActions  │
                            └─────────────────┘
```

### Component Breakdown

#### Main Page (`app/search/page.tsx`)
- **Lines:** 162 (down from 1,079)
- **Responsibilities:**
  - Suspense wrapper for loading states
  - Wraps content with `SearchProvider`
  - Minimal logic

#### Search Context (`contexts/SearchContext.tsx`)
- **Responsibilities:**
  - Centralized state management
  - Filter state (locations, types, themes, dates, ranges)
  - Actions (add/remove locations, toggle themes, execute search)
  - Computed values (hasActiveFilters)
  - URL navigation

#### Search Hook (`hooks/useSearch.ts`)
- **Responsibilities:**
  - Provides access to shared search state
  - Re-exports types for convenience
  - Components pull state instead of receiving props

#### Filter Sections

**LocationFilterSection** (137 lines)
- Container for location search
- Sub-components:
  - `LocationDropdown` (104 lines) - Complex dropdown logic
  - `SelectedLocationsList` (31 lines) - Display selected locations

**TripTypeFilterSection** (68 lines)
- Trip type selection with icons
- Single selection logic

**ThemeFilterSection** (59 lines)
- Theme tag selection with icons
- Multi-selection (max 3)

**DateFilterSection** (79 lines)
- Year and month selection
- Dependent dropdowns (months filtered by year)

**RangeFiltersSection** (101 lines)
- Duration dual range slider
- Budget single range slider
- Difficulty button selection

#### Other Components

**SearchPageHeader**
- Logo and navigation
- User greeting
- Logout functionality

**SearchActions**
- Search button
- Clear filters button

**SearchPageLoading**
- Loading state display

**SearchPageError**
- Error state with retry option

### State Management

#### React Context Pattern

```typescript
// SearchContext.tsx
export function SearchProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [filters, setFilters] = useState<SearchFilters>(DEFAULT_FILTERS);
  
  // Actions
  const addLocation = useCallback((location: LocationSelection) => {
    // ... implementation
  }, [filters]);
  
  const executeSearch = useCallback(() => {
    const params = new URLSearchParams();
    // ... build params from filters
    router.push(`/search/results?${params.toString()}`);
  }, [filters, router]);
  
  // ... more actions
  
  const value = useMemo(() => ({
    filters,
    addLocation,
    removeLocation,
    setTripType,
    toggleTheme,
    setDate,
    setDuration,
    setBudget,
    setDifficulty,
    clearAllFilters,
    executeSearch,
    hasActiveFilters,
  }), [/* dependencies */]);
  
  return (
    <SearchContext.Provider value={value}>
      {children}
    </SearchContext.Provider>
  );
}

// useSearch.ts
export function useSearch() {
  return useSearchContext();
}
```

#### Component Usage

```typescript
// Filter component
function LocationFilterSection() {
  const search = useSearch(); // Access shared state
  
  return (
    <div>
      <input
        value={search.filters.locationSearch}
        onChange={(e) => search.setLocationSearch(e.target.value)}
      />
      {search.filters.selectedLocations.map((loc, index) => (
        <SelectionBadge
          key={index}
          selection={loc}
          onRemove={() => search.removeLocation(index)}
        />
      ))}
    </div>
  );
}
```

### Benefits of Refactoring

**Before:**
- 1,079 lines in single file
- Mixed concerns
- Prop drilling
- Difficult to maintain
- Hard to test

**After:**
- 162-line main page
- Clear separation of concerns
- No prop drilling (Context API)
- Easy to maintain
- Testable components

---

## State Management

### React Context API

The application uses React Context for shared state management:

#### SearchContext
- **Purpose:** Manage search filters and actions
- **Location:** `contexts/SearchContext.tsx`
- **Usage:** Wrap search page with `SearchProvider`, access via `useSearch()`

#### DataStoreContext
- **Purpose:** Manage reference data (countries, trip types, theme tags)
- **Location:** `lib/dataStore.tsx`
- **Usage:** Wrap app with `DataStoreProvider`, access via `useCountries()`, `useTripTypes()`, `useThemeTags()`

### Custom Hooks

#### useSearch
- **Purpose:** Access search state and actions
- **Returns:** Filters, actions, computed values
- **Pattern:** Headless hook (logic separated from UI)

#### useSyncSearchQuery
- **Purpose:** Synchronize filters with URL parameters
- **Returns:** Load/serialize functions
- **Pattern:** URL state management

#### useTracking
- **Purpose:** Event tracking (page views, clicks, impressions)
- **Returns:** Tracking functions
- **Pattern:** Side effect hook

#### useUser
- **Purpose:** User authentication state
- **Returns:** User name, loading state
- **Pattern:** Authentication hook

### State Flow

```
User Interaction
    ↓
Component calls Context action (via useSearch)
    ↓
Context updates state
    ↓
All components using useSearch re-render
    ↓
URL updates (via useSyncSearchQuery)
```

---

## API Layer

### Structure

The API layer mirrors the backend blueprint organization:

```
src/api/
├── client.ts       # Core utilities (apiFetch, validateResponse)
├── types.ts        # TypeScript type definitions
├── system.ts       # System API (health check)
├── resources.ts    # Resources API (countries, guides, tags)
├── events.ts       # Events API (tracking, sessions)
└── v2.ts           # V2 API (recommendations, trips)
```

### Core Utilities (`client.ts`)

```typescript
// apiFetch - Core HTTP client
export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {},
  schema?: z.ZodSchema<T>
): Promise<T> {
  // 1. Build request
  // 2. Execute fetch
  // 3. Handle errors
  // 4. Validate response with Zod
  // 5. Developer logging
  // 6. Return typed data
}

// validateResponse - Zod validation
function validateResponse<T>(
  data: unknown,
  schema: z.ZodSchema<T>,
  endpoint: string
): T {
  // Validate and log errors in development
}
```

### Zod Validation

All API responses are validated at runtime:

```typescript
// schemas/trip.ts
export const TripOccurrenceSchema = z.object({
  id: z.number(),
  title: z.string(),
  startDate: z.string(),
  endDate: z.string(),
  price: z.number(),
  matchScore: z.number().optional(),
  // ... more fields
});

// api/v2.ts
export async function getRecommendations(
  preferences: RecommendationRequest
): Promise<RecommendationResponse> {
  return apiFetch(
    '/api/v2/recommendations',
    {
      method: 'POST',
      body: JSON.stringify(preferences),
    },
    RecommendationResponseSchema // Zod validation
  );
}
```

### Type Safety

Types are inferred from Zod schemas:

```typescript
// schemas/trip.ts
export const TripOccurrenceSchema = z.object({
  id: z.number(),
  title: z.string(),
  // ...
});

// api/types.ts
export type TripOccurrence = z.infer<typeof TripOccurrenceSchema>;
```

### Developer Logging

In development mode, all API calls are logged:

```
[API] POST /api/v2/recommendations
[API] Response: { success: true, count: 10, ... }
[API] Validation: ✓ Passed
```

---

## Component Design

### Component Categories

#### 1. Pages (`app/`)
- Route-based components
- Minimal logic
- Compose feature components
- Handle loading/error states

#### 2. Feature Components (`components/features/`)
- Domain-specific components
- Business logic
- Use hooks and contexts
- Examples: `TripResultCard`, `SearchPageHeader`

#### 3. UI Components (`components/ui/`)
- Reusable, stateless components
- No business logic
- Generic and composable
- Examples: `DualRangeSlider`, `SelectionBadge`

### Design Principles

#### Single Responsibility
Each component has one clear purpose:
- `LocationFilterSection` - Handles location search
- `TripTypeFilterSection` - Handles trip type selection
- `SearchActions` - Handles search and clear actions

#### Composition
Build complex UIs from simple components:
```typescript
<SearchPageContent>
  <SearchPageHeader />
  <LocationFilterSection />
  <TripTypeFilterSection />
  <ThemeFilterSection />
  <DateFilterSection />
  <RangeFiltersSection />
  <SearchActions />
</SearchPageContent>
```

#### Stateless UI
UI components should be stateless when possible:
```typescript
// Good - Stateless
function SelectionBadge({ selection, onRemove }: Props) {
  return (
    <div>
      <span>{selection.nameHe}</span>
      <button onClick={onRemove}>×</button>
    </div>
  );
}

// Bad - Stateful
function SelectionBadge({ selection }: Props) {
  const [isHovered, setIsHovered] = useState(false);
  // ... unnecessary state
}
```

#### Headless Hooks
Separate logic from presentation:
```typescript
// Hook - Logic only
function useSearch() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  // ... logic
  return { filters, actions };
}

// Component - Presentation only
function SearchForm() {
  const search = useSearch();
  return <form>{/* UI */}</form>;
}
```

---

## Routing

### Next.js App Router

The application uses Next.js 14 App Router with file-based routing:

```
app/
├── page.tsx                 # / (Home)
├── auth/
│   ├── page.tsx            # /auth (Login)
│   └── callback/
│       └── page.tsx        # /auth/callback (OAuth callback)
├── search/
│   ├── page.tsx            # /search (Search form)
│   └── results/
│       └── page.tsx        # /search/results (Results)
└── trip/
    └── [id]/
        └── page.tsx        # /trip/:id (Trip detail)
```

### URL State Management

Search parameters are preserved in URL for shareability:

```
/search/results?
  countries=1,5&
  continents=Asia,Europe&
  type=3&
  themes=10,15&
  minDuration=7&
  maxDuration=14&
  budget=12000&
  difficulty=2&
  year=2026&
  month=3
```

### Navigation

```typescript
// Programmatic navigation
const router = useRouter();
router.push('/search/results?countries=1,5');

// Link component
<Link href="/search">Search</Link>
```

---

## Performance

### Optimizations

#### Code Splitting
- Automatic via Next.js
- Dynamic imports for heavy components
- Route-based splitting

#### Image Optimization
- Next.js Image component
- Automatic resizing and optimization
- Lazy loading

#### Event Batching
- Batch tracking events (10 events or 5 seconds)
- Reduces API calls
- Improves performance

#### Modular Architecture
- Smaller, focused components
- Better code splitting
- Faster initial load

### Bundle Size

- Main bundle: Optimized via Next.js
- Component bundles: Split by route
- Vendor bundles: Separated automatically

---

## Best Practices

### Code Style

- **TypeScript strict mode** - Enabled for type safety
- **ESLint** - Code quality and consistency
- **No ternary operators** - Use if-else statements for clarity
- **Functional components** - Use hooks instead of classes

### File Organization

- **Barrel exports** - Use `index.ts` for clean imports
- **Colocation** - Keep related files together
- **Naming conventions** - PascalCase for components, camelCase for hooks

### State Management

- **Context for shared state** - Use React Context for cross-component state
- **Local state for UI** - Use useState for component-specific state
- **URL for shareable state** - Use URL parameters for shareable state

### Component Design

- **Single Responsibility** - Each component has one purpose
- **Composition** - Build complex UIs from simple components
- **Stateless UI** - Separate logic from presentation
- **Headless hooks** - Reusable logic without UI

### API Integration

- **Type safety** - Use Zod for runtime validation
- **Error handling** - Consistent error handling across all endpoints
- **Developer logging** - Detailed logging in development mode
- **Retry logic** - Automatic retries for transient failures

---

## Testing

### Structure Testing

```bash
npm run test:search
```

Validates:
- File existence
- Component usage
- Import correctness
- File size constraints

### Manual Testing

Test flows:
1. Search flow (filters → search → results)
2. URL synchronization (back button, direct URL)
3. Authentication (login, logout)
4. Error handling (network errors, invalid data)

---

## Future Enhancements

### Potential Improvements

1. **Unit Tests** - Add Jest/React Testing Library
2. **E2E Tests** - Add Playwright/Cypress
3. **Storybook** - Component documentation
4. **Performance Monitoring** - Add analytics
5. **Accessibility** - WCAG compliance
6. **Dark Mode** - Theme support
7. **Internationalization** - i18n support
8. **Progressive Web App** - Offline support

---

## Conclusion

The SmartTrip frontend demonstrates modern React architecture with:

- **Modular Design** - Clear separation of concerns
- **Type Safety** - TypeScript + Zod validation
- **State Management** - React Context API
- **API Layer** - Structured, type-safe client
- **Performance** - Optimized bundle and code splitting
- **Maintainability** - Clean, testable code

The refactored search page (from 1,079 to 162 lines) exemplifies these principles, providing a maintainable, scalable foundation for future development.

---

**Document Version:** 1.0  
**Last Updated:** January 2026  
**Status:** Current Implementation
