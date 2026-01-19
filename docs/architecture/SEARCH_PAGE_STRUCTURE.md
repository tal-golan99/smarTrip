# Search Page Architecture

This document describes the current modular architecture of the search page, which was refactored from a monolithic 1,079-line component into a maintainable, modular structure.

## Overview

The search page (`frontend/src/app/search/page.tsx`) has been refactored from a single 1,079-line file into a clean, modular architecture with:
- **Main page**: ~237 lines (coordination and data fetching)
- **Modular filter sections**: Each filter is a separate, focused component
- **Shared state management**: React Context API for centralized state
- **Headless hooks**: Business logic separated from UI components
- **Reusable UI components**: Stateless components in `components/ui/`

## Current File Structure

```
frontend/src/app/search/
├── page.tsx                          # Main page (237 lines) - coordinator
└── results/
    ├── page.tsx                      # Results page (separate)
    ├── loading.tsx
    └── error.tsx

frontend/src/components/features/search/
├── index.ts                          # Barrel exports
├── SearchPageHeader.tsx              # Header with user info and navigation
├── SearchActions.tsx                 # Search and clear buttons
├── SearchPageLoading.tsx              # Loading state component
├── SearchPageError.tsx                # Error state component
└── filters/
    ├── LocationFilterSection.tsx     # Location search and selection
    ├── LocationDropdown.tsx          # Location dropdown with search
    ├── SelectedLocationsList.tsx     # Selected locations display
    ├── TripTypeFilterSection.tsx     # Trip type selection
    ├── ThemeFilterSection.tsx         # Theme tag selection (max 3)
    ├── DateFilterSection.tsx          # Year/month date filters
    └── RangeFiltersSection.tsx        # Duration, budget, difficulty

frontend/src/contexts/
└── SearchContext.tsx                 # Shared search state (Context API)

frontend/src/hooks/
├── useSearch.ts                      # Hook to access search context
└── useSyncSearchQuery.ts            # URL parameter serialization/deserialization

frontend/src/components/ui/
├── SelectionBadge.tsx                # Reusable badge for selected items
├── TagCircle.tsx                     # Reusable circle for tags/types
├── ClearFiltersButton.tsx            # Clear filters button
└── DualRangeSlider.tsx               # Dual range slider component
```

## Architecture Layers

### 1. Page Layer (`app/search/page.tsx`)

**Responsibilities**:
- Data fetching coordination (countries, trip types, theme tags)
- Error and loading state handling
- Suspense boundary setup
- User authentication state
- Logout modal coordination

**Structure**:
```typescript
SearchPage (default export)
  └── Suspense wrapper
      └── SearchPageContent
          ├── Data fetching hooks (useCountries, useTripTypes)
          ├── Error handling
          └── SearchProvider wrapper
              └── SearchPageContentInner
                  ├── URL synchronization
                  ├── Filter tracking
                  └── UI rendering
```

**Key Features**:
- Uses `useCountries()` and `useTripTypes()` from `lib/dataStore.tsx` for centralized data fetching
- Handles loading states with Suspense fallback
- Provides error recovery with retry functionality
- Wraps content in `SearchProvider` for shared state

### 2. State Management Layer

#### SearchContext (`contexts/SearchContext.tsx`)

**Purpose**: Centralized state management for all search filters using React Context API.

**State Structure**:
```typescript
interface SearchFilters {
  selectedLocations: LocationSelection[];  // Countries and continents
  selectedType: number | null;              // Single trip type
  selectedThemes: number[];                 // Up to 3 theme tags
  selectedYear: string;                     // 'all' or year string
  selectedMonth: string;                    // 'all' or '1'-'12'
  minDuration: number;                      // Default: 5
  maxDuration: number;                      // Default: 30
  maxBudget: number;                        // Default: 15000
  difficulty: number | null;                 // 1-3 or null
}
```

**Actions Provided**:
- `addLocation(location)` - Add country or continent
- `removeLocation(index)` - Remove location by index
- `setTripType(typeId)` - Toggle trip type selection
- `toggleTheme(themeId)` - Toggle theme (max 3)
- `setDate(year, month)` - Set year and month filters
- `setDuration(min, max)` - Set duration range
- `setBudget(budget)` - Set maximum budget
- `setDifficulty(difficulty)` - Toggle difficulty level
- `clearAllFilters()` - Reset to defaults
- `loadFilters(newFilters)` - Load filters from object (for URL sync)
- `executeSearch()` - Navigate to results page with URL params

**Computed Values**:
- `hasActiveFilters` - Boolean indicating if any filters are active

**Special Logic**:
- Antarctica handling: Prevents duplicate selection as both country and continent
- Theme limit: Enforces maximum of 3 selected themes
- Search type classification: Automatically classifies as 'exploration' or 'focused_search' based on filter count

#### useSearch Hook (`hooks/useSearch.ts`)

**Purpose**: Convenience hook to access search context.

