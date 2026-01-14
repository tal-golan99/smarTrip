# Frontend - SmartTrip

Next.js 14 frontend application for the SmartTrip trip recommendation platform.

## Overview

The frontend is built with Next.js 14 using the App Router, React 18, TypeScript, and Tailwind CSS. It provides a bilingual (Hebrew/English) interface for users to search and discover personalized trip recommendations.

## Tech Stack

- **Next.js 14** - React framework with App Router
- **React 18** - UI library
- **TypeScript 5** - Type safety
- **Tailwind CSS 3.4** - Utility-first styling
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
│   │   └── trip/[id]/        # Trip detail pages
│   ├── components/            # React components
│   │   ├── features/         # Feature components
│   │   └── ui/               # UI primitives
│   ├── hooks/                # Custom React hooks
│   ├── lib/                  # Utilities and state
│   └── services/             # API and tracking services
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

## Key Features

### Search & Recommendations

- **Search Form** (`src/app/search/page.tsx`) - Multi-criteria search with:
  - Geographic filters (countries, continents)
  - Trip preferences (type, themes)
  - Constraints (budget, duration, difficulty)
  - Date filters (year, month)

- **Results Page** (`src/app/search/results/page.tsx`) - Displays personalized recommendations with:
  - Match scores (0-100) with color coding
  - Trip cards with key information
  - Primary and relaxed results separation

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

- **DataStore** (`src/lib/dataStore.tsx`) - Context API for reference data (countries, trip types, tags)
- **Local State** - Component-level state for UI interactions
- **URL State** - Search parameters preserved in URL for shareability

## API Integration

### API Service

The `src/services/api.service.ts` provides a centralized API client with:

- **Retry Logic** - Automatic retries for cold starts
- **Authentication** - JWT token injection
- **Error Handling** - Consistent error handling
- **Type Safety** - TypeScript interfaces for all endpoints

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
- `app/search/page.tsx` - Search form
- `app/search/results/page.tsx` - Search results
- `app/trip/[id]/page.tsx` - Trip detail page
- `app/auth/page.tsx` - Authentication page

### Components

- **Features** (`components/features/`) - Feature-specific components:
  - `TripResultCard.tsx` - Trip card component
  - `DualRangeSlider.tsx` - Budget/duration slider
  - `RegistrationModal.tsx` - Registration modal
  - `LogoutConfirmModal.tsx` - Logout confirmation

- **UI** (`components/ui/`) - Reusable UI primitives

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

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Responsive design for all screen sizes

## Development Guidelines

### Code Style

- TypeScript strict mode enabled
- ESLint for code quality
- No ternary operators (use if-else statements)
- Functional components with hooks

### File Naming

- Components: PascalCase (e.g., `TripResultCard.tsx`)
- Hooks: camelCase with `use` prefix (e.g., `useTracking.ts`)
- Services: camelCase (e.g., `api.service.ts`)
- Pages: lowercase (Next.js convention)

### State Management

- Use Context API for global reference data
- Use local state for component-specific data
- Use URL parameters for shareable state (search params)

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

## Deployment

The frontend is deployed on Vercel:

1. Connect repository to Vercel
2. Set root directory to `frontend`
3. Configure environment variables
4. Deploy automatically on push to main branch

See `docs/deployment/` for detailed deployment guides.

## Related Documentation

- [Main README](../README.md) - Project overview
- [Architecture Docs](../docs/architecture/) - System architecture
- [API Docs](../docs/api/) - API reference
- [Deployment Guide](../docs/deployment/) - Deployment instructions
