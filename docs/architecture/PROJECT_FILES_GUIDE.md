## SmartTrip Project Files Guidebook

This guide gives you a **high‑level, beginner‑friendly tour of the main files and folders** in the SmartTrip project, with a focus on what you actually need to understand to work on the app end‑to‑end.

It does **not** explain the recommendation algorithm, events, Flask basics, or TypeScript basics in depth – those are already covered in the other Week 1–4 guides. Instead, this document is your **map of the project**: what lives where, why each file exists, and when you will (or won’t) touch it.

---

## 1. Top‑Level (Root) Files & Folders

These are the first things you see at the project root.

- **`backend/`**  
  Python backend: Flask API, database models, scripts, recommendation engine, event tracking, background jobs.

- **`src/`**  
  TypeScript/React frontend (Next.js App Router): pages, components, hooks, and client‑side tracking.

- **`tests/`**  
  All automated tests: backend, integration, and end‑to‑end UI tests (Playwright). Already covered in the testing guide, but important to remember the location.

- **`public/`**  
  Static assets for the frontend: images, SVG icons, logos, etc. Anything here is served directly by Next.js.

- **`docs/`**  
  All learning documentation and generated PDFs (the guides you’ve been reading), plus the PDF generator script.

- **`package.json` / `package-lock.json`**  
  JavaScript/TypeScript dependencies and scripts for the frontend and tooling (like `md-to-pdf`).  
  - You edit `package.json` when adding frontend libraries.  
  - `package-lock.json` is auto‑managed by npm.

- **`tsconfig.json`**  
  TypeScript configuration for the frontend. Controls strictness, path aliases, and compiler options. You rarely touch this as a beginner, except to add path aliases if needed.

- **`tailwind.config.ts`**  
  Tailwind CSS configuration: which files are scanned for class names, theme extensions, custom colors, etc.

- **`eslint.config.mjs`**  
  ESLint configuration for linting frontend code. Helps keep code style consistent.

- **`next.config.js`**  
  Next.js configuration: rewrites, image domains, experimental flags. Important if you need custom routing or backend proxying.

- **`postcss.config.mjs`**  
  PostCSS configuration used by Tailwind; you almost never touch this directly.

- **`pytest.ini`**  
  Pytest configuration file for backend tests: markers, test path settings, etc.

- **`render.yaml`**  
  Render deployment configuration for the backend. Describes how the Python service is built and run in production.

- **`run_tests.py`**  
  Convenience script to run the project’s Python test suite or specific subsets. Useful when you want a one‑command test run.

- **`README.md`**  
  Top‑level project README: high‑level overview, setup instructions, and links to docs. Good starting point when you need a reminder of the big picture.

- **`smarttrip_backup.dump`**  
  Database backup file (PostgreSQL dump). Not part of the application logic; used to restore data into a database instance.

---

## 2. Frontend Structure (`src/`)

The frontend is a Next.js App Router app written in TypeScript/React.

### 2.1 `src/app/` – Pages & Layout

These are the **actual pages** of the app. Next.js uses the folder structure under `app/` to define routes.

- **`src/app/layout.tsx`**  
  Root layout for the whole app. Defines global HTML structure, `<head>` tags (metadata), and wraps all pages (e.g., global `<Header />`, `<Footer />`).  
  - You’d touch this if you add global providers (context, theming) or layout changes that affect every page.

- **`src/app/page.tsx`**  
  The homepage (`/`). Entry point for users: high‑level marketing or featured trips, and links to search.

- **`src/app/error.tsx`**  
  Global error boundary for top‑level routes. Next.js uses this when an uncaught error happens.

- **`src/app/globals.css`**  
  Global CSS imported into the app. Tailwind base styles, global resets, any non‑Tailwind custom styles.

- **`src/app/search/page.tsx`**  
  Search form page (`/search`).  
  - Uses form state (`useState`) and controlled inputs to capture user preferences.  
  - On submit, navigates to the results page with query parameters.

- **`src/app/search/error.tsx`**  
  Error UI for the search route if something fails there specifically.

