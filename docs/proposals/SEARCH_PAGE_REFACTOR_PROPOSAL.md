# Search Page Refactoring Proposal

## Executive Summary

The `frontend/src/app/search/page.tsx` file currently contains **1,079 lines** of code, violating the Single Responsibility Principle and making the codebase difficult to maintain, test, and extend. This proposal outlines a structured approach to split this monolithic component into smaller, focused, and reusable components.

## Current State Analysis

### File Structure
- **Search Page**: `frontend/src/app/search/page.tsx` - **1,079 lines**
- **Results Page**: `frontend/src/app/search/results/page.tsx` - **700 lines** (separate page)
- **Main Component**: `SearchPageContent` (~850 lines within search page)
- **Sub-components**: `SelectionBadge`, `TagCircle` (still inline in search page)
- **Wrapper**: `SearchPage` with Suspense
- **Loading Component**: `SearchPageLoading` (inline)

### Already Extracted Components
The following components have been successfully extracted:
- ✅ `DualRangeSlider` → `components/features/DualRangeSlider.tsx`
- ✅ `LogoutConfirmModal` → `components/features/LogoutConfirmModal.tsx`
- ✅ `TripResultCard` → `components/features/TripResultCard.tsx`

### Current Issues

1. **Mixed Concerns**: UI components, business logic, state management, and side effects are all in one file
2. **Difficult Testing**: Large component makes unit testing challenging
3. **Poor Reusability**: Components like `SelectionBadge` and `TagCircle` cannot be reused elsewhere
4. **Maintenance Burden**: Changes require navigating a 1,000+ line file
5. **Performance**: Large component may impact bundle size and code splitting
6. **Code Review**: Difficult to review changes in such a large file
7. **Filter Sections Not Extracted**: All filter sections (location, trip type, themes, date, ranges) are still inline

### Responsibilities Identified

The current component handles:
- Header with navigation and user authentication
- Location search with dropdown and selection
- Trip type selection
- Theme tag selection (up to 3)
- Date filtering (year/month)
- Range filters (duration, budget, difficulty)
- Search submission and URL parameter handling
- State synchronization with URL params
- Loading and error states
- Data fetching coordination

### Current Architecture Notes

**Data Fetching**: The search page now uses centralized data hooks from `lib/dataStore.tsx`:
- `useCountries()` - Fetches and caches countries
- `useTripTypes()` - Fetches and caches trip types
- `useThemeTags()` - Fetches and caches theme tags
- `useDataStore()` - Provides refresh functionality

This centralized approach eliminates duplicate API calls and provides consistent data across the application. The refactoring should preserve this pattern.

## Proposed Architecture

### Component Hierarchy

```
SearchPage (page.tsx - coordinator)
├── SearchProvider (Context API - optional, or useSearch hook)
├── SearchPageHeader (components/features/search/)
├── SearchPageContent (components/features/search/)
│   ├── LocationFilterSection (components/features/search/filters/)
│   │   ├── LocationSearchInput
│   │   ├── LocationDropdown (separate component for complex logic)
│   │   └── SelectedLocationsList
│   ├── TripTypeFilterSection (components/features/search/filters/)
│   ├── ThemeFilterSection (components/features/search/filters/)
│   ├── DateFilterSection (components/features/search/filters/)
│   ├── RangeFiltersSection (components/features/search/filters/)
│   │   ├── DurationRangeFilter
│   │   ├── BudgetRangeFilter
│   │   └── DifficultyFilter
│   └── SearchActions (components/features/search/)
├── SearchPageLoading (components/features/search/)
└── SearchPageError (components/features/search/)
```

### Core Hooks (Required - Phase 1)

```
hooks/
├── useSearch.ts (headless hook - "the brain")
├── useSyncSearchQuery.ts (URL param serialization/deserialization)
└── useSearchFilters.ts (alternative to Context API)
```

### UI Components (extract to components/ui/)

