# Tracking Service Refactor Proposal

**Status:** Proposed  
**Author:** AI Assistant  
**Date:** 2026-01-20  
**Related Files:** `frontend/src/services/tracking.service.ts`

---

## Executive Summary

The current `tracking.service.ts` file has grown to 619 lines and handles multiple concerns (identity management, device detection, session management, event queuing, and high-level tracking functions). This proposal recommends splitting it into a modular structure with 9 focused files for better maintainability, testability, and developer experience.

---

## Problem Statement

### Current Issues

1. **File Size**: 619 lines make it difficult to navigate and understand
2. **Multiple Responsibilities**: Single file handles 6+ distinct concerns
3. **Testing Complexity**: Hard to mock and test individual components in isolation
4. **Merge Conflicts**: Multiple developers working on tracking features causes conflicts
5. **Cognitive Load**: Developers must understand entire file to make small changes
6. **Code Discovery**: Finding specific functionality requires scrolling through large file

### Impact

- Slower feature development
- Higher bug risk due to complexity
- Difficult onboarding for new developers
- Reduced code maintainability

---

## Proposed Solution

### New Directory Structure

```
frontend/src/services/tracking/
├── index.ts                    # Main export (re-exports all public APIs)
├── types.ts                    # Type definitions
├── constants.ts                # Configuration constants
├── identity.ts                 # User/session ID management
├── device.ts                   # Device detection
├── session.ts                  # Session initialization
├── queue.ts                    # Event queue and batching
├── events.ts                   # High-level tracking functions
└── lifecycle.ts                # Page load/unload handlers
```

### File Breakdown

#### 1. `types.ts` (~40 lines)

**Purpose:** Centralize all TypeScript type definitions

**Contents:**
- `EventType` - Union type of all valid event types
- `ClickSource` - Union type for click attribution
- `DeviceType` - Device type enum
- `TrackingEvent` - Core event interface

**Why Separate:**
- Types are imported across multiple modules
- Easy to find and update type definitions
- Can be imported without importing implementation code

---

#### 2. `constants.ts` (~20 lines)

**Purpose:** Configuration values and magic numbers

**Contents:**
- `ANONYMOUS_ID_KEY = 'smartrip_anonymous_id'`
- `SESSION_ID_KEY = 'smartrip_session_id'`
- `SESSION_EXPIRY_KEY = 'smartrip_session_expiry'`
- `SESSION_TIMEOUT_MS = 30 * 60 * 1000`
- `BATCH_SIZE = 10`
- `BATCH_INTERVAL_MS = 5000`

**Why Separate:**
- Single source of truth for configuration
- Easy to adjust behavior without touching logic
- Can be imported by test files for validation

---

#### 3. `identity.ts` (~60 lines)

**Purpose:** Manage anonymous user IDs and session IDs

**Public API:**
- `getAnonymousId(): string` - Get/create persistent anonymous ID
- `getSessionId(): string` - Get/create session ID with expiry
- `getTrackingIds(): { anonymousId, sessionId }` - Get both IDs

**Internal:**
- localStorage read/write logic
- Session expiry validation
- UUID generation

**Why Separate:**
- Clear boundary: identity management is a distinct concern
- Can be tested independently with localStorage mocks
- Reusable across different tracking scenarios

---

#### 4. `device.ts` (~20 lines)

**Purpose:** Detect device type from window width

**Public API:**
- `detectDeviceType(): DeviceType` - Returns 'mobile' | 'tablet' | 'desktop'

**Breakpoints:**
- Mobile: < 768px
- Tablet: 768px - 1023px
- Desktop: >= 1024px

**Why Separate:**
- Simple, focused utility
- Easy to test with different window widths
- May be used by other modules in the future

---

#### 5. `session.ts` (~50 lines)

**Purpose:** Initialize tracking session with backend

**Public API:**
- `initializeSession(): Promise<void>` - Start session with backend

**Internal:**
- Session initialization state flag
- API call to `/api/session/start`
- Error handling and graceful degradation

**Dependencies:**
- `identity.ts` - Get anonymous ID and session ID
- `device.ts` - Get device type
- `@/api/events` - API transport layer