- **`src/app/search/results/page.tsx`**  
  Search results page (`/search/results`).  
  - Reads URL search params, calls the backend recommendation API, and displays the list of trips with scores and statuses.  
  - Uses the recommendation algorithm output heavily (match_score, is_relaxed, etc.).

- **`src/app/search/results/loading.tsx`**  
  Loading UI for results route. Next.js shows this while data is being fetched.

- **`src/app/trip/[id]/page.tsx`**  
  Dynamic route for a single trip detail page (`/trip/123`).  
  - Fetches trip data from backend by ID.  
  - Uses tracking hooks (e.g., dwell time, trip view events).

### 2.2 `src/lib/` – Frontend Utilities & Hooks

- **`src/lib/api.ts`**  
  Typed API client for the frontend. Knows how to call backend endpoints (e.g., recommendations, trips) and defines TypeScript interfaces for response shapes.  
  - Central place to add new frontend→backend calls.

- **`src/lib/dataStore.tsx`**  
  Frontend state management helper (likely a React context or custom hook) for shared UI state such as filters, selected trips, or user preferences.  
  - You would use this if you want to access shared data across multiple pages (e.g., search preferences remembered between pages).

- **`src/lib/tracking.ts`**  
  Core frontend tracking module (Phase 1).  
  - Manages anonymous ID and session ID via `localStorage`.  
  - Queues tracking events, batches them, and sends to `/api/events/batch`.  
  - Provides functions like `trackPageView`, `trackResultsView`, `trackTripClick`, `trackSaveTrip`, etc.  
  - Essential glue between React hooks and backend event service.

- **`src/lib/useTracking.ts`**  
  React hooks **wrapper** around `tracking.ts`:  
  - `usePageView`, `useTripDwellTime`, `useImpressionTracking`, `useResultsTracking`, `useFilterTracking`, etc.  
  - Export of key tracking functions like `trackTripClick`, `trackSaveTrip`, `trackBookingStart`.  
  - When you want to track something from a component, you import from here.

---

## 3. Backend Structure (`backend/`)

The backend is a Flask app with SQLAlchemy models and a modular architecture.

### 3.1 Core Files

- **`backend/app.py`**  
  Main Flask application.  
  - Registers routes (e.g., `/api/recommendations`, `/api/v2/...`, `/api/trips`).  
  - Contains the **recommendation algorithm** (V1 deprecated and/or V2 driver).  
  - Integrates event tracking (`EVENTS_ENABLED`) and logging.  
  - You’ve already studied this deeply in the recommendation guides.

- **`backend/database.py`**  
  Database setup and session management.  
  - Provides `engine`, `SessionLocal`, and often a scoped session `db_session`.  
  - You rarely change this once it’s correct, but you might read it to understand how sessions are created.

- **`backend/models.py`**  
  Main SQLAlchemy ORM models (V1 schema): `Trip`, `Country`, `Guide`, `TripType`, `Tag`, `TripTag`, etc.  
  - Already covered in the Database Models guide.  
  - Essential to understand the shape of data the app stores.

- **`backend/models_v2.py`**  
  Newer V2 schema models: `Company`, `TripTemplate`, `TripOccurrence`, etc.  
  - Used by `api_v2.py` and background jobs.  
  - Important for understanding how the system is evolving (e.g., company attribution, occurrences vs templates).

- **`backend/api_v2.py`**  
  V2 Flask API blueprint.  
  - Newer endpoints that operate on V2 schema (templates, occurrences, companies).  
  - Likely successor to some older V1 endpoints in `app.py`.  
  - If you build new backend features, you’ll often do it here instead of bolting onto the legacy V1 endpoints.

### 3.2 Events Module (`backend/events/`)

- **`backend/events/api.py`**  
  Flask blueprint for event tracking endpoints:  
  - `/api/events` (single event)  
  - `/api/events/batch` (batch tracking)  
  - Uses `EventService` under the hood.