**Design Principle**: UI components must be **stateless and reusable**. They should not know about business logic or data structures.

```
components/ui/
├── SelectionBadge.tsx (stateless - takes selection object)
├── TagCircle.tsx (stateless - takes icon prop, not iconMap)
└── ClearFiltersButton.tsx (stateless - takes onClick handler)
```

**Key Change**: `TagCircle` should accept an `icon` prop (React component) rather than `iconMap`. This makes it reusable across the app (User Profile, Trip Detail, etc.).

## Detailed Component Breakdown

### 1. Search Page Header
**Location**: `components/features/search/SearchPageHeader.tsx`

**Responsibilities**:
- Display logo
- Navigation buttons (home, logout)
- User greeting
- Logout confirmation modal integration

**Props**:
```typescript
interface SearchPageHeaderProps {
  userName: string | null;
  isLoadingUser: boolean;
  onLogout: () => void;
  onNavigateHome: () => void;
}
```

**Lines**: ~80 lines (reduced from ~100 in original)

---

### 2. Location Filter Section
**Location**: `components/features/search/filters/LocationFilterSection.tsx`

**Responsibilities**:
- Location search input
- Selected locations display
- Coordinates LocationDropdown and SelectedLocationsList

**Props** (minimal - uses useSearch hook):
```typescript
interface LocationFilterSectionProps {
  // Minimal props - pulls state from useSearch hook
}
```

**Sub-components** (separate for better maintainability):
- `LocationDropdown.tsx` (~120 lines) - Complex dropdown with keyboard navigation, click-outside logic
- `SelectedLocationsList.tsx` (~40 lines) - Simple display component using SelectionBadge

**Dependencies**:
- `useSearch()` hook for state management
- `SelectionBadge` (from components/ui/)
- `LocationDropdown` (separate component)

**Lines**: ~60 lines (container) + ~120 lines (dropdown) + ~40 lines (list) = ~220 lines total

---

### 3. Trip Type Filter Section
**Location**: `components/features/search/filters/TripTypeFilterSection.tsx`

**Responsibilities**:
- Display trip types as selectable circles
- Handle single selection
- Display custom trip link

**Props**:
```typescript
interface TripTypeFilterSectionProps {
  tripTypes: SearchTag[];
  selectedType: number | null;
  isLoading: boolean;
  onTypeSelect: (typeId: number | null) => void;
  iconMap: Record<string, any>;
}
```

**Lines**: ~80 lines

---

### 4. Theme Filter Section
**Location**: `components/features/search/filters/ThemeFilterSection.tsx`

**Responsibilities**:
- Display theme tags as selectable circles
- Handle multi-selection (max 3)
- Display selection counter

**Props**:
```typescript
interface ThemeFilterSectionProps {
  themes: SearchTag[];
  selectedThemes: number[];
  isLoading: boolean;
  onThemeToggle: (themeId: number) => void;
  iconMap: Record<string, any>;
}
```

**Lines**: ~70 lines

---

### 5. Date Filter Section
**Location**: `components/features/search/filters/DateFilterSection.tsx`

**Responsibilities**:
- Year selection dropdown
- Month selection dropdown (filtered by year)
- Handle year/month changes

**Props**:
```typescript
interface DateFilterSectionProps {
  selectedYear: string;
  selectedMonth: string;
  availableYears: string[];
  availableMonths: Array<{ index: number; name: string }>;
  onYearChange: (year: string) => void;
  onMonthChange: (month: string) => void;
}
```

**Lines**: ~70 lines

---

### 6. Range Filters Section
**Location**: `components/features/search/filters/RangeFiltersSection.tsx`

**Responsibilities**:
- Container for all range-based filters
- Duration dual range slider
- Budget single range slider
- Difficulty buttons

