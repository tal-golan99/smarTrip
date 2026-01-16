# Frontend - SmartTrip

Next.js 14 frontend application for the SmartTrip trip recommendation platform.

## Overview

The frontend is built with Next.js 14 using the App Router, React 18, TypeScript, and Tailwind CSS. It provides a bilingual (Hebrew/English) interface for users to search and discover personalized trip recommendations with a fully refactored, modular architecture.

## Tech Stack

- **Next.js 14** - React framework with App Router
- **React 18** - UI library with Context API
- **TypeScript 5** - Type safety
- **Tailwind CSS 3.4** - Utility-first styling
- **Zod 3.22** - Runtime schema validation
- **Lucide React** - Icon library
- **Supabase** - Authentication and database client

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx         # Root layout with providers
│   │   ├── page.tsx           # Home page
│   │   ├── auth/              # Authentication pages
│   │   ├── search/            # Search functionality
│   │   │   ├── page.tsx       # Search page (162 lines, refactored)
│   │   │   └── results/       # Search results page
│   │   └── trip/[id]/        # Trip detail pages
│   ├── api/                   # API client layer
│   │   ├── client.ts          # Core API utilities
│   │   ├── types.ts           # TypeScript types
│   │   ├── system.ts          # System API
│   │   ├── resources.ts       # Resources API
│   │   ├── events.ts          # Events API
│   │   └── v2.ts              # V2 API
│   ├── schemas/               # Zod validation schemas
│   │   ├── base.ts            # Base schemas
│   │   ├── resources.ts       # Resource schemas
│   │   ├── trip.ts            # Trip schemas
│   │   ├── events.ts          # Event schemas
│   │   └── analytics.ts       # Analytics schemas
│   ├── components/            # React components
│   │   ├── features/         # Feature components
│   │   │   ├── search/       # Search page components
│   │   │   │   ├── filters/  # Filter sections
│   │   │   │   ├── SearchPageHeader.tsx
│   │   │   │   ├── SearchActions.tsx
│   │   │   │   └── index.ts  # Barrel exports
│   │   │   ├── TripResultCard.tsx
│   │   │   ├── RegistrationModal.tsx
│   │   │   └── LogoutConfirmModal.tsx
│   │   └── ui/               # Reusable UI components
│   │       ├── DualRangeSlider.tsx
│   │       ├── SelectionBadge.tsx
│   │       ├── TagCircle.tsx
│   │       └── ClearFiltersButton.tsx
│   ├── contexts/             # React Context providers
│   │   └── SearchContext.tsx # Search state management
│   ├── hooks/                # Custom React hooks
│   │   ├── useSearch.ts      # Search state hook
│   │   ├── useSyncSearchQuery.ts  # URL sync hook
│   │   ├── useTracking.ts    # Tracking hooks
│   │   └── useUser.ts        # User state hook
│   ├── lib/                  # Utilities and state
│   │   ├── dataStore.tsx     # Data store context
│   │   ├── supabaseClient.ts # Supabase client
│   │   └── utils.ts          # Utility functions
│   └── services/             # Service layer
│       └── tracking.service.ts  # Tracking service
├── scripts/                  # Development scripts
│   └── test-search-page.ts  # Search page validation
├── public/                   # Static assets
└── package.json             # Dependencies
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm 9+ or yarn

### Installation

```bash
# Install dependencies
npm install
```

### Environment Variables

Create `frontend/.env.local`:

```env
# Backend API URL (required)
NEXT_PUBLIC_API_URL=http://localhost:5000

# Supabase Authentication (optional - app works in guest mode)
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

**Important:**
- The `.env.local` file must be in the `frontend/` directory
- Next.js only reads environment files from the directory where it runs
- This file is automatically gitignored

### Development

```bash
# Start development server
npm run dev