**Usage**:
```typescript
const search = useSearch();
// Access: search.filters, search.hasActiveFilters
// Actions: search.addLocation(), search.executeSearch(), etc.
```

**Note**: Must be used within `SearchProvider` component.

### 3. URL Synchronization Layer

#### useSyncSearchQuery (`hooks/useSyncSearchQuery.ts`)

**Purpose**: Handles serialization and deserialization of search filters to/from URL parameters.

**Functions**:
- `serializeFiltersToUrl(filters)` - Convert filters to URLSearchParams
- `loadFiltersFromUrl(searchParams, countries)` - Convert URL params to filters object

**URL Parameter Format**:
```
/search/results?
  countries=1,5,12&
  continents=Asia,Europe&
  type=3&
  themes=10,15,20&
  year=2026&
  month=3&
  minDuration=7&
  maxDuration=14&
  budget=12000&
  difficulty=2
```

**Features**:
- Preserves filter state in URL for shareability
- Supports browser back/forward navigation
- Handles missing or invalid parameters gracefully
- Maps country IDs to country objects using countries array

### 4. Component Layer

#### SearchPageHeader (`components/features/search/SearchPageHeader.tsx`)

**Purpose**: Page header with logo, navigation, and user authentication UI.

**Props**:
```typescript
interface SearchPageHeaderProps {
  userName: string | null;
  isLoadingUser: boolean;
  onLogout: () => void;
}
```

**Features**:
- Logo display
- Navigation buttons (home)
- User greeting (if authenticated)
- Logout button (if authenticated)

#### Filter Sections

All filter sections follow the same pattern:
- Use `useSearch()` hook to access shared state
- No props needed (state comes from context)
- Focused, single-responsibility components

##### LocationFilterSection (`components/features/search/filters/LocationFilterSection.tsx`)

**Purpose**: Location search and selection interface.

**Sub-components**:
- `LocationDropdown` - Searchable dropdown with keyboard navigation
- `SelectedLocationsList` - Display selected locations with remove buttons

**Features**:
- Search input for filtering locations
- Grouped by continent
- Supports both countries and continents
- Prevents duplicate selections
- Special handling for Antarctica

##### TripTypeFilterSection (`components/features/search/filters/TripTypeFilterSection.tsx`)

**Purpose**: Single trip type selection.

**Features**:
- Grid layout of trip type circles
- Single selection (toggles on click)
- Uses `TagCircle` component for display
- Fetches trip types from `useTripTypes()` hook

##### ThemeFilterSection (`components/features/search/filters/ThemeFilterSection.tsx`)

**Purpose**: Multi-select theme tags (max 3).

**Features**:
- Grid layout of theme circles
- Multi-selection with 3-item limit
- Selection counter display
- Uses `TagCircle` component for display
- Fetches themes from `useThemeTags()` hook

##### DateFilterSection (`components/features/search/filters/DateFilterSection.tsx`)

**Purpose**: Year and month date filtering.

**Features**:
- Year dropdown (all years or specific year)
- Month dropdown (filtered by selected year)
- 'All' option for both year and month
- Uses `useSearch()` for state management

##### RangeFiltersSection (`components/features/search/filters/RangeFiltersSection.tsx`)

**Purpose**: Duration, budget, and difficulty filters.

**Sub-components**:
- Duration: Dual range slider (`DualRangeSlider`)
- Budget: Single range slider
- Difficulty: Button group (1-3 or null)

**Features**:
- Duration range: 5-30 days
- Budget range: 0-15000+ (configurable)
- Difficulty: 1 (Easy), 2 (Medium), 3 (Hard), or null (Any)
- All use `useSearch()` for state management

#### SearchActions (`components/features/search/SearchActions.tsx`)

**Purpose**: Search submission and filter clearing actions.

**Props**:
```typescript
interface SearchActionsProps {
  onSearch: () => void;
  onClear: () => void;
  hasActiveFilters: boolean;
  onClearLocationSearch: () => void;
}
```

**Features**:
- "Find My Trip" button (primary action)
- Clear filters button (secondary action)
- Disabled state when no active filters
- Event tracking integration

### 5. UI Components Layer (`components/ui/`)

#### SelectionBadge (`components/ui/SelectionBadge.tsx`)

**Purpose**: Reusable badge for displaying selected items with remove button.

**Props**:
```typescript
interface SelectionBadgeProps {
  selection: LocationSelection;
  onRemove: () => void;
}
```

**Usage**: Used in `SelectedLocationsList` to display selected countries/continents.

#### TagCircle (`components/ui/TagCircle.tsx`)

**Purpose**: Reusable circle component for tags and trip types.

**Props**:
```typescript
interface TagCircleProps {
  icon: React.ComponentType;  // Icon component (not iconMap)
  label: string;
  isSelected: boolean;
  onClick: () => void;
  disabled?: boolean;
}
```

**Usage**: Used in `TripTypeFilterSection` and `ThemeFilterSection`.

**Design Principle**: Accepts icon as React component prop, making it reusable across the app.