**Props**:
```typescript
interface RangeFiltersSectionProps {
  minDuration: number;
  maxDuration: number;
  maxBudget: number;
  difficulty: number | null;
  onDurationChange: (min: number, max: number) => void;
  onBudgetChange: (budget: number) => void;
  onDifficultyChange: (difficulty: number | null) => void;
}
```

**Sub-components** (optional extraction):
- `DurationRangeFilter.tsx` (~40 lines)
- `BudgetRangeFilter.tsx` (~50 lines)
- `DifficultyFilter.tsx` (~40 lines)

**Lines**: ~150 lines (if sub-components are inline) or ~30 lines (if extracted)

---

### 7. Search Actions
**Location**: `components/features/search/SearchActions.tsx`

**Responsibilities**:
- Search button
- Clear filters button
- Handle search submission
- Handle clear action

**Props**:
```typescript
interface SearchActionsProps {
  hasActiveFilters: boolean;
  onSearch: () => void;
  onClear: () => void;
}
```

**Lines**: ~50 lines

---

### 8. UI Components

#### SelectionBadge
**Location**: `components/ui/SelectionBadge.tsx`

**Extracted from**: Inline component in page.tsx

**Props**:
```typescript
interface SelectionBadgeProps {
  selection: LocationSelection;
  onRemove: () => void;
}
```

**Lines**: ~60 lines

---

#### TagCircle
**Location**: `components/ui/TagCircle.tsx`

**Extracted from**: Inline component in page.tsx

**Design Principle**: Stateless and reusable. Does not know about iconMap or business logic.

**Props**:
```typescript
interface TagCircleProps {
  label: string;
  isSelected: boolean;
  onClick: () => void;
  icon: React.ComponentType<{ className?: string }>; // Icon component, not iconMap
  className?: string;
}
```

**Usage Example**:
```typescript
<TagCircle
  label={tag.nameHe}
  isSelected={selectedThemes.includes(tag.id)}
  onClick={() => toggleTheme(tag.id)}
  icon={THEME_TAG_ICONS[tag.name] || Compass}
/>
```

**Lines**: ~40 lines

---

#### ClearFiltersButton
**Location**: `components/ui/ClearFiltersButton.tsx`

**New component** to standardize clear button behavior

**Props**:
```typescript
interface ClearFiltersButtonProps {
  hasActiveFilters: boolean;
  onClick: () => void;
  className?: string;
}
```

**Lines**: ~30 lines

---

### 9. Core Hooks (Required - Phase 1)

#### useSearch (Headless Hook - "The Brain")
**Location**: `hooks/useSearch.ts`

**Purpose**: Centralize all search business logic. Components "pull" state rather than "receive" it via props.

**Returns**:
```typescript
{
  // State (read-only)
  filters: SearchFilters;
  
  // Actions
  updateLocation: (location: LocationSelection) => void;
  removeLocation: (index: number) => void;
  setTripType: (typeId: number | null) => void;
  toggleTheme: (themeId: number) => void;
  setDate: (year: string, month: string) => void;
  setDuration: (min: number, max: number) => void;
  setBudget: (budget: number) => void;
  setDifficulty: (difficulty: number | null) => void;
  
  // Computed
  hasActiveFilters: boolean;
  
  // Actions
  clearAllFilters: () => void;
  executeSearch: () => void; // Handles navigation to results
}
```

**Lines**: ~150 lines

**Alternative**: Use Context API (`SearchProvider`) if prop drilling becomes excessive.

---

#### useSyncSearchQuery
**Location**: `hooks/useSyncSearchQuery.ts`

**Purpose**: Handle URL parameter serialization/deserialization. Separates URL logic from business logic.

**Returns**:
```typescript
{
  // Load filters from URL (on mount/back button)
  loadFiltersFromUrl: (searchParams: URLSearchParams) => SearchFilters;
  
  // Serialize filters to URL
  serializeFiltersToUrl: (filters: SearchFilters) => URLSearchParams;
}
```

**Lines**: ~80 lines