**Why Separate:**
- Session initialization is a one-time setup operation
- Contains async logic separate from event tracking
- Can be tested with mock API responses

---

#### 6. `queue.ts` (~150 lines)

**Purpose:** Core event tracking, queuing, and batching logic

**Public API:**
- `trackEvent(eventType, options)` - Queue a single event
- `flushEvents(): Promise<void>` - Send queued events immediately
- `flushPendingEvents(): void` - Synchronous flush for page unload

**Internal:**
- `eventQueue: TrackingEvent[]` - Event buffer
- `batchTimeout: NodeJS.Timeout` - Batch timer
- Batching logic (size and time-based)
- sendBeacon support for page unload

**Dependencies:**
- `identity.ts` - Get tracking IDs
- `session.ts` - Ensure session initialized
- `@/api/events` - Batch event API
- `@/lib/supabaseClient` - Get user email if authenticated

**Why Separate:**
- Core business logic of the tracking system
- Most complex module - benefits from isolation
- Testable with mock APIs and timers

---

#### 7. `events.ts` (~120 lines)

**Purpose:** High-level convenience functions for tracking specific events

**Public API:**
- `trackPageView(pageName)`
- `trackSearchSubmit(preferences, searchType)`
- `trackResultsView(resultCount, ...)`
- `trackImpression(tripId, position, score, source)`
- `trackTripClick(tripId, position, score, source, timeToClickMs?)`
- `trackTripView(tripId)`
- `trackDwellTime(tripId, durationSeconds)`
- `trackFilterChange(filterName, oldValue, newValue)`
- `trackFilterRemoved(filterName, oldValue)`
- `trackSaveTrip(tripId)`
- `trackUnsaveTrip(tripId)`
- `trackWhatsAppContact(tripId)`
- `trackPhoneContact(tripId)`
- `trackBookingStart(tripId)`

**Dependencies:**
- `queue.ts` - Call `trackEvent()` with formatted data

**Why Separate:**
- Provides ergonomic API for developers
- Easy to add new event types without touching core logic
- Self-documenting: each function shows what can be tracked
- Can be tested by verifying `trackEvent()` calls

---

#### 8. `lifecycle.ts` (~30 lines)

**Purpose:** Setup event listeners for page load and unload

**Contents:**
- `beforeunload` listener → `flushPendingEvents()`
- `pagehide` listener → `flushPendingEvents()`
- `load` listener → `initializeSession()`
- SSR safety checks

**Dependencies:**
- `session.ts` - Initialize on load
- `queue.ts` - Flush on unload

**Why Separate:**
- Browser lifecycle is distinct from tracking logic
- Can be disabled for testing
- Clear entry point for setup

---

#### 9. `index.ts` (~30 lines)

**Purpose:** Main export file maintaining backward compatibility

**Contents:**
```typescript
// Re-export types
export type { EventType, ClickSource, DeviceType, TrackingEvent } from './types';

// Re-export identity functions
export { getAnonymousId, getSessionId, getTrackingIds } from './identity';

// Re-export device detection
export { detectDeviceType } from './device';

// Re-export session management
export { initializeSession } from './session';

// Re-export queue functions
export { trackEvent, flushPendingEvents } from './queue';

// Re-export all high-level tracking functions
export {
  trackPageView,
  trackSearchSubmit,
  trackResultsView,
  trackImpression,
  trackTripClick,
  trackTripView,
  trackDwellTime,
  trackFilterChange,
  trackFilterRemoved,
  trackSaveTrip,
  trackUnsaveTrip,
  trackWhatsAppContact,
  trackPhoneContact,
  trackBookingStart,
} from './events';

// Setup lifecycle handlers (auto-runs on import)
import './lifecycle';
```

**Why Needed:**
- Maintains existing import paths
- Single entry point for consumers
- Controls public API surface

---

## Implementation Plan

### Phase 1: Create New Structure (No Breaking Changes)

1. Create `frontend/src/services/tracking/` directory
2. Create all 9 files with proper content
3. Add `index.ts` re-exports
4. Keep `tracking.service.ts` as-is (temporarily)

**Testing:** Verify new structure works in isolation

### Phase 2: Update Imports

