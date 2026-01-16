# Design Patterns in SmartTrip Project

## Table of Contents
1. [Backend Patterns](#backend-patterns)
2. [Frontend Patterns](#frontend-patterns)
3. [Architectural Patterns](#architectural-patterns)
4. [Summary](#summary)

---

## Backend Patterns

### 1. Singleton Pattern

**Location**: `backend/events/service.py`

**Implementation**:
```python
_event_service = None

def get_event_service() -> EventService:
    global _event_service
    if _event_service is None:
        _event_service = EventService()
    return _event_service
```

**Why Singleton Instead of Alternatives**:

- **Alternative: Multiple Instances** - Rejected because event tracking requires consistent state (session management, user resolution) across all API endpoints. Multiple instances would lead to inconsistent tracking data.
- **Alternative: Dependency Injection Container** - Not chosen because the project size doesn't warrant a full DI framework. Singleton provides simplicity while maintaining the single-instance guarantee needed for event tracking consistency.
- **Alternative: Module-level Instance** - The lazy initialization pattern (create on first access) is preferred over module-level instantiation to allow graceful initialization and better testability.

**Benefits**:
- Ensures consistent event tracking state across the application
- Prevents duplicate session management
- Simplifies access without requiring dependency injection

---

### 2. Service Layer Pattern

**Location**: `backend/events/service.py` - `EventService` class

**Implementation**:
- Business logic separated from API endpoints
- `EventService` handles: user resolution, session management, event validation, trip interactions

**Why Service Layer Instead of Alternatives**:

- **Alternative: Fat Controllers** - Rejected because it would mix HTTP concerns (request/response) with business logic, making code harder to test and maintain. Service layer allows testing business logic without HTTP mocks.
- **Alternative: Active Record Pattern** - Not suitable because event tracking involves complex operations across multiple entities (User, Session, Event, TripInteraction). Service layer orchestrates these operations.
- **Alternative: Domain-Driven Design (DDD)** - Not chosen because the domain complexity doesn't require full DDD. Service layer provides sufficient separation without over-engineering.

**Benefits**:
- Business logic is testable independently of HTTP layer
- Reusable across different interfaces (REST API, background jobs)
- Clear separation of concerns: API handles HTTP, Service handles business rules

---

### 3. Repository Pattern (Implicit)

**Location**: SQLAlchemy models in `backend/models_v2.py`

**Implementation**:
- SQLAlchemy ORM models act as repositories
- Models like `TripTemplate`, `TripOccurrence`, `User` provide data access methods

**Why Implicit Repository Instead of Alternatives**:

- **Alternative: Explicit Repository Classes** - Not implemented because SQLAlchemy ORM already provides repository-like functionality (query methods, relationships). Adding explicit repositories would create unnecessary abstraction layers.
- **Alternative: Data Access Objects (DAO)** - SQLAlchemy models already serve this purpose. Creating separate DAOs would duplicate ORM functionality.
- **Alternative: ActiveRecord Pattern** - SQLAlchemy uses Unit of Work pattern, which is more flexible than ActiveRecord for complex transactions involving multiple entities.

**Benefits**:
- Leverages SQLAlchemy's built-in capabilities without additional abstraction
- Reduces code duplication
- Models serve dual purpose: domain objects and data access

---

### 4. Data Mapper Pattern

**Location**: SQLAlchemy ORM throughout the backend

**Implementation**:
- Maps database tables to Python objects
- Handles relationships (one-to-many, many-to-many)
- Manages object identity and change tracking

**Why Data Mapper Instead of Alternatives**:

- **Alternative: Active Record** - Rejected because Active Record couples objects to database, making complex queries and transactions harder. Data Mapper separates persistence logic from domain objects.
- **Alternative: Table Data Gateway** - Not suitable because it works at table level, while we need object-level mapping with relationships. Data Mapper handles complex object graphs better.
- **Alternative: Row Data Gateway** - Too low-level; doesn't handle relationships well.

**Benefits**:
- Objects can exist independently of database schema
- Better handling of complex relationships (TripTemplate → TripOccurrence → Guide)
- Unit of Work pattern (SQLAlchemy sessions) enables efficient batch operations

---

### 5. Factory Pattern

**Location**: `backend/database.py`

**Implementation**:
```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)
```

**Why Factory Pattern Instead of Alternatives**:

- **Alternative: Direct Engine Usage** - Rejected because each request needs its own session. Factory pattern ensures proper session lifecycle management (create, use, close).
- **Alternative: Singleton Sessions** - Not thread-safe and causes transaction issues. Factory creates new sessions per request/thread.
- **Alternative: Dependency Injection** - Factory pattern is simpler and integrates well with Flask's request lifecycle. DI would require framework integration.

**Benefits**:
- Ensures thread-safe database sessions
- Proper session lifecycle management
- Scoped sessions prevent connection leaks

---

### 6. Blueprint Pattern (Flask)

**Location**: `backend/events/api.py`, `backend/api_v2.py`

**Implementation**:
- Flask blueprints (`events_bp`, `api_v2_bp`) organize routes into modules
- Each blueprint has its own URL prefix

**Why Blueprint Pattern Instead of Alternatives**:

- **Alternative: All Routes in app.py** - Rejected because it becomes unmaintainable as routes grow. Blueprints enable modular organization.
- **Alternative: Separate Flask Apps** - Not necessary because we need shared configuration and middleware. Blueprints provide modularity within a single app.
- **Alternative: Router Classes** - Blueprints are Flask's native pattern, well-integrated with the framework. Custom routers would require more boilerplate.

**Benefits**:
- Modular route organization (events, v2 API, etc.)
- Easy to add/remove features
- Maintains shared application context and configuration

---

### 7. Adapter Pattern

**Location**: `backend/api_v2.py` - `format_occurrence_as_trip()` function

**Implementation**:
- Converts new schema (TripOccurrence + TripTemplate) to legacy format (Trip)
- Provides backward compatibility for frontend

**Why Adapter Pattern Instead of Alternatives**:

- **Alternative: Breaking Changes** - Rejected because it would require immediate frontend rewrite. Adapter allows gradual migration.
- **Alternative: Versioned Endpoints Only** - Adapter pattern provides smooth transition. Frontend can migrate at its own pace.
- **Alternative: Duplicate Endpoints** - Adapter reuses new schema, avoiding code duplication. Separate endpoints would duplicate business logic.

**Benefits**:
- Enables incremental migration (backward compatible)
- Reuses new schema implementation
- No frontend breaking changes during transition

---

### 8. Strategy Pattern (Scoring Algorithm)

**Location**: `backend/api_v2.py` - Recommendation scoring logic

**Implementation**:
- Different scoring strategies: theme matching, difficulty, budget, duration, geography
- Configurable weights (`SCORING_WEIGHTS`) allow strategy modification

**Why Strategy Pattern Instead of Alternatives**:

- **Alternative: Hardcoded Scoring Logic** - Rejected because scoring rules need frequent tuning. Strategy pattern with configurable weights allows adjustments without code changes.
- **Alternative: Rule Engine** - Over-engineered for current needs. Strategy pattern with weights provides flexibility without complexity.
- **Alternative: Multiple Scoring Classes** - Current implementation uses strategy-like configurable weights. Full class-based strategy would add unnecessary complexity.

**Benefits**:
- Easy to adjust scoring weights without code changes
- Testable scoring components
- Clear separation of scoring logic from filtering logic

---

## Frontend Patterns

### 1. Provider Pattern (Context API)

**Location**: `src/lib/dataStore.tsx`

**Implementation**:
- `DataStoreProvider` wraps application
- Provides global state via React Context
- Custom hooks (`useDataStore`, `useCountries`, etc.) consume context

**Why Provider Pattern Instead of Alternatives**:

- **Alternative: Prop Drilling** - Rejected because reference data (countries, trip types, tags) is needed throughout the app. Prop drilling would be cumbersome and error-prone.
- **Alternative: Global State Library (Redux)** - Not chosen because the state is simple (reference data, loading states). Context API is sufficient and reduces dependencies.
- **Alternative: Server State Library (React Query)** - Reference data needs to be available immediately on client-side. Provider pattern provides instant access without network requests.
- **Alternative: Local Storage Only** - Provider pattern provides reactive updates and loading states, which localStorage doesn't provide.

**Benefits**:
- Centralized reference data access
- Automatic re-renders when data updates
- Type-safe with TypeScript
- No external dependencies (uses React built-in Context)

---

### 2. Custom Hooks Pattern

**Location**: `src/lib/useTracking.ts`, `src/lib/dataStore.tsx`

**Implementation**:
- Multiple custom hooks: `usePageView()`, `useTripDwellTime()`, `useImpressionTracking()`, `useResultsTracking()`, `useFilterTracking()`
- Each hook encapsulates specific tracking logic

**Why Custom Hooks Instead of Alternatives**:

- **Alternative: Component Logic in Components** - Rejected because tracking logic is reusable across components. Custom hooks enable code reuse.
- **Alternative: Higher-Order Components (HOCs)** - Hooks are more flexible and don't create component nesting. Hooks provide better composition.
- **Alternative: Render Props** - Hooks provide cleaner API and better TypeScript support. Render props create callback nesting.
- **Alternative: Class Components with Mixins** - Hooks work with functional components, which are React's recommended approach. Mixins are deprecated.

**Benefits**:
- Reusable logic across components
- Clean component code (logic separated from UI)
- Easy to test hooks independently
- Composable (hooks can use other hooks)

---

### 3. Observer Pattern

**Location**: `src/lib/useTracking.ts` - `useImpressionTracking()` hook

**Implementation**:
- `IntersectionObserver` API for viewport visibility detection
- Observes when trip cards become visible

**Why Observer Pattern Instead of Alternatives**:

- **Alternative: Scroll Event Listeners** - Rejected because scroll events fire frequently and impact performance. IntersectionObserver is more efficient and browser-optimized.
- **Alternative: Manual Visibility Calculations** - Observer pattern is more reliable across browsers and handles edge cases (iframes, transforms) automatically.
- **Alternative: Third-party Libraries** - Native IntersectionObserver is well-supported and doesn't require external dependencies.

**Benefits**:
- Efficient viewport detection (browser-optimized)
- Automatic handling of edge cases
- No performance impact from scroll events
- Clean API with threshold configuration

---

### 4. Singleton Pattern (Module State)

**Location**: `src/lib/tracking.ts`

**Implementation**:
- Module-level state: `eventQueue`, `batchTimeout`, `sessionInitialized`
- Single instance of tracking state across the application

**Why Singleton Instead of Alternatives**:

- **Alternative: Per-Component State** - Rejected because event batching requires shared queue. Per-component state would prevent batching efficiency.
- **Alternative: Context Provider** - Not necessary because tracking state doesn't need to trigger re-renders. Module-level singleton is simpler and more efficient.
- **Alternative: Redux Store** - Overkill for simple queue state. Module singleton provides necessary state sharing without complexity.

**Benefits**:
- Single event queue enables efficient batching
- Shared session state across all tracking calls
- No re-renders triggered (performance benefit)
- Simple implementation without framework overhead

---

### 5. Facade Pattern

**Location**: `src/lib/tracking.ts`

**Implementation**:
- High-level functions: `trackPageView()`, `trackTripClick()`, `trackImpression()`
- Hides complexity of batching, queueing, session management

**Why Facade Pattern Instead of Alternatives**:

- **Alternative: Direct Queue Access** - Rejected because components shouldn't know about batching logic. Facade provides simple API.
- **Alternative: Class-based API** - Functions are simpler to use and don't require instantiation. Facade functions are more convenient.
- **Alternative: Exposed Internal Functions** - Facade hides implementation details (batching, queueing), allowing internal changes without affecting callers.

**Benefits**:
- Simple API for components (just call `trackPageView()`)
- Hides implementation complexity (batching, queueing, session)
- Easy to change internal implementation
- Consistent interface across all tracking functions

---

### 6. Module Pattern

**Location**: Multiple TypeScript modules (`tracking.ts`, `api.ts`, `imageUtils.ts`)

**Implementation**:
- Encapsulated modules with explicit exports
- Private implementation details (not exported)
- Public API via exports

**Why Module Pattern Instead of Alternatives**:

- **Alternative: Global Namespace** - Rejected because it pollutes global scope and causes naming conflicts. Modules provide namespace isolation.
- **Alternative: Classes for Everything** - Not necessary for utility functions. Module pattern is lighter-weight and more appropriate for stateless utilities.
- **Alternative: Namespace Objects** - ES6 modules provide better tree-shaking and static analysis. TypeScript integrates well with ES6 modules.

**Benefits**:
- Namespace isolation (no global pollution)
- Clear public API (exports)
- Tree-shaking support (unused exports removed)
- TypeScript type checking across modules

---

### 7. Event Batching Pattern

**Location**: `src/lib/tracking.ts`

**Implementation**:
- Events queued in `eventQueue`
- Batched by size (10 events) or time (5 seconds)
- Single network request per batch

**Why Event Batching Instead of Alternatives**:

- **Alternative: Send Each Event Immediately** - Rejected because it creates network overhead (many small requests). Batching reduces network requests significantly.
- **Alternative: Send on Page Unload Only** - Risk of losing events if page closes unexpectedly. Batching provides balance: efficiency + reliability.
- **Alternative: Fixed Interval Batching** - Current implementation uses both size and time thresholds, which is more efficient (send when queue full OR after timeout).

**Benefits**:
- Reduces network requests (10x fewer for typical usage)
- Better performance (fewer HTTP requests)
- Still sends events promptly (5-second timeout)
- Uses `sendBeacon` for page unload reliability

---

## Architectural Patterns

### 1. Layered Architecture

**Implementation**:
- **API Layer**: Flask blueprints handle HTTP requests/responses
- **Service Layer**: Business logic (EventService, recommendation scoring)
- **Data Layer**: SQLAlchemy models and database access

**Why Layered Architecture Instead of Alternatives**:

- **Alternative: Monolithic Structure** - Rejected because mixing concerns makes code hard to test and maintain. Layers provide clear boundaries.
- **Alternative: Microservices** - Not necessary for current scale. Layered architecture provides separation without operational complexity.
- **Alternative: Hexagonal Architecture** - Over-engineered for current needs. Layered architecture provides sufficient structure.

**Benefits**:
- Clear separation of concerns
- Testable layers (mock data layer, test service layer)
- Easy to understand and navigate codebase
- Allows independent evolution of layers

---

### 2. RESTful API Pattern

**Location**: All API endpoints

**Implementation**:
- Standard HTTP methods (GET, POST)
- Resource-based URLs (`/api/trips`, `/api/events`)
- JSON request/response format

**Why RESTful Instead of Alternatives**:

- **Alternative: GraphQL** - Not chosen because REST is simpler for current use cases. GraphQL adds complexity (schema, resolvers) without clear benefits for this project.
- **Alternative: RPC-style (XML-RPC, JSON-RPC)** - REST is more standard and tool-friendly. RPC is less intuitive for resource-oriented operations.
- **Alternative: SOAP** - Too verbose and complex. REST with JSON is simpler and more modern.

**Benefits**:
- Standard, well-understood pattern
- Good tooling support (browsers, Postman, etc.)
- Cacheable (GET requests)
- Easy to document and understand

---

### 3. Database Connection Pooling

**Location**: `backend/database.py`

**Implementation**:
- SQLAlchemy engine with connection pooling
- Configurable pool size based on connection type (pooler vs direct)

**Why Connection Pooling Instead of Alternatives**:

- **Alternative: New Connection Per Request** - Rejected because creating connections is expensive. Pooling reuses connections, dramatically improving performance.
- **Alternative: Single Shared Connection** - Not thread-safe and causes blocking. Pool allows concurrent requests.
- **Alternative: Fixed Pool Size** - Current implementation adjusts pool size based on connection type (pooler needs smaller pools), which is more efficient.

**Benefits**:
- Reuses expensive database connections
- Handles concurrent requests efficiently
- Prevents connection exhaustion
- Configurable based on infrastructure (pooler vs direct)

---

## Summary

### Pattern Selection Philosophy

The SmartTrip project uses a pragmatic approach to design patterns:

1. **Choose simplicity over complexity**: Patterns are used when they provide clear benefits, not for the sake of using patterns.

2. **Leverage framework capabilities**: SQLAlchemy's ORM provides repository/mapper patterns implicitly, so explicit implementations aren't needed.

3. **Support incremental migration**: Adapter pattern enables schema migration without breaking changes.

4. **Performance considerations**: Event batching, connection pooling, and Observer pattern are chosen for performance benefits.

5. **Type safety and developer experience**: TypeScript modules and React hooks provide type safety while maintaining clean APIs.

### Pattern Categories

- **Creational**: Factory (database sessions), Singleton (event service, tracking state)
- **Structural**: Adapter (schema compatibility), Facade (tracking API), Module (encapsulation)
- **Behavioral**: Observer (viewport detection), Strategy (scoring), Service Layer (business logic)
- **Architectural**: Layered Architecture, RESTful API, Connection Pooling

### Trade-offs Made

1. **Simplicity vs Flexibility**: Chose Context API over Redux for simpler state needs
2. **Explicit vs Implicit**: Use SQLAlchemy's implicit repository pattern instead of explicit repositories
3. **Standard vs Custom**: Use Flask blueprints (standard) instead of custom routing
4. **Performance vs Simplicity**: Implement event batching for performance, even though it adds complexity

This balanced approach ensures the codebase remains maintainable, performant, and aligned with modern best practices while avoiding over-engineering.