**Note**: `SearchPageContent` should only work with clean filter objects, not URL strings.

---

## Refactored Page Component

### SearchPageContent (New Structure)
**Location**: `components/features/search/SearchPageContent.tsx`

**Responsibilities**:
- Coordinate data fetching
- Manage high-level state (or use useSearchFilters hook)
- Handle search submission
- Compose filter sections
- Handle loading/error states

**Structure**:
```typescript
function SearchPageContent() {
  // Data fetching - using centralized data store hooks
  const { countries, isLoading: isLoadingCountries } = useCountries();
  const { tripTypes, isLoading: isLoadingTripTypes } = useTripTypes();
  const { themeTags, isLoading: isLoadingThemeTags } = useThemeTags();
  
  // Headless hook - all business logic here
  const search = useSearch();
  
  // URL sync - handles serialization/deserialization
  const { loadFiltersFromUrl, serializeFiltersToUrl } = useSyncSearchQuery();
  const searchParams = useSearchParams();
  
  // Load from URL on mount/back button
  useEffect(() => {
    const filters = loadFiltersFromUrl(searchParams);
    search.loadFilters(filters);
  }, [searchParams]);
  
  // Render sections - components pull state from useSearch hook
  return (
    <div>
      <SearchPageHeader />
      <div className="container">
        <LocationFilterSection />
        <TripTypeFilterSection />
        <ThemeFilterSection />
        <DateFilterSection />
        <RangeFiltersSection />
        <SearchActions onSearch={search.executeSearch} />
      </div>
    </div>
  );
}
```

**Key Benefits**:
- No prop drilling - components use `useSearch()` hook directly
- Clean separation: URL logic in `useSyncSearchQuery`, business logic in `useSearch`
- Components are simpler - they don't need complex prop interfaces

**Lines**: ~150-200 lines (down from 850+)

---

### SearchPage (page.tsx)
**Location**: `app/search/page.tsx`

**Responsibilities**:
- Suspense wrapper
- Export default component
- Minimal logic

**Structure**:
```typescript
export default function SearchPage() {
  return (
    <Suspense fallback={<SearchPageLoading />}>
      <SearchPageContent />
    </Suspense>
  );
}
```

**Lines**: ~10 lines

---

## Current File Structure

```
frontend/src/
├── app/
│   └── search/
│       ├── page.tsx (1,079 lines - monolithic)
│       ├── results/
│       │   └── page.tsx (700 lines - separate results page)
│       ├── error.tsx
│       └── results/
│           ├── error.tsx
│           └── loading.tsx
│
├── components/
│   ├── features/
│   │   ├── DualRangeSlider.tsx ✅ (extracted)
│   │   ├── LogoutConfirmModal.tsx ✅ (extracted)
│   │   ├── TripResultCard.tsx ✅ (extracted)
│   │   └── search/ (to be created)
│   │       ├── SearchPageContent.tsx (~200 lines)
│   │       ├── SearchPageHeader.tsx (~80 lines)
│   │       ├── SearchActions.tsx (~50 lines)
│   │       ├── SearchPageLoading.tsx (~30 lines)
│   │       ├── SearchPageError.tsx (~40 lines)
│   │       └── filters/
│   │           ├── LocationFilterSection.tsx (~200 lines)
│   │           ├── TripTypeFilterSection.tsx (~80 lines)
│   │           ├── ThemeFilterSection.tsx (~70 lines)
│   │           ├── DateFilterSection.tsx (~70 lines)
│   │           └── RangeFiltersSection.tsx (~150 lines)
│   │
│   └── ui/
│       ├── SelectionBadge.tsx (~60 lines) ⏳ (to be extracted)
│       ├── TagCircle.tsx (~40 lines) ⏳ (to be extracted)
│       └── ClearFiltersButton.tsx (~30 lines) ⏳ (to be created)
│
└── hooks/
    ├── useSearch.ts (~150 lines) ⏳ (REQUIRED - Phase 1)
    └── useSyncSearchQuery.ts (~80 lines) ⏳ (REQUIRED - Phase 1)
```