- **`backend/events/service.py`**  
  Event tracking service (Phase 1).  
  - Responsible for user/session resolution, event validation, classification, and trip interaction updates.  
  - Defines `EVENT_CATEGORIES`, `VALID_EVENT_TYPES`, and the `EventService` class.  
  - Already covered in the Event Tracking guide.

- **`backend/events/models.py`**  
  SQLAlchemy models for event‑related tables: `Event`, `EventType`, `EventCategory`, `TripInteraction`, `Session`, `User`, etc.  
  - Understanding these helps you analyze analytics data in the DB.

### 3.3 Recommender Module (`backend/recommender/`)

- **`backend/recommender/logging.py`**  
  Logging helpers for recommendation requests (Phase 0).  
  - Generates `request_id`, logs inputs and outputs for analysis.

- **`backend/recommender/metrics.py`**  
  Aggregates performance metrics (e.g., response times, score distributions) from recommendation runs.

- **`backend/recommender/evaluation.py`**  
  Scenario evaluator: runs predefined test scenarios to evaluate the quality of recommendations against expectations.  
  - Connects to test cases like `tests/backend/test_05_recommender.py` and `tests/integration/test_recommendations.py`.

- **`backend/recommender/README.md`**  
  Additional documentation focused on the recommender architecture, scenarios, and evaluation approach.

These files are essential if you want to **improve or debug the recommendation engine quality** beyond basic scoring changes.

### 3.4 Scheduler & Background Jobs

- **`backend/scheduler.py`**  
  Background scheduler (Phase 1) that runs periodic jobs (e.g., daily aggregates, cleanup).  
  - Integrates with scripts in `backend/scripts/`.

- **`backend/scripts/`**  
  One‑off and recurring maintenance scripts. Key examples:
  - `aggregate_daily_metrics.py` – Aggregates daily metrics for dashboards.  
  - `aggregate_trip_interactions.py` – Recalculates `TripInteraction` counters.  
  - `analyze_scoring.py` / `analyze_scoring_v2.py` – Analyze how scoring behaves across trips.  
  - `seed.py`, `seed_from_csv.py` – Seed the database with initial or CSV‑based data.  
  - `check_schema.py`, `verify_schema.py`, `verify_seed.py` – Sanity checks for DB schema and seed data.  
  - `cleanup_sessions.py` – Clean up old or invalid sessions.  
  - `export_data.py`, `import_data.py` – Data import/export operations.

  You typically **run** these scripts via `python -m backend.scripts.<name>` or via a scheduled job in production. They are not imported by the app at runtime (except where explicitly wired by the scheduler).

### 3.5 Scenarios & Personas

- **`backend/scenarios/README.md`**  
  Explains predefined user personas and test scenarios used to evaluate recommendations.

- **`backend/scenarios/generated_personas.json`**  
  Machine‑generated persona data used in evaluation and analytics scripts. Helps simulate diverse user profiles.

---

## 4. Tests (`tests/`)

While there is a full Testing & Deployment guide, here is how the test tree relates to the rest of the project.

- **`tests/backend/`**  
  - `test_01_db_schema.py` – Checks DB schema and constraints.  
  - `test_02_api.py` – API endpoints behavior (trips, V2, recommendations).  
  - `test_03_analytics.py` – Analytics, events, metrics.  
  - `test_04_cron.py` – Scheduler and background jobs.  
  - `test_05_recommender.py` – Recommendation algorithm behavior (scoring, filters, relaxed results, logging).

- **`tests/integration/`**  
  - `test_algorithm.py`, `test_recommendations.py` – Integration tests that run the full recommendation stack.  
  - `test_api_endpoints.py` – Multi‑endpoint flows.  
  - `test_event_tracking.py` – Frontend→backend→DB event flows.  
  - `test_search_scenarios.py` – Realistic search flows combining filters, results, and scoring.

- **`tests/e2e/`**  
  - `test_06_ui_desktop.py`, `test_07_ui_mobile.py` – UI layout and interaction checks on different viewports.  
  - `test_08_search_flow.py`, `test_09_trip_details.py`, `test_10_visual_feedback.py` – End‑to‑end user flows (search → results → trip details → feedback), using Playwright.