#### ClearFiltersButton (`components/ui/ClearFiltersButton.tsx`)

**Purpose**: Reusable button for clearing filters.

**Props**:
```typescript
interface ClearFiltersButtonProps {
  hasActiveFilters: boolean;
  onClick: () => void;
}
```

**Features**:
- Disabled state when no active filters
- Consistent styling across the app

#### DualRangeSlider (`components/ui/DualRangeSlider.tsx`)

**Purpose**: Dual-handle range slider for duration filtering.

**Props**:
```typescript
interface DualRangeSliderProps {
  min: number;
  max: number;
  value: [number, number];
  onChange: (value: [number, number]) => void;
  step?: number;
  labels?: { min: string; max: string };
}
```

**Usage**: Used in `RangeFiltersSection` for duration selection.

## Data Flow

### Initialization Flow

```
1. SearchPage mounts
   ↓
2. Suspense boundary triggers
   ↓
3. SearchPageContent fetches data:
   - useCountries() → API call to /api/locations
   - useTripTypes() → API call to /api/trip-types
   ↓
4. Data loaded → SearchProvider wraps content
   ↓
5. SearchPageContentInner:
   - Reads URL params (if present)
   - Loads filters from URL using useSyncSearchQuery
   - Initializes search state
   ↓
6. Filter components render with shared state
```

### User Interaction Flow

```
1. User interacts with filter (e.g., selects trip type)
   ↓
2. Filter component calls search.setTripType(typeId)
   ↓
3. SearchContext updates state
   ↓
4. All components re-render with new state
   ↓
5. URL sync hook tracks changes (optional, for future enhancement)
```

### Search Submission Flow

```
1. User clicks "Find My Trip" button
   ↓
2. SearchActions calls search.executeSearch()
   ↓
3. SearchContext:
   - Serializes filters to URL params
   - Tracks search submission event
   - Classifies search type (exploration vs focused_search)
   - Flushes pending events
   ↓
4. Navigation to /search/results?params...
   ↓
5. Results page reads URL params and makes API request
```

## Key Design Principles

### 1. Separation of Concerns

- **State Management**: Centralized in `SearchContext`
- **Business Logic**: In context actions and hooks
- **UI Components**: Stateless, receive data via props or hooks
- **Data Fetching**: Centralized in `lib/dataStore.tsx`

### 2. Single Responsibility

Each component has one clear purpose:
- `LocationFilterSection` - Only handles location selection
- `TripTypeFilterSection` - Only handles trip type selection
- `SearchActions` - Only handles search submission

### 3. Reusability

- UI components (`TagCircle`, `SelectionBadge`) are reusable across the app
- Hooks (`useSearch`, `useSyncSearchQuery`) can be used in other pages
- Filter sections are self-contained and could be reused elsewhere

### 4. Testability

- Components are small and focused (easier to test)
- Business logic separated from UI (can test independently)
- Hooks can be tested in isolation
- Context can be tested with mock providers

### 5. Maintainability

- Clear file structure (easy to find components)
- Consistent patterns across filter sections
- TypeScript types for type safety
- Barrel exports for clean imports

## Performance Considerations

### Code Splitting

- Each filter section is a separate component (can be lazy-loaded if needed)
- UI components are small and focused (minimal bundle impact)

### State Management

- Context API provides efficient re-renders (only components using context re-render)
- Memoized computed values (`hasActiveFilters`)
- Stable function references using `useCallback`

### Data Fetching

- Centralized data store prevents duplicate API calls
- Caching in React context (data persists across navigation)
- Error recovery with retry functionality

## Event Tracking Integration

The search page integrates with the event tracking system:

- **Page View**: Tracked via `usePageView('search')` hook
- **Filter Changes**: Tracked via `useFilterTracking()` hook
- **Search Submission**: Tracked in `executeSearch()` with search type classification
- **Event Batching**: Events are batched and sent efficiently

## Future Enhancements

### Potential Improvements

1. **URL Sync Enhancement**: Automatically sync URL params as filters change (currently only on search)
2. **Filter Presets**: Save and load common filter combinations
3. **Advanced Filters**: Add more filter options (guide selection, company selection)
4. **Filter Validation**: Client-side validation before search submission
5. **Accessibility**: Enhanced keyboard navigation and screen reader support
6. **Mobile Optimization**: Optimized layouts for mobile devices

### Migration Notes

If migrating from the old monolithic structure:

1. All filter state is now in `SearchContext` (not local component state)
2. URL params are handled by `useSyncSearchQuery` hook
3. Data fetching uses centralized `dataStore` hooks
4. Components are smaller and more focused
5. Event tracking is integrated at the context level

## Related Documentation

- [Frontend Architecture Overview](../architecture/FRONTEND_ARCHITECTURE.md)
- [Data Pipelines](../architecture/DATA_PIPELINES.md)
- [Search Page Refactor Proposal](../implemented/SEARCH_PAGE_REFACTOR_PROPOSAL.md)
- [API Structure](../api/API_STRUCTURE.md)