# Runs on http://localhost:3000
```

### Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

### Linting

```bash
# Run ESLint
npm run lint
```

### Testing

```bash
# Test search page structure
npm run test:search
```

## Key Features

### Search & Recommendations

- **Search Form** (`src/app/search/page.tsx`) - Refactored modular search with:
  - React Context for state management
  - Modular filter sections
  - URL synchronization for shareable links
  - 162 lines (down from 1,079)
  
- **Filter Sections** (`src/components/features/search/filters/`) - Focused components:
  - `LocationFilterSection` - Location search with dropdown
  - `TripTypeFilterSection` - Trip type selection
  - `ThemeFilterSection` - Theme tag selection (max 3)
  - `DateFilterSection` - Year and month filters
  - `RangeFiltersSection` - Duration, budget, and difficulty

- **Results Page** (`src/app/search/results/page.tsx`) - Displays personalized recommendations with:
  - Match scores (0-100) with color coding
  - Trip cards with key information
  - Primary and relaxed results separation
  - Minimum score threshold of 30

### Authentication

- **Supabase Integration** (`src/lib/supabaseClient.ts`) - OAuth and email/password auth
- **Guest Mode** - App works without authentication
- **User Context** (`src/hooks/useUser.ts`) - User state management

### Event Tracking

- **Tracking Service** (`src/services/tracking.service.ts`) - Event batching and session management
- **Tracking Hooks** (`src/hooks/useTracking.ts`) - Reusable tracking hooks:
  - `usePageView()` - Page view tracking
  - `useResultsTracking()` - Search results tracking
  - `useImpressionTracking()` - Viewport impression tracking

### State Management

- **React Context API** - Centralized state management
  - `SearchProvider` - Search state context
  - `DataStoreProvider` - Reference data context
- **Custom Hooks** - Headless logic hooks
  - `useSearch()` - Access search state
  - `useSyncSearchQuery()` - URL parameter sync
- **URL State** - Search parameters preserved in URL for shareability

## API Integration

### API Service

The `src/api/` directory provides a structured API client with:

- **Mirrored Structure** - Matches backend blueprint organization
- **Type Safety** - TypeScript interfaces for all endpoints
- **Zod Validation** - Runtime schema validation for all responses
- **Developer Logging** - Detailed logging in development mode
- **Retry Logic** - Automatic retries for cold starts
- **Authentication** - JWT token injection
- **Error Handling** - Consistent error handling

### API Structure

```
src/api/
├── client.ts       # Core utilities (apiFetch, validateResponse)
├── types.ts        # TypeScript type definitions
├── system.ts       # System API (health check)
├── resources.ts    # Resources API (countries, guides, tags)
├── events.ts       # Events API (tracking, sessions)
└── v2.ts           # V2 API (recommendations, trips)
```

### Main Endpoints

- `POST /api/v2/recommendations` - Get trip recommendations
- `GET /api/locations` - Get countries and continents
- `GET /api/trip-types` - Get trip type categories
- `GET /api/tags` - Get theme tags
- `POST /api/events/batch` - Batch upload events

## Component Architecture

### Pages

Pages are organized using Next.js App Router file-based routing:

- `app/page.tsx` - Home page
- `app/search/page.tsx` - Search form (refactored, 162 lines)
- `app/search/results/page.tsx` - Search results
- `app/trip/[id]/page.tsx` - Trip detail page
- `app/auth/page.tsx` - Authentication page

### Search Page Architecture

The search page follows a modular, component-based architecture:

#### Main Page (`app/search/page.tsx`)
- Minimal Suspense wrapper (162 lines)
- Wraps content with `SearchProvider`
- Handles loading and error states

#### Search Context (`contexts/SearchContext.tsx`)
- Centralized state management
- Filter state (locations, types, themes, dates, ranges)
- Actions (add/remove locations, toggle themes, execute search)
- Computed values (hasActiveFilters)

#### Search Hook (`hooks/useSearch.ts`)
- Provides access to shared search state
- Components pull state instead of receiving props
- No prop drilling

#### Filter Sections (`components/features/search/filters/`)
- **LocationFilterSection** (137 lines) - Location search container
  - **LocationDropdown** (104 lines) - Complex dropdown logic
  - **SelectedLocationsList** (31 lines) - Display selected locations
- **TripTypeFilterSection** (68 lines) - Trip type selection
- **ThemeFilterSection** (59 lines) - Theme tag selection
- **DateFilterSection** (79 lines) - Year and month filters
- **RangeFiltersSection** (101 lines) - Duration, budget, difficulty

#### Other Components
- **SearchPageHeader** - Logo, navigation, user greeting
- **SearchActions** - Search and clear buttons
- **SearchPageLoading** - Loading state
- **SearchPageError** - Error state with retry

### UI Components

- **Features** (`components/features/`) - Feature-specific components:
  - `TripResultCard.tsx` - Trip card component
  - `DualRangeSlider.tsx` - Budget/duration slider (moved to `components/ui/`)
  - `RegistrationModal.tsx` - Registration modal
  - `LogoutConfirmModal.tsx` - Logout confirmation

- **UI** (`components/ui/`) - Reusable UI primitives:
  - `DualRangeSlider.tsx` - Dual range slider
  - `SelectionBadge.tsx` - Location selection badge
  - `TagCircle.tsx` - Tag circle component
  - `ClearFiltersButton.tsx` - Clear filters button

## Styling

### Tailwind CSS

The project uses Tailwind CSS for styling:

- **Utility Classes** - Rapid UI development
- **Custom Colors** - Project-specific color palette
- **Responsive Design** - Mobile-first approach
- **Dark Mode Ready** - Can be extended for dark mode

### Global Styles

- `app/globals.css` - Global styles and Tailwind directives
- Custom CSS variables for theming

## Performance Optimizations

- **Code Splitting** - Automatic via Next.js
- **Image Optimization** - Next.js Image component
- **Lazy Loading** - Dynamic imports for heavy components
- **Event Batching** - Efficient event tracking (10 events or 5 seconds)
- **Modular Architecture** - Smaller, focused components for better code splitting

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Responsive design for all screen sizes

## Development Guidelines

### Code Style

- TypeScript strict mode enabled
- ESLint for code quality
- **No ternary operators** (use if-else statements)
- Functional components with hooks
- React Context for shared state

### File Naming

- Components: PascalCase (e.g., `TripResultCard.tsx`)
- Hooks: camelCase with `use` prefix (e.g., `useTracking.ts`)
- Services: camelCase (e.g., `tracking.service.ts`)
- Pages: lowercase (Next.js convention)

### State Management

- Use Context API for shared state (search filters, reference data)
- Use local state for component-specific data
- Use URL parameters for shareable state (search params)
- Custom hooks for reusable logic

### Component Design

- **Single Responsibility** - Each component has one clear purpose
- **Composition** - Build complex UIs from simple components
- **Stateless UI** - UI components should be stateless when possible
- **Headless Hooks** - Separate logic from presentation

## Architecture Principles

### Search Page Refactoring

The search page was refactored from a monolithic 1,079-line component to a modular architecture:

**Before:**
- Single file with mixed concerns
- Inline components
- Prop drilling
- Difficult to maintain and test

**After:**
- Modular component structure
- React Context for state management
- Focused, reusable components
- Clear separation of concerns
- 162-line main page

### State Management Pattern

**React Context API:**
- `SearchProvider` wraps the search page
- `useSearch()` hook provides access to shared state
- Components pull state instead of receiving props
- No prop drilling

**Benefits:**
- Centralized state management
- Easy to add new filters
- Components are simpler
- Better testability

### API Layer Pattern

**Structure:**
- Mirrors backend blueprint organization
- Type-safe with Zod validation
- Consistent error handling
- Developer logging

**Benefits:**
- Easy to find endpoints
- Type safety at runtime
- Consistent API usage
- Better debugging

## Troubleshooting

### Common Issues

**Environment Variables Not Loading**
- Ensure `.env.local` is in the `frontend/` directory
- Restart the dev server after adding variables
- Variables must be prefixed with `NEXT_PUBLIC_` to be accessible in browser

**API Connection Errors**
- Check `NEXT_PUBLIC_API_URL` is correct
- Verify backend is running
- Check CORS settings on backend

**Build Errors**
- Run `npm install` to ensure dependencies are installed
- Check TypeScript errors with `npm run lint`
- Clear `.next` folder and rebuild

**Search Page Issues**
- Verify `SearchProvider` wraps the page
- Check `useSearch()` hook is used correctly
- Verify URL parameters are synced

## Deployment

The frontend is deployed on Vercel:

1. Connect repository to Vercel
2. Set root directory to `frontend`
3. Configure environment variables
4. Deploy automatically on push to main branch

See `docs/deployment/` for detailed deployment guides.

## Testing

### Structure Testing

```bash
# Test search page structure
npm run test:search
```

This validates:
- File existence
- Component usage
- Import correctness
- File size constraints

### Manual Testing

Test the search flow:
1. Navigate to `/search`
2. Select filters (location, type, themes, dates, ranges)
3. Click search
4. Verify URL contains parameters
5. Verify results display correctly
6. Test back button (URL sync)

## Recent Updates

### Search Page Refactoring (January 2026)

- Refactored from 1,079 lines to 162 lines
- Implemented React Context for state management
- Created 7 modular filter section components
- Added URL synchronization for shareable links
- Moved `DualRangeSlider` to `components/ui/`
- Removed backward compatibility layer
- Added `test:search` script for validation

### API Layer Updates

- Mirrored backend blueprint structure
- Added Zod validation for all endpoints
- Implemented developer logging
- Consistent error handling

## Related Documentation

- [Main README](../README.md) - Project overview
- [Backend README](../backend/README.md) - Backend architecture
- [API Structure](../docs/api/API_STRUCTURE.md) - API documentation
- [Search Page Refactor](../docs/proposals/SEARCH_PAGE_REFACTOR_PROPOSAL.md) - Refactoring details
- [Architecture Alignment](../docs/architecture/API_STRUCTURE_ALIGNMENT.md) - Frontend/Backend alignment

## Contributing

This is a portfolio project. For questions or suggestions, please contact the author.

---

**Last Updated:** January 2026