1. Update all imports to use new structure:
   ```typescript
   // Old
   import { trackPageView } from '@/services/tracking.service';
   
   // New
   import { trackPageView } from '@/services/tracking';
   ```

2. Search and replace across codebase:
   ```bash
   find frontend/src -name "*.ts" -o -name "*.tsx" | \
     xargs sed -i "s/@\/services\/tracking.service/@\/services\/tracking/g"
   ```

**Testing:** Run full test suite, verify no broken imports

### Phase 3: Remove Old File

1. Delete `frontend/src/services/tracking.service.ts`
2. Verify no references remain

**Testing:** Build passes, no import errors

### Phase 4: Documentation

1. Update architecture docs
2. Add JSDoc comments to public APIs
3. Create usage examples

---

## Migration Impact

### Breaking Changes

**None** - The public API remains identical

### Import Changes

```typescript
// Before (still works during migration)
import { trackPageView } from '@/services/tracking.service';

// After (preferred)
import { trackPageView } from '@/services/tracking';
```

### Code Changes Required

- Update ~30 import statements across the codebase
- No logic changes needed

---

## Benefits

### 1. Improved Maintainability

- Each file has single responsibility (SRP)
- Easy to locate specific functionality
- Reduced file size (max ~150 lines vs 619 lines)

### 2. Better Testability

- Mock individual modules in isolation
- Test identity management without event logic
- Test event queuing without session logic
- Faster test execution (can run in parallel)

### 3. Enhanced Developer Experience

- Easier code navigation
- Clearer mental model of the system
- Self-documenting structure
- Faster onboarding for new developers

### 4. Reduced Merge Conflicts

- Changes to event types don't conflict with queue logic
- Multiple developers can work on different modules
- Smaller files = fewer conflict markers

### 5. Better Tree Shaking

- Unused modules can be eliminated in production builds
- Smaller bundle size if only using subset of functionality

### 6. Future-Proof Architecture

- Easy to add new event types (edit `events.ts` only)
- Easy to swap implementations (e.g., different queue strategy)
- Clear extension points for new features

---

## Risks & Mitigations

### Risk 1: Import Path Confusion

**Description:** Developers might not know which path to use

**Mitigation:**
- Deprecation warning in old file
- Update ESLint to prefer new imports
- Code review checklist item

### Risk 2: Breaking Tests

**Description:** Tests might rely on internal implementation

**Mitigation:**
- Run full test suite before/after migration
- Keep old file temporarily during transition
- Rollback plan if tests fail

### Risk 3: Circular Dependencies

**Description:** New modules might import each other circularly

**Mitigation:**
- Clear dependency graph (defined above)
- ESLint rule to prevent circular imports
- Review module boundaries carefully

---

## Testing Strategy

### Unit Tests

Each module gets isolated unit tests:

```typescript
// identity.test.ts
describe('getAnonymousId', () => {
  it('creates new ID if none exists', () => { ... });
  it('returns existing ID from localStorage', () => { ... });
});

// queue.test.ts
describe('trackEvent', () => {
  it('queues event for batching', () => { ... });
  it('flushes when batch size reached', () => { ... });
});
```

### Integration Tests

Test module interactions:

```typescript
// tracking.integration.test.ts
describe('Tracking System', () => {
  it('initializes session and tracks events', async () => {
    await initializeSession();
    trackPageView('home');
    // Verify API called correctly
  });
});
```

### Backward Compatibility Tests

Ensure old imports still work during migration:

```typescript
describe('Legacy Imports', () => {
  it('imports from tracking.service still work', () => {
    const { trackPageView } = require('@/services/tracking.service');
    expect(trackPageView).toBeDefined();
  });
});
```

---

## Alternative Approaches Considered

### Alternative 1: Keep Single File

**Pros:**
- No migration needed
- All code in one place

**Cons:**
- Continues to grow (already 619 lines)
- Testing remains difficult
- Merge conflicts continue

**Decision:** Rejected - technical debt will worsen

### Alternative 2: Split into 2-3 Larger Files

**Example:**
- `tracking-core.ts` (identity, session, queue)
- `tracking-events.ts` (high-level functions)

**Pros:**
- Smaller migration
- Fewer files to manage