**Legend:**
- ✅ = Already extracted/implemented
- ⏳ = Pending extraction/implementation

## Target File Structure After Refactoring

```
frontend/src/
├── app/
│   └── search/
│       └── page.tsx (10 lines - Suspense wrapper only)
│
├── components/
│   ├── features/
│   │   ├── DualRangeSlider.tsx ✅
│   │   ├── LogoutConfirmModal.tsx ✅
│   │   ├── TripResultCard.tsx ✅
│   │   └── search/
│   │       ├── SearchPageContent.tsx (~200 lines)
│   │       ├── SearchPageHeader.tsx (~80 lines)
│   │       ├── SearchActions.tsx (~50 lines)
│   │       ├── SearchPageLoading.tsx (~30 lines)
│   │       ├── SearchPageError.tsx (~40 lines)
│   │       └── filters/
│   │           ├── LocationFilterSection.tsx (~60 lines - container)
│   │           ├── LocationDropdown.tsx (~120 lines - complex logic)
│   │           ├── SelectedLocationsList.tsx (~40 lines - display)
│   │           ├── TripTypeFilterSection.tsx (~80 lines)
│   │           ├── ThemeFilterSection.tsx (~70 lines)
│   │           ├── DateFilterSection.tsx (~70 lines)
│   │           └── RangeFiltersSection.tsx (~150 lines)
│   │
│   └── ui/
│       ├── SelectionBadge.tsx (~60 lines) - stateless
│       ├── TagCircle.tsx (~40 lines) - stateless (takes icon prop)
│       └── ClearFiltersButton.tsx (~30 lines) - stateless
│
└── hooks/
    ├── useSearch.ts (~150 lines) - Headless hook (required)
    └── useSyncSearchQuery.ts (~80 lines) - URL serialization (required)
```

## Implementation Plan

### Phase 1: Core Infrastructure & UI Components (Required Foundation) - **NOT STARTED**

**Critical**: This phase establishes the foundation. Do not proceed to Phase 2 without completing this.

1. **Create Headless Hook** (`hooks/useSearch.ts`)
   - Centralize all filter state management
   - Implement business logic (add/remove locations, toggle themes, etc.)
   - Provide `executeSearch()` method for navigation
   - **This eliminates prop drilling from the start**

2. **Create URL Sync Hook** (`hooks/useSyncSearchQuery.ts`)
   - Move all URLSearchParams logic here
   - Separate serialization/deserialization from business logic
   - `SearchPageContent` should only work with clean filter objects

3. **Extract Stateless UI Components**
   - Extract `SelectionBadge` to `components/ui/SelectionBadge.tsx`
   - Extract `TagCircle` to `components/ui/TagCircle.tsx` (**stateless** - takes `icon` prop, not `iconMap`)
   - Create `ClearFiltersButton` component
   - Update imports in `page.tsx`

4. **Testing**: Verify UI remains identical, state management works correctly

**Estimated Time**: 4-6 hours
**Risk Level**: Low-Medium (foundation work)
**Status**: Pending

---

### Phase 2: Extract Filter Sections (Medium Risk) - **NOT STARTED**

**Note**: With `useSearch` hook in place, these components will be simpler - they pull state rather than receive props.

1. **Extract `LocationFilterSection`** (split into 3 components)
   - `LocationFilterSection.tsx` (~60 lines) - Container
   - `LocationDropdown.tsx` (~120 lines) - Complex dropdown with keyboard nav, click-outside
   - `SelectedLocationsList.tsx` (~40 lines) - Simple display using SelectionBadge
   - All use `useSearch()` hook for state
   
2. Extract `TripTypeFilterSection`
   - Uses `useSearch()` hook
   - Uses stateless `TagCircle` component
   
