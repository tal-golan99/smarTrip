# User Profile Page Implementation Proposal

## Executive Summary

This proposal outlines the implementation of a user profile page and profile dropdown menu for authenticated users. The feature will provide users with access to their profile information, preferences, saved trips, search history, and account settings. The implementation includes a user avatar/button in the header with a dropdown menu (similar to Google's user menu pattern) and a dedicated profile page.

## Current State Analysis

### Authentication System
- **Authentication Provider**: Supabase (email/password and Google OAuth)
- **User Hook**: `useUser()` hook in `hooks/useUser.ts` manages user state
- **User Data Available**: 
  - User metadata (full_name, name, first_name, last_name)
  - Email address
  - User ID (Supabase UUID)
  - Session information

### Current Header Structure
- **Component**: `SearchPageHeader.tsx` (70 lines)
- **Current Layout**:
  - Left: Home button, Logout button (if authenticated)
  - Center: Title and user greeting ("שלום {userName}!")
  - Right: Company logo
- **User Display**: User name shown in subtitle below title (centered)

### Existing User-Related Features
- User session tracking via Events API (`/api/session/start`, `/api/user/identify`)
- Anonymous user tracking with `anonymous_id`
- User identification endpoint (`POST /api/user/identify`)

### Missing Features
- No user profile page
- No user preferences management
- No saved trips/favorites functionality
- No search history per user
- No user avatar display
- No dropdown menu for user actions

## Proposed Architecture

### Component Hierarchy

```
Header (SearchPageHeader or new UserHeader)
├── UserMenuButton (components/features/user/)
│   ├── UserAvatar (components/ui/)
│   └── UserDropdownMenu (components/features/user/)
│       ├── UserInfoSection
│       ├── MenuItem (My Profile)
│       ├── MenuItem (Preferences)
│       ├── MenuItem (Saved Trips)
│       ├── MenuItem (Search History)
│       ├── Divider
│       └── MenuItem (Logout)
└── [Existing header elements]

Profile Page (app/profile/page.tsx)
├── ProfileHeader
├── ProfileTabs
│   ├── OverviewTab
│   ├── PreferencesTab
│   ├── SavedTripsTab
│   └── SearchHistoryTab
└── ProfileActions
```

### File Structure

```
frontend/src/
├── app/
│   └── profile/
│       ├── page.tsx (~200 lines - main profile page)
│       ├── loading.tsx (~30 lines)
│       └── error.tsx (~40 lines)
│
├── components/
│   ├── features/
│   │   └── user/
│   │       ├── UserMenuButton.tsx (~80 lines)
│   │       ├── UserDropdownMenu.tsx (~150 lines)
│   │       ├── UserAvatar.tsx (~60 lines)
│   │       ├── ProfileHeader.tsx (~100 lines)
│   │       ├── ProfileTabs.tsx (~50 lines)
│   │       ├── OverviewTab.tsx (~150 lines)
│   │       ├── PreferencesTab.tsx (~200 lines)
│   │       ├── SavedTripsTab.tsx (~150 lines)
│   │       └── SearchHistoryTab.tsx (~150 lines)
│   │
│   └── ui/
│       ├── DropdownMenu.tsx (~100 lines - reusable)
│       ├── Avatar.tsx (~50 lines - reusable)
│       └── TabButton.tsx (~40 lines - reusable)
│
└── hooks/
    ├── useUserProfile.ts (~100 lines)
    ├── useUserPreferences.ts (~80 lines)
    └── useSavedTrips.ts (~100 lines)
```

## Detailed Component Breakdown

### 1. User Menu Button (Header Integration)

**Location**: `components/features/user/UserMenuButton.tsx`

**Purpose**: Replace the current logout button with a user menu button that shows avatar/initials and opens dropdown menu.

**Design Pattern**: Similar to Google's user menu (top-right corner with avatar circle)

**Props**:
```typescript
interface UserMenuButtonProps {
  userName: string | null;
  userEmail: string | null;
  userAvatar?: string | null;
  isLoading: boolean;
}
```

**Features**:
- Display user avatar (if available) or initials circle
- Show dropdown menu on click
- Handle click-outside to close menu
- Keyboard navigation support (Enter, Escape, Arrow keys)
- Accessible (ARIA labels, focus management)

**Lines**: ~80 lines

---

### 2. User Avatar Component

**Location**: `components/ui/Avatar.tsx` (reusable)

**Purpose**: Display user avatar or initials fallback.

**Props**:
```typescript
interface AvatarProps {
  name: string | null;
  email: string | null;
  imageUrl?: string | null;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}
```

**Features**:
- Display user image if available (from Supabase metadata or Google OAuth)
- Fallback to initials (first letter of first name + first letter of last name)
- Fallback to first letter of email if no name
- Size variants (small for header, medium/large for profile page)
- Circular design with background color based on name hash

**Lines**: ~60 lines

---

### 3. User Dropdown Menu

**Location**: `components/features/user/UserDropdownMenu.tsx`

**Purpose**: Dropdown menu that appears when clicking user button.

**Props**:
```typescript
interface UserDropdownMenuProps {
  userName: string | null;
  userEmail: string | null;
  userAvatar?: string | null;
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (path: string) => void;
  onLogout: () => void;
}
```

**Menu Items**:
1. **User Info Section** (non-clickable)
   - Avatar + Name + Email
   - Shows current user info
   
2. **My Profile** (navigates to `/profile`)
   - Icon: User icon
   - Hebrew: "הפרופיל שלי"
   
3. **Preferences** (navigates to `/profile?tab=preferences`)
   - Icon: Settings icon
   - Hebrew: "העדפות"
   
4. **Saved Trips** (navigates to `/profile?tab=saved`)
   - Icon: Heart/Bookmark icon
   - Hebrew: "טיולים שמורים"
   
5. **Search History** (navigates to `/profile?tab=history`)
   - Icon: Clock/History icon
   - Hebrew: "היסטוריית חיפושים"
   
6. **Divider**
   
7. **Logout** (triggers logout)
   - Icon: LogOut icon
   - Hebrew: "התנתק"
   - Shows confirmation modal (reuse `LogoutConfirmModal`)

**Features**:
- Smooth open/close animation
- Click-outside to close
- Keyboard navigation (Arrow keys, Enter, Escape)
- Focus trap when open
- Accessible (ARIA menu, roles, labels)

**Lines**: ~150 lines

---

### 4. Profile Page

**Location**: `app/profile/page.tsx`

**Purpose**: Main profile page with tabs for different sections.

**Structure**:
```typescript
export default function ProfilePage() {
  const { user, userName, isLoading } = useUser();
  const searchParams = useSearchParams();
  const activeTab = searchParams.get('tab') || 'overview';
  
  // Redirect to auth if not logged in
  if (!isLoading && !user) {
    redirect('/auth?redirect=/profile');
  }
  
  return (
    <div>
      <ProfileHeader user={user} userName={userName} />
      <ProfileTabs activeTab={activeTab} />
      {activeTab === 'overview' && <OverviewTab />}
      {activeTab === 'preferences' && <PreferencesTab />}
      {activeTab === 'saved' && <SavedTripsTab />}
      {activeTab === 'history' && <SearchHistoryTab />}
    </div>
  );
}
```

**Features**:
- Protected route (redirects to auth if not logged in)
- Tab-based navigation (URL query params: `?tab=preferences`)
- Responsive design
- Loading and error states

**Lines**: ~200 lines

---

### 5. Profile Header

**Location**: `components/features/user/ProfileHeader.tsx`

**Purpose**: Header section of profile page with user info and avatar.

**Features**:
- Large avatar display
- User name and email
- Edit profile button (future: opens edit modal)
- Back to search button

**Lines**: ~100 lines

---

### 6. Overview Tab

**Location**: `components/features/user/OverviewTab.tsx`

**Purpose**: Default tab showing user summary and quick stats.

**Content**:
- User information card
  - Name, email, account creation date
  - Account type (email/Google)
- Quick stats
  - Total searches performed
  - Saved trips count
  - Trips viewed
- Recent activity
  - Last 5 searches
  - Last 3 saved trips

**Lines**: ~150 lines

---

### 7. Preferences Tab

**Location**: `components/features/user/PreferencesTab.tsx`

**Purpose**: User preferences and settings management.

**Preferences to Manage**:
- **Language Preference** (Hebrew/English) - Future feature
- **Default Search Filters**
  - Preferred trip types
  - Preferred themes
  - Default budget range
  - Default duration range
- **Notification Preferences** - Future feature
  - Email notifications
  - Trip recommendations
- **Privacy Settings** - Future feature
  - Search history tracking
  - Analytics opt-out

**API Integration**:
- `GET /api/user/preferences` - Fetch user preferences
- `PUT /api/user/preferences` - Update user preferences

**Features**:
- Form-based interface
- Save/Cancel buttons
- Loading states
- Success/error messages
- Validation

**Lines**: ~200 lines

---

### 8. Saved Trips Tab

**Location**: `components/features/user/SavedTripsTab.tsx`

**Purpose**: Display and manage user's saved trips/favorites.

**Features**:
- List of saved trips (using `TripResultCard` component)
- Empty state when no saved trips
- Remove from saved functionality
- Filter/sort options (by date saved, trip type, etc.)
- Pagination (if many saved trips)

**API Integration**:
- `GET /api/user/saved-trips` - Fetch saved trips
- `POST /api/user/saved-trips` - Save a trip
- `DELETE /api/user/saved-trips/:id` - Remove saved trip

**Lines**: ~150 lines

---

### 9. Search History Tab

**Location**: `components/features/user/SearchHistoryTab.tsx`

**Purpose**: Display user's search history.

**Features**:
- List of past searches with filters applied
- Click to re-run search (navigate to `/search/results` with params)
- Clear history button
- Date/time of each search
- Results count for each search
- Empty state when no history

**API Integration**:
- `GET /api/user/search-history` - Fetch search history
- `DELETE /api/user/search-history` - Clear all history
- `DELETE /api/user/search-history/:id` - Remove specific search

**Data Source**: Can leverage existing Events API (`/api/events`) filtered by user_id and event_type='search'

**Lines**: ~150 lines

---

## Backend API Requirements

### New Endpoints Needed

#### User Preferences API

**Base Path**: `/api/user`

**Endpoints**:

1. **`GET /api/user/preferences`**
   - Returns user preferences
   - Requires authentication
   - Response:
   ```json
   {
     "success": true,
     "preferences": {
       "default_trip_types": [1, 3],
       "default_themes": [5, 10],
       "default_budget_min": 5000,
       "default_budget_max": 15000,
       "default_duration_min": 7,
       "default_duration_max": 14,
       "language": "he"
     }
   }
   ```

2. **`PUT /api/user/preferences`**
   - Updates user preferences
   - Requires authentication
   - Request body: Same structure as GET response
   - Response: Updated preferences

3. **`GET /api/user/saved-trips`**
   - Returns user's saved trips
   - Requires authentication
   - Query params: `page`, `limit`, `sort`
   - Response:
   ```json
   {
     "success": true,
     "count": 10,
     "data": [
       {
         "id": 123,
         "trip_occurrence_id": 517,
         "saved_at": "2025-01-15T10:30:00Z",
         "trip": { /* full trip object */ }
       }
     ]
   }
   ```

4. **`POST /api/user/saved-trips`**
   - Save a trip to user's favorites
   - Requires authentication
   - Request body: `{ "trip_occurrence_id": 517 }`
   - Response: Saved trip object

5. **`DELETE /api/user/saved-trips/:id`**
   - Remove saved trip
   - Requires authentication
   - Response: Success confirmation

6. **`GET /api/user/search-history`**
   - Returns user's search history
   - Requires authentication
   - Query params: `page`, `limit`
   - Response:
   ```json
   {
     "success": true,
     "count": 25,
     "data": [
       {
         "id": 456,
         "search_params": { /* search filters */ },
         "results_count": 10,
         "searched_at": "2025-01-15T10:30:00Z"
       }
     ]
   }
   ```

7. **`DELETE /api/user/search-history`**
   - Clear all search history
   - Requires authentication
   - Response: Success confirmation

8. **`DELETE /api/user/search-history/:id`**
   - Remove specific search from history
   - Requires authentication
   - Response: Success confirmation

### Database Schema Changes

**New Tables**:

1. **`user_preferences`**
   ```sql
   CREATE TABLE user_preferences (
     id SERIAL PRIMARY KEY,
     user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
     preferences JSONB NOT NULL DEFAULT '{}',
     created_at TIMESTAMP DEFAULT NOW(),
     updated_at TIMESTAMP DEFAULT NOW(),
     UNIQUE(user_id)
   );
   ```

2. **`saved_trips`**
   ```sql
   CREATE TABLE saved_trips (
     id SERIAL PRIMARY KEY,
     user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
     trip_occurrence_id INTEGER NOT NULL REFERENCES trip_occurrences(id) ON DELETE CASCADE,
     saved_at TIMESTAMP DEFAULT NOW(),
     UNIQUE(user_id, trip_occurrence_id)
   );
   ```

3. **`user_search_history`**
   ```sql
   CREATE TABLE user_search_history (
     id SERIAL PRIMARY KEY,
     user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
     search_params JSONB NOT NULL,
     results_count INTEGER,
     searched_at TIMESTAMP DEFAULT NOW()
   );
   CREATE INDEX idx_user_search_history_user_id ON user_search_history(user_id);
   CREATE INDEX idx_user_search_history_searched_at ON user_search_history(searched_at DESC);
   ```

**Note**: Search history can also be derived from Events API data, but a dedicated table provides better performance and structure.

## Implementation Plan

### Phase 1: Header Integration & User Menu (Foundation) - **HIGH PRIORITY**

**Estimated Time**: 6-8 hours  
**Risk Level**: Low-Medium

1. **Create Reusable UI Components**
   - `components/ui/Avatar.tsx` - Avatar component with initials fallback
   - `components/ui/DropdownMenu.tsx` - Reusable dropdown menu component
   - Test components in isolation

2. **Create User Menu Components**
   - `components/features/user/UserMenuButton.tsx` - Button with avatar
   - `components/features/user/UserDropdownMenu.tsx` - Dropdown menu
   - Integrate click-outside and keyboard navigation
   - Add accessibility features (ARIA, focus management)

3. **Update Header Component**
   - Modify `SearchPageHeader.tsx` to include `UserMenuButton`
   - Replace logout button with user menu button
   - Keep logout functionality in dropdown menu
   - Test responsive design

4. **Update useUser Hook**
   - Add `userEmail` to return value
   - Add `userAvatar` extraction from metadata
   - Ensure proper loading states

**Deliverables**:
- User menu button in header (top-right or top-left as per design)
- Dropdown menu with menu items
- Logout functionality preserved
- Responsive and accessible

---

### Phase 2: Profile Page Structure (Medium Priority)

**Estimated Time**: 8-10 hours  
**Risk Level**: Medium

1. **Create Profile Page Route**
   - `app/profile/page.tsx` - Main profile page
   - `app/profile/loading.tsx` - Loading state
   - `app/profile/error.tsx` - Error state
   - Protected route logic (redirect if not authenticated)

2. **Create Profile Components**
   - `components/features/user/ProfileHeader.tsx` - Profile header
   - `components/features/user/ProfileTabs.tsx` - Tab navigation
   - Tab components (OverviewTab, PreferencesTab, SavedTripsTab, SearchHistoryTab)
   - Use placeholder data initially

3. **Implement Tab Navigation**
   - URL-based tab switching (`?tab=preferences`)
   - Active tab highlighting
   - Smooth transitions

**Deliverables**:
- Profile page accessible at `/profile`
- Tab navigation working
- All tabs display (with placeholder content)
- Protected route working

---

### Phase 3: Backend API Implementation (High Priority)

**Estimated Time**: 12-16 hours  
**Risk Level**: Medium-High

1. **Database Migration**
   - Create migration file for new tables
   - Add indexes for performance
   - Test migration on development database

2. **Create User API Blueprint**
   - `backend/app/api/user/__init__.py`
   - `backend/app/api/user/routes.py`
   - Register blueprint in `main.py`

3. **Implement Endpoints**
   - User preferences endpoints (GET, PUT)
   - Saved trips endpoints (GET, POST, DELETE)
   - Search history endpoints (GET, DELETE)
   - Add authentication middleware
   - Add error handling and validation

4. **Create Service Layer**
   - `backend/app/services/user_service.py`
   - Business logic for user operations
   - Database operations

5. **Add Schemas**
   - `backend/app/schemas/user_schemas.py`
   - Pydantic models for request/response validation

**Deliverables**:
- All API endpoints implemented and tested
- Database tables created
- Authentication working
- API documentation updated

---

### Phase 4: Profile Page Content Integration (Medium Priority)

**Estimated Time**: 10-12 hours  
**Risk Level**: Medium

1. **Implement Overview Tab**
   - Fetch user stats from API
   - Display user information
   - Show recent activity
   - Add loading and error states

2. **Implement Preferences Tab**
   - Fetch current preferences
   - Form for editing preferences
   - Save functionality
   - Validation and error handling

3. **Implement Saved Trips Tab**
   - Fetch saved trips
   - Display using `TripResultCard` component
   - Remove functionality
   - Empty state

4. **Implement Search History Tab**
   - Fetch search history
   - Display search queries
   - Re-run search functionality
   - Clear history functionality

**Deliverables**:
- All tabs functional with real data
- API integration complete
- Error handling implemented
- Loading states working

---

### Phase 5: Polish & Enhancements (Low Priority)

**Estimated Time**: 6-8 hours  
**Risk Level**: Low

1. **UI/UX Improvements**
   - Animations and transitions
   - Better empty states
   - Improved loading skeletons
   - Mobile responsiveness refinements

2. **Additional Features**
   - Export search history (future)
   - Share saved trips (future)
   - Profile picture upload (future)
   - Email verification status display

3. **Testing**
   - Unit tests for components
   - Integration tests for API
   - E2E tests for user flows

4. **Documentation**
   - Update API documentation
   - Add component documentation
   - Update user guide

**Deliverables**:
- Polished UI/UX
- Additional features (as prioritized)
- Test coverage
- Updated documentation

---

## Design Specifications

### User Menu Button (Header)

**Position**: Top-right corner (or top-left as per user preference)

**Visual Design**:
- Circular avatar (32px-40px diameter)
- Border: 2px solid white/transparent
- Hover: Slight scale (1.05x) and shadow
- Active: Dropdown menu opens below

**States**:
- Default: Avatar/initials displayed
- Hover: Slight elevation, cursor pointer
- Active: Dropdown menu visible
- Loading: Skeleton/spinner overlay

### Dropdown Menu

**Position**: Below user button, aligned to right edge

**Dimensions**:
- Width: 280px-320px
- Max height: 400px (scrollable if needed)
- Padding: 8px

**Visual Design**:
- White background
- Shadow: Large elevation (similar to Google's menu)
- Border radius: 8px
- Animation: Fade in + slide down (200ms)

**Menu Items**:
- Height: 48px per item
- Padding: 12px 16px
- Hover: Light gray background (#f5f5f5)
- Icon: 20px, left-aligned
- Text: 14px, Hebrew font
- Divider: 1px solid #e0e0e0

### Profile Page Layout

**Header Section**:
- Background: Gradient (matching app theme)
- Avatar: Large (120px diameter)
- User name: 24px, bold
- Email: 16px, gray
- Padding: 40px

**Tabs Section**:
- Tab buttons: Horizontal row
- Active tab: Underline + color accent
- Inactive tabs: Gray text
- Spacing: 24px between tabs

**Content Section**:
- Max width: 1200px
- Padding: 24px
- Cards: White background, shadow, rounded corners

## Accessibility Requirements

1. **Keyboard Navigation**
   - Tab through menu items
   - Enter to activate
   - Escape to close dropdown
   - Arrow keys for navigation

2. **Screen Reader Support**
   - ARIA labels for all interactive elements
   - ARIA menu role for dropdown
   - ARIA expanded state
   - Descriptive text for icons

3. **Focus Management**
   - Focus trap in dropdown menu
   - Focus returns to button on close
   - Visible focus indicators

4. **Color Contrast**
   - WCAG AA compliance
   - Text contrast ratios meet standards

## Security Considerations

1. **Authentication**
   - All user endpoints require valid JWT token
   - Verify user_id matches authenticated user
   - Prevent access to other users' data

2. **Data Validation**
   - Validate all input on backend
   - Sanitize user preferences JSON
   - Rate limiting on write operations

3. **Privacy**
   - User data only accessible by owner
   - Search history can be cleared by user
   - Preferences stored securely

## Testing Strategy

### Unit Tests
- Avatar component (initials generation, image fallback)
- Dropdown menu (open/close, keyboard navigation)
- Profile tabs (tab switching, URL params)
- API hooks (data fetching, error handling)

### Integration Tests
- User menu button integration with header
- Profile page navigation flow
- API endpoint authentication
- Data persistence (save/delete operations)

### E2E Tests
- Complete user flow: Login → Open menu → Navigate to profile
- Save trip → View in saved trips tab
- Update preferences → Verify persistence
- Clear search history → Verify deletion

## Migration Strategy

### Option 1: Feature Flag (Recommended)
- Add feature flag for profile page
- Enable for beta users first
- Gradual rollout to all users

### Option 2: Direct Deployment
- Deploy all phases together
- Monitor for issues
- Quick rollback if needed

### Option 3: Incremental Rollout
- Deploy Phase 1 (header menu) first
- Gather feedback
- Deploy subsequent phases

## Success Metrics

1. **Adoption**
   - % of authenticated users accessing profile page
   - Average time spent on profile page
   - Most used tab (preferences vs saved trips)

2. **Engagement**
   - Number of saved trips per user
   - Preferences update frequency
   - Search history usage

3. **Performance**
   - Profile page load time < 2s
   - API response time < 500ms
   - No performance regressions

4. **User Satisfaction**
   - User feedback/surveys
   - Support ticket reduction
   - Feature requests

## Risks and Mitigation

### Risk 1: Performance Impact
**Issue**: Additional API calls and database queries  
**Mitigation**: 
- Implement caching for user preferences
- Paginate saved trips and search history
- Use database indexes
- Lazy load tab content

### Risk 2: Breaking Existing Functionality
**Issue**: Header changes might break existing flows  
**Mitigation**:
- Thorough testing of header integration
- Keep logout functionality working
- Maintain backward compatibility

### Risk 3: Database Migration Issues
**Issue**: Migration might fail in production  
**Mitigation**:
- Test migration on staging first
- Backup database before migration
- Rollback plan ready
- Gradual migration if needed

### Risk 4: User Adoption
**Issue**: Users might not discover or use profile page  
**Mitigation**:
- Prominent user menu button
- Onboarding tooltips (future)
- Email notifications for new features
- Clear value proposition

## Alternatives Considered

### Alternative 1: Modal-Based Profile
**Rejected**: Less discoverable, doesn't feel like a dedicated space

### Alternative 2: Sidebar Navigation
**Rejected**: Doesn't fit current header design, takes up screen space

### Alternative 3: Separate Profile App
**Rejected**: Over-engineering, adds complexity

## Dependencies

### Frontend Dependencies
- Existing: Next.js, React, Supabase client, Tailwind CSS
- New: None (use existing stack)

### Backend Dependencies
- Existing: Flask, SQLAlchemy, PostgreSQL
- New: None (use existing stack)

### External Services
- Supabase (authentication, user management)
- No new services required

## Timeline Estimate

**Total Estimated Time**: 42-54 hours (5-7 working days)

**Breakdown**:
- Phase 1: 6-8 hours (1 day)
- Phase 2: 8-10 hours (1-1.5 days)
- Phase 3: 12-16 hours (1.5-2 days)
- Phase 4: 10-12 hours (1.5 days)
- Phase 5: 6-8 hours (1 day)

**Recommended Schedule**:
- Week 1: Phases 1-2 (Header + Profile Page Structure)
- Week 2: Phase 3 (Backend API)
- Week 3: Phase 4 (Content Integration)
- Week 4: Phase 5 (Polish & Testing)

## Next Steps

1. **Review and Approval**: Get stakeholder buy-in
2. **Design Review**: Finalize UI/UX design mockups
3. **Database Design Review**: Validate schema design
4. **Create Tickets**: Break down into actionable tasks
5. **Set Timeline**: Schedule implementation
6. **Start Phase 1**: Begin with header integration

---

## Appendix

### A. User Menu Button Placement Options

**Option 1: Top-Right (Google-style)**
- Most common pattern
- Matches user expectations
- Doesn't interfere with logo

**Option 2: Top-Left**
- As requested by user
- Replaces current home/logout buttons
- Requires layout adjustment

**Option 3: Center-Right**
- Next to user greeting
- Keeps user context together
- Less conventional

**Recommendation**: Option 1 (Top-Right) for familiarity, but can implement Option 2 per user preference.

### B. Profile Page URL Structure

- `/profile` - Overview tab (default)
- `/profile?tab=preferences` - Preferences tab
- `/profile?tab=saved` - Saved trips tab
- `/profile?tab=history` - Search history tab

Alternative: `/profile/preferences`, `/profile/saved`, etc. (requires Next.js dynamic routes)

### C. Future Enhancements

1. **Profile Picture Upload**
   - Upload to Supabase Storage
   - Crop/resize functionality
   - Avatar preview

2. **Email Preferences**
   - Newsletter subscription
   - Trip recommendation emails
   - Marketing preferences

3. **Social Features**
   - Share saved trips
   - Follow other users
   - Trip reviews/ratings

4. **Advanced Preferences**
   - Accessibility settings
   - Theme preferences (dark mode)
   - Notification channels

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Author**: Senior Developer  
**Status**: Proposal - Pending Approval