**Cons:**
- Still mixing concerns in "core" file
- Doesn't fully solve the problem
- Will need to split again later

**Decision:** Rejected - doesn't go far enough

### Alternative 3: Move to Separate Package

**Example:** Create `@smarttrip/tracking` npm package

**Pros:**
- Complete isolation
- Reusable across projects
- Enforced API boundaries

**Cons:**
- Overkill for current needs
- Adds build complexity
- Harder to make rapid changes

**Decision:** Rejected - too much overhead for internal module

---

## Success Metrics

### Code Quality

- File size reduced: 619 lines → max 150 lines per file
- Cyclomatic complexity reduced
- Test coverage maintained or improved (target: >80%)

### Developer Experience

- Code navigation time reduced (measured by time to find function)
- Fewer merge conflicts in tracking code
- Faster onboarding (measured by time for new dev to understand system)

### Performance

- No performance regression in tracking events
- Bundle size unchanged or reduced (via tree shaking)

---

## Timeline

### Week 1: Preparation

- [ ] Review and approve this proposal
- [ ] Create implementation plan
- [ ] Set up test environment

### Week 2: Implementation

- [ ] Day 1-2: Create new file structure
- [ ] Day 3-4: Write unit tests for new modules
- [ ] Day 5: Update imports across codebase

### Week 3: Validation

- [ ] Run full test suite
- [ ] Manual QA testing
- [ ] Performance testing

### Week 4: Deployment

- [ ] Deploy to staging
- [ ] Monitor for errors
- [ ] Deploy to production
- [ ] Remove old file

---

## Conclusion

The tracking service has served well but has outgrown its single-file structure. Splitting it into 9 focused modules will:

1. Make the code easier to understand and maintain
2. Improve testability and reduce bugs
3. Enable parallel development without conflicts
4. Set up a scalable architecture for future growth

The migration is low-risk with no breaking changes to the public API. The benefits far outweigh the one-time cost of refactoring.

**Recommendation:** Approve and implement this refactor in the next sprint.

---

## Appendix A: Dependency Graph

```
types.ts
  ↓
constants.ts
  ↓
device.ts

identity.ts (uses constants.ts)
  ↓
session.ts (uses identity.ts, device.ts)
  ↓
queue.ts (uses identity.ts, session.ts, types.ts, constants.ts)
  ↓
events.ts (uses queue.ts, types.ts)
  ↓
lifecycle.ts (uses session.ts, queue.ts)
  ↓
index.ts (re-exports all)
```

**Rule:** Dependencies flow downward only (no circular dependencies)

---

## Appendix B: File Size Comparison

| File | Lines | Responsibility |
|------|-------|----------------|
| **Current** | | |
| tracking.service.ts | 619 | Everything |
| **Proposed** | | |
| types.ts | 40 | Type definitions |
| constants.ts | 20 | Configuration |
| device.ts | 20 | Device detection |
| identity.ts | 60 | ID management |
| session.ts | 50 | Session init |
| queue.ts | 150 | Event queuing |
| events.ts | 120 | High-level API |
| lifecycle.ts | 30 | Setup listeners |
| index.ts | 30 | Re-exports |
| **Total** | **520** | *99 lines saved via removal of duplication* |

---

## Appendix C: Public API Reference

All functions that must remain accessible from `@/services/tracking`:

**Types:**
- `EventType`, `ClickSource`, `DeviceType`, `TrackingEvent`

**Core Functions:**
- `trackEvent()`
- `flushPendingEvents()`

**Identity:**
- `getAnonymousId()`
- `getSessionId()`
- `getTrackingIds()`

**Session:**
- `initializeSession()`

**Device:**
- `detectDeviceType()`

**High-Level Tracking:**
- `trackPageView()`
- `trackSearchSubmit()`
- `trackResultsView()`
- `trackImpression()`
- `trackTripClick()`
- `trackTripView()`
- `trackDwellTime()`
- `trackFilterChange()`
- `trackFilterRemoved()`
- `trackSaveTrip()`
- `trackUnsaveTrip()`
- `trackWhatsAppContact()`
- `trackPhoneContact()`
- `trackBookingStart()`

**Total:** 24 exported items (no change from current API)