3. Extract `ThemeFilterSection`
   - Uses `useSearch()` hook
   - Uses stateless `TagCircle` component
   
4. Extract `DateFilterSection`
   - Uses `useSearch()` hook
   - Test year/month dependency
   
5. Extract `RangeFiltersSection`
   - Uses `useSearch()` hook
   - Reuse existing `DualRangeSlider` component
   - Extract sub-components if needed

**Estimated Time**: 8-12 hours
**Risk Level**: Medium (simplified by Phase 1 infrastructure)
**Status**: Pending

---

### Phase 3: Extract Header and Actions (Low Risk) - **NOT STARTED**
1. Extract `SearchPageHeader`
   - Move header JSX and related logic
   - Handle logout modal integration
   - Note: `LogoutConfirmModal` already extracted, can be reused
   
2. Extract `SearchActions`
   - Move search and clear buttons
   - Extract clear filters logic

**Estimated Time**: 3-4 hours
**Risk Level**: Low
**Status**: Pending

---

### Phase 4: Refactor Main Component (High Risk) - **NOT STARTED**
1. Create `SearchPageContent` component
2. Refactor state management (consider useSearchFilters hook)
3. Integrate all extracted components
4. Move loading/error states to separate components
5. Test end-to-end functionality

**Estimated Time**: 6-8 hours
**Risk Level**: High (core functionality)
**Status**: Pending

---

### Phase 5: Optional Enhancements (Low Priority) - **NOT STARTED**

1. **Consider Context API** (`SearchProvider`)
   - If prop drilling becomes an issue (unlikely with `useSearch` hook)
   - Alternative to hook-based approach
   
2. Extract `SearchPageError` component
3. Add component-level tests
4. Update documentation
5. Performance optimizations (React.memo, code splitting)

**Estimated Time**: 4-6 hours
**Risk Level**: Low
**Status**: Pending

---

## Benefits

### Maintainability
- **Smaller Files**: Each component is 50-200 lines, easy to navigate
- **Single Responsibility**: Each component has one clear purpose
- **Easier Debugging**: Issues can be isolated to specific components
- **Better Code Reviews**: Changes are localized to relevant files

### Reusability
- UI components (`SelectionBadge`, `TagCircle`) can be reused
- Filter sections can be reused in other search contexts
- Header can be reused in other authenticated pages

### Testability
- Each component can be unit tested independently
- Mock dependencies are easier to manage
- Test coverage can be improved incrementally

### Performance
- Better code splitting opportunities
- Smaller initial bundle size
- Lazy loading potential for filter sections

### Developer Experience
- Faster navigation in IDE
- Better autocomplete and IntelliSense
- Clearer component boundaries
- Easier onboarding for new developers

## Risks and Mitigation

### Risk 1: State Management Complexity
**Issue**: Passing state through multiple component layers (prop drilling)
**Mitigation**: 
- **Phase 1 Requirement**: Create `useSearch` hook from the start - components pull state rather than receive props
- Consider Context API (`SearchProvider`) only if hook-based approach becomes unwieldy
- Avoid prop drilling by design, not as an afterthought

### Risk 2: Breaking Changes
**Issue**: Refactoring might introduce bugs
**Mitigation**:
- Phase-by-phase implementation with testing at each phase
- Maintain feature parity at each step
- Test thoroughly before moving to next phase
- Keep original file until refactoring is complete and tested

### Risk 3: Over-Engineering
**Issue**: Creating too many small components
**Mitigation**:
- Start with larger components, extract further if needed
- Follow the rule: "Extract when component exceeds ~200 lines"
- Keep related functionality together

### Risk 4: Performance Regression
**Issue**: Additional component layers might impact performance
**Mitigation**:
- React is optimized for component composition
- Use React.memo for expensive components if needed
- Profile before and after refactoring

## Testing Strategy

### Unit Tests
- Test each extracted component independently
- Mock props and dependencies
- Test user interactions (clicks, selections, inputs)