- **`tests/conftest.py`**  
  Global test configuration and fixtures:  
  - Creates `client` (Flask test client), `db_session`, sample entities (`sample_trip`, `sample_country`, etc.).  
  - Defines `pytest` markers like `@pytest.mark.api`, `@pytest.mark.recommender`, `@pytest.mark.e2e`.

- **`tests/requirements-test.txt`**  
  Python dependencies needed to run tests only (pytest, coverage, Playwright, etc.).

---

## 5. Deployment & Infrastructure Files

### 5.1 Render (Backend)

- **`backend/requirements.txt`**  
  Python dependency list for the backend (Flask, SQLAlchemy, etc.). Render uses this to build the image.

- **`backend/Procfile`**  
  Tells Render (or Heroku‑style platforms) how to start the web process, e.g.:  
  `web: gunicorn app:app`  
  You’d adjust this if the entrypoint changes (e.g., to a different app module).

- **`backend/runtime.txt`**  
  Indicates the Python runtime version (e.g., `python-3.11.x`).

- **`render.yaml` (root)**  
  High‑level Render configuration: defines services (web, worker), environment variables, build/launch commands, and health check paths.

### 5.2 Vercel (Frontend)

No explicit Vercel config file is required by default; Vercel auto‑detects Next.js. The main things you configure are:

- **Environment variable `NEXT_PUBLIC_API_URL`** – Points to your deployed backend.
- **`next.config.js`** – If you need rewrites, custom headers, or experimental flags.

### 5.3 Tooling & Quality

- **`eslint.config.mjs`** – Linting rules for TypeScript/React.  
- **`tailwind.config.ts`** – Tailwind theme and content paths.  
- **`pytest.ini`** – Pytest config (markers, options).  
- **`docs/generate_learning_pdfs.py`** – Script that converts all learning Markdown guides into PDFs using `md-to-pdf`.

---

## 6. Which Files to Focus on First

Because this is your **first app**, here’s a suggested priority for deeply understanding the codebase:

1. **Frontend Core**
   - `src/app/layout.tsx` – How the app shell is structured.
   - `src/app/page.tsx` – Homepage and how it links into search.
   - `src/app/search/page.tsx` – Search form and URL parameters.
   - `src/app/search/results/page.tsx` – How results are fetched and rendered.
   - `src/app/trip/[id]/page.tsx` – Trip detail flow.

2. **Frontend Utilities**
   - `src/lib/api.ts` – How the frontend talks to the backend.
   - `src/lib/useTracking.ts` + `src/lib/tracking.ts` – How user actions are tracked.
   - `src/lib/dataStore.tsx` – Shared state patterns (if used in flows you care about).

3. **Backend Essentials**
   - `backend/app.py` – Main Flask app, routes, recommendation logic.
   - `backend/models.py` – How Trips/Countries/Guides/Tags are represented.
   - `backend/events/service.py` + `backend/events/api.py` – Event tracking pipeline.
   - `backend/api_v2.py` + `backend/models_v2.py` – Newer API surface and data model.

4. **Quality & Testing**
   - `tests/backend/test_02_api.py` – What the API is expected to do.
   - `tests/backend/test_05_recommender.py` – How the algorithm is expected to behave.
   - `tests/integration/test_recommendations.py` – End‑to‑end recommendation flows.

5. **Deployment & Operations**
   - `render.yaml`, `backend/Procfile`, `backend/runtime.txt`, `backend/requirements.txt` – How the backend is deployed.
   - `package.json`, `next.config.js`, `tailwind.config.ts`, `tsconfig.json` – How the frontend is built and configured.

You **don’t need to fully understand every script in `backend/scripts/` or every test file** on day one. Start with the core flows (search → recommend → view trip) and the files above, then expand to scripts and advanced tooling when you’re comfortable.

As you work, you can always come back to this guidebook as a reference when you stumble upon a file you don’t recognize.