### Integration Tests
- Test filter sections together
- Test URL parameter synchronization
- Test search submission flow

### E2E Tests
- Test complete search flow
- Test browser navigation (back/forward)
- Test with different filter combinations

## Migration Strategy

### Option 1: Big Bang (Not Recommended)
- Refactor entire file at once
- High risk, difficult to debug

### Option 2: Incremental (Recommended)
- Phase-by-phase approach (as outlined above)
- Test after each phase
- Keep original file until complete
- Use feature flags if needed

### Option 3: Parallel Implementation
- Create new components alongside old code
- Switch over with feature flag
- Remove old code after validation

## Success Metrics

1. **File Size Reduction**: 
   - Main page file: < 200 lines
   - Individual components: < 200 lines each

2. **Component Count**: 
   - 8-12 focused components
   - Clear separation of concerns

3. **Test Coverage**: 
   - > 80% unit test coverage
   - Integration tests for critical flows

4. **Developer Feedback**: 
   - Easier to navigate codebase
   - Faster feature development
   - Reduced bugs

5. **Performance**: 
   - No regression in bundle size
   - Maintain or improve load times

## Alternatives Considered

### Alternative 1: Keep Monolithic Structure
**Rejected**: Does not address maintainability issues

### Alternative 2: Split by Feature (All Filters in One File)
**Rejected**: Still creates large files, less granular control

### Alternative 3: Use State Management Library (Redux/Zustand)
**Considered but deferred**: Current state management is adequate. Can be added later if needed.

## Conclusion

This refactoring proposal addresses the core issues of the monolithic search page by:
1. Extracting reusable UI components
2. Creating focused filter section components
3. Separating concerns (header, filters, actions)
4. Maintaining a clear component hierarchy
5. Providing a phased implementation plan

The proposed structure follows React best practices, improves maintainability, and sets a foundation for future enhancements while minimizing risk through incremental implementation.

## Next Steps

1. **Review and Approval**: Get team/stakeholder buy-in
2. **Prioritize Phases**: Decide which phases are critical vs. nice-to-have
3. **Create Tickets**: Break down into actionable tasks
4. **Set Timeline**: Estimate and schedule implementation
5. **Start Phase 1**: Begin with low-risk UI component extraction

---

## Progress Summary

### Completed
- ✅ `DualRangeSlider` component extracted
- ✅ `LogoutConfirmModal` component extracted
- ✅ `TripResultCard` component extracted
- ✅ Results page separated to `/search/results/page.tsx` (700 lines)

### In Progress
- None currently

### Pending
- ⏳ Extract `SelectionBadge` and `TagCircle` UI components
- ⏳ Extract filter sections (Location, Trip Type, Theme, Date, Range)
- ⏳ Extract header and actions components
- ⏳ Refactor main `SearchPageContent` component
- ⏳ Create custom hooks for state management

### Notes
- The search page remains at 1,079 lines and is still monolithic
- Results page is properly separated (700 lines)
- Some reusable components have been extracted, which will help with the refactoring
- Data fetching is now handled via `useCountries`, `useTripTypes`, `useThemeTags` hooks from `dataStore.tsx`

### Architecture Improvements (Based on Senior Dev Review)
- **Headless Hook Pattern**: `useSearch` hook centralizes business logic, components pull state
- **URL Logic Separation**: `useSyncSearchQuery` handles serialization, keeping components clean
- **Stateless UI Components**: `TagCircle` and others are truly reusable (no business logic)
- **Granular Location Components**: Dropdown logic separated from display logic for maintainability

---

**Document Version**: 2.1
**Last Updated**: December 2024
**Author**: Senior Developer Review
**Status**: Proposal - Partially Implemented (3 components extracted, main refactoring pending)
**Review Notes**: Updated based on senior dev feedback - useSearch hook now Phase 1 requirement, UI components made stateless, URL logic separated
