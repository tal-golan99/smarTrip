# SmartTrip Master Test Plan

**Document Version:** 1.0  
**Created:** December 16, 2025  
**Author:** QA Automation Architect  
**Application Version:** Phase 1 Complete (Database Schema V2, Analytics, Background Jobs)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Test Environment](#test-environment)
3. [Database Schema V2 & Migration Tests](#1-database-schema-v2--migration-tests)
4. [Backend API & Logic Tests](#2-backend-api--logic-tests)
5. [Phase 1 Analytics & User Tracking Tests](#3-phase-1-analytics--user-tracking-tests)
6. [Automated Cron Jobs (APScheduler) Tests](#4-automated-cron-jobs-apscheduler-tests)
7. [Phase 0 Recommender System Tests](#5-phase-0-recommender-system-tests)
8. [UI/UX & End-to-End Tests](#6-uiux--end-to-end-tests)
9. [Test Summary Matrix](#test-summary-matrix)

---

## Executive Summary

This Master Test Plan provides comprehensive coverage for the SmartTrip trip recommendation application following the major Phase 1 refactoring. The plan contains **312 distinct test cases** organized across 6 major categories covering database integrity, API functionality, analytics tracking, background jobs, recommendation algorithms, and user interface validation.

### Test Distribution

| Category | Test Cases | Priority |
|----------|------------|----------|
| Database Schema V2 & Migration | 52 | Critical |
| Backend API & Logic | 62 | Critical |
| Phase 1 Analytics & User Tracking | 50 | High |
| Automated Cron Jobs (APScheduler) | 32 | High |
| Phase 0 Recommender System | 34 | High |
| UI/UX & End-to-End | 82 | Medium |
| **Total** | **312** | - |

---

## Test Environment

### Prerequisites
- PostgreSQL 15+ with test database
- Python 3.11+ with all requirements installed
- Node.js 18+ for frontend tests
- Chrome/Firefox for E2E tests
- Postman/curl for API tests

### Test Data Requirements
- Minimum 500 trip_templates
- Minimum 700 trip_occurrences
- 10 companies
- 50+ countries
- 10 trip_types
- 20+ tags

---

## 1. Database Schema V2 & Migration Tests

### 1.1 Trip Templates Table Structure (TC-DB-001 to TC-DB-010)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-DB-001 | Verify trip_templates table exists with correct columns | Database migrated to V2 | Table contains: id, company_id, title, title_he, description, description_he, default_image_url, base_price, single_supplement_price, default_max_capacity, difficulty_level, trip_type_id, is_active, properties, created_at, updated_at |
| TC-DB-002 | Verify trip_templates.id is auto-incrementing primary key | Database migrated | INSERT without id auto-generates sequential integer |
| TC-DB-003 | Verify trip_templates.company_id is NOT NULL foreign key | Database migrated | INSERT with NULL company_id fails with constraint violation |
| TC-DB-004 | Verify trip_templates.title is VARCHAR(255) NOT NULL | Database migrated | INSERT with NULL title fails; INSERT with 256+ chars fails |
| TC-DB-005 | Verify trip_templates.title_he allows NULL | Database migrated | INSERT with NULL title_he succeeds |
| TC-DB-006 | Verify trip_templates.base_price is DECIMAL(10,2) NOT NULL | Database migrated | INSERT with NULL base_price fails; Decimal precision maintained |
| TC-DB-007 | Verify trip_templates.difficulty_level accepts 1-5 only | Database migrated | INSERT with 0 or 6 fails CHECK constraint |
| TC-DB-008 | Verify trip_templates.is_active defaults to TRUE | Database migrated | INSERT without is_active sets value to TRUE |
| TC-DB-009 | Verify trip_templates.properties is JSONB nullable | Database migrated | INSERT with valid JSON succeeds; NULL allowed |
| TC-DB-010 | Verify trip_templates FK to trip_types ON DELETE RESTRICT | trip_type exists with templates | DELETE trip_type fails if templates reference it |

### 1.2 Trip Occurrences Table Structure (TC-DB-011 to TC-DB-022)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-DB-011 | Verify trip_occurrences table exists with correct columns | Database migrated to V2 | Table contains: id, trip_template_id, guide_id, start_date, end_date, price_override, image_url_override, spots_left, status, notes, notes_he, properties, created_at, updated_at |
| TC-DB-012 | Verify trip_occurrences.trip_template_id is NOT NULL FK | Database migrated | INSERT with NULL trip_template_id fails |
| TC-DB-013 | Verify trip_occurrences.guide_id is nullable FK | Database migrated | INSERT with NULL guide_id succeeds |
| TC-DB-014 | Verify trip_occurrences.start_date is DATE NOT NULL | Database migrated | INSERT with NULL start_date fails |
| TC-DB-015 | Verify trip_occurrences.end_date is DATE NOT NULL | Database migrated | INSERT with NULL end_date fails |
| TC-DB-016 | Verify trip_occurrences.price_override is nullable DECIMAL | Database migrated | INSERT with NULL price_override succeeds; value overrides template base_price |
| TC-DB-017 | Verify trip_occurrences.image_url_override is nullable | Database migrated | INSERT with NULL image_url_override succeeds |
| TC-DB-018 | Verify trip_occurrences.spots_left is INTEGER NOT NULL | Database migrated | INSERT with NULL spots_left fails |
| TC-DB-019 | Verify trip_occurrences.spots_left CHECK >= 0 | Database migrated | UPDATE to negative value fails CHECK constraint |
| TC-DB-020 | Verify trip_occurrences.status ENUM values | Database migrated | Only 'Open', 'Guaranteed', 'Last Places', 'Full' accepted |
| TC-DB-021 | Verify trip_occurrences FK CASCADE on template delete | Template with occurrences exists | DELETE template cascades to delete occurrences |
| TC-DB-022 | Verify trip_occurrences.properties JSONB | Database migrated | Can store/retrieve arbitrary JSON objects |

### 1.3 Companies Table (TC-DB-023 to TC-DB-030)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-DB-023 | Verify companies table exists with correct columns | Database migrated | Table contains: id, name, name_he, description, logo_url, website_url, phone, email, is_active, created_at, updated_at |
| TC-DB-024 | Verify companies.name is VARCHAR(255) NOT NULL UNIQUE | Database migrated | Duplicate names fail UNIQUE constraint |
| TC-DB-025 | Verify companies.email format validation | Database migrated | Invalid email format rejected (if constraint exists) |
| TC-DB-026 | Verify companies.is_active defaults to TRUE | Database migrated | INSERT without is_active sets TRUE |
| TC-DB-027 | Verify seed data populates 10 companies | Fresh seed | Exactly 10 companies exist with realistic data |
| TC-DB-028 | Verify company-template 1:N relationship | Companies and templates exist | Each template belongs to exactly one company |
| TC-DB-029 | Verify company deletion restricted if templates exist | Company with templates | DELETE company fails with FK violation |
| TC-DB-030 | Verify company queries with template counts | Companies with varied templates | Aggregation query returns correct counts per company |

### 1.4 Legacy Data Migration (TC-DB-031 to TC-DB-038)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-DB-031 | Verify all old trips have corresponding templates | Migration completed | COUNT(old_trips) = COUNT(trip_templates) after migration |
| TC-DB-032 | Verify all old trips have corresponding occurrences | Migration completed | Each old trip has at least 1 occurrence |
| TC-DB-033 | Verify trip titles preserved in templates | Migration completed | template.title matches original trip.title |
| TC-DB-034 | Verify trip prices preserved | Migration completed | template.base_price matches original trip.price |
| TC-DB-035 | Verify trip dates moved to occurrences | Migration completed | occurrence.start_date/end_date match original |
| TC-DB-036 | Verify trip-tag relationships preserved | Migration completed | trip_template_tags contains all original associations |
| TC-DB-037 | Verify trip-country relationships preserved | Migration completed | trip_template_countries contains correct mappings |
| TC-DB-038 | Verify rollback capability | Before migration | Rollback script restores original schema |

### 1.5 JSONB Properties Columns (TC-DB-039 to TC-DB-046)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-DB-039 | Insert template with packing_list property | Template exists | JSON {"packing_list": ["item1", "item2"]} stored correctly |
| TC-DB-040 | Insert template with requirements property | Template exists | JSON {"requirements": {"visa": true, "vaccinations": ["Yellow Fever"]}} stored |
| TC-DB-041 | Query templates by JSONB property | Templates with properties | SELECT WHERE properties->>'key' = 'value' works |
| TC-DB-042 | Update nested JSONB property | Template with properties | jsonb_set updates specific nested key |
| TC-DB-043 | Insert occurrence with cabin_type property | Occurrence exists | JSON {"cabin_type": "Suite"} stored for cruise occurrence |
| TC-DB-044 | Query occurrences by JSONB contains | Occurrences with properties | SELECT WHERE properties @> '{"key": "value"}' works |
| TC-DB-045 | Verify JSONB index performance | 1000+ templates with properties | GIN index query < 100ms |
| TC-DB-046 | Verify NULL properties handling | Templates exist | NULL properties does not break queries |

### 1.6 Multi-Country Relationships (TC-DB-047 to TC-DB-052)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-DB-047 | Verify trip_template_countries junction table | Database migrated | Table has trip_template_id, country_id composite PK |
| TC-DB-048 | Insert template with multiple countries | Countries exist | Junction table accepts multiple country associations |
| TC-DB-049 | Query templates by country | Templates with countries | JOIN returns all templates for given country |
| TC-DB-050 | Verify cascade delete on template | Template with countries | DELETE template removes junction entries |
| TC-DB-051 | Verify restrict delete on country | Country with templates | DELETE country fails if templates reference it |
| TC-DB-052 | Query multi-country trip with all countries | Multi-country template | Query returns array of all associated countries |

---

## 2. Backend API & Logic Tests

### 2.1 Trips API Endpoints (TC-API-001 to TC-API-015)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-API-001 | GET /api/trips returns 200 with trip list | Trips exist in DB | Response contains array of trip objects with pagination |
| TC-API-002 | GET /api/trips with limit parameter | 50+ trips exist | Response limited to specified count |
| TC-API-003 | GET /api/trips with offset parameter | 50+ trips exist | Response starts from specified offset |
| TC-API-004 | GET /api/trips/:id returns single trip | Trip ID exists | Response contains full trip details |
| TC-API-005 | GET /api/trips/:id returns 404 for invalid ID | Invalid ID | Response: 404 Not Found with error message |
| TC-API-006 | GET /api/trips filters by country | Trips in multiple countries | Only trips matching country returned |
| TC-API-007 | GET /api/trips filters by continent | Trips across continents | Only trips in specified continent returned |
| TC-API-008 | GET /api/trips filters by trip_type | Various trip types exist | Only matching trip types returned |
| TC-API-009 | GET /api/trips filters by tags (multiple) | Trips with tags | Trips matching ANY specified tag returned |
| TC-API-010 | GET /api/trips filters by price range | Varied prices | Only trips within min_price-max_price returned |
| TC-API-011 | GET /api/trips filters by date range | Various dates | Only trips within start_date-end_date returned |
| TC-API-012 | GET /api/trips filters by difficulty | Difficulty 1-5 | Only trips matching difficulty level returned |
| TC-API-013 | GET /api/trips filters by status | Various statuses | Only 'Open', 'Guaranteed', 'Last Places' returned (excludes Full) |
| TC-API-014 | GET /api/trips combined filters | Varied data | Filters combine with AND logic correctly |
| TC-API-015 | GET /api/trips empty result | Impossible filters | Returns empty array, not error |

### 2.2 V2 API - Templates & Occurrences (TC-API-016 to TC-API-030)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-API-016 | GET /api/v2/templates returns all templates | Templates exist | Array of template objects with company info |
| TC-API-017 | GET /api/v2/templates/:id returns single template | Template exists | Full template with tags, countries, occurrences |
| TC-API-018 | GET /api/v2/templates/:id/occurrences | Template with occurrences | Array of all occurrences for template |
| TC-API-019 | GET /api/v2/occurrences returns all occurrences | Occurrences exist | Array with effective_price calculated |
| TC-API-020 | GET /api/v2/occurrences/:id returns single occurrence | Occurrence exists | Full occurrence with template details |
| TC-API-021 | GET /api/v2/occurrences filters by template_id | Multiple templates | Only occurrences for specified template |
| TC-API-022 | GET /api/v2/occurrences filters by date_from | Various dates | Only future occurrences from date returned |
| TC-API-023 | GET /api/v2/occurrences filters by date_to | Various dates | Only occurrences before date returned |
| TC-API-024 | GET /api/v2/trips backward compatibility | V2 data exists | Returns occurrences formatted as legacy trips |
| TC-API-025 | GET /api/v2/companies returns all companies | Companies exist | Array of company objects |
| TC-API-026 | GET /api/v2/companies/:id returns company | Company exists | Company with template count |
| TC-API-027 | GET /api/v2/companies/:id/templates | Company with templates | All templates for company |
| TC-API-028 | Verify effective_price returns override when set | Occurrence with price_override | effective_price = price_override |
| TC-API-029 | Verify effective_price returns base when no override | Occurrence without override | effective_price = template.base_price |
| TC-API-030 | Verify effective_image_url logic | Occurrence with/without override | Returns override if set, else template default |

### 2.3 Recommendations API (TC-API-031 to TC-API-042)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-API-031 | POST /api/recommendations with valid input | Trips exist | Returns scored and ranked trip list |
| TC-API-032 | POST /api/recommendations with empty preferences | Trips exist | Returns default recommendations |
| TC-API-033 | POST /api/recommendations with budget filter | Varied prices | Only trips within budget returned |
| TC-API-034 | POST /api/recommendations with duration preference | Varied durations | Trips sorted by duration match score |
| TC-API-035 | POST /api/recommendations with theme tags | Tagged trips | Theme-matching trips scored higher |
| TC-API-036 | POST /api/recommendations with country preference | Multi-country trips | Country-matching trips prioritized |
| TC-API-037 | POST /api/recommendations with continent filter | Global trips | Only continent-matching trips returned |
| TC-API-038 | POST /api/recommendations response time | 500+ trips | Response < 500ms |
| TC-API-039 | POST /api/recommendations includes match_score | Valid input | Each trip has match_score 0-100 |
| TC-API-040 | POST /api/recommendations logs request | Valid input | Entry created in recommendation_requests |
| TC-API-041 | GET /api/v2/recommendations uses new schema | V2 data | Recommendations from trip_occurrences |
| TC-API-042 | POST /api/recommendations relaxed mode | No exact matches | Relaxes filters and returns partial matches |

### 2.4 Error Handling (TC-API-043 to TC-API-052)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-API-043 | Invalid JSON body returns 400 | Any POST endpoint | 400 Bad Request with parse error |
| TC-API-044 | Missing required field returns 400 | POST /api/events | 400 with field validation error |
| TC-API-045 | Invalid date format returns 400 | Date filter endpoint | 400 with date format error |
| TC-API-046 | Invalid enum value returns 400 | Status filter | 400 with enum validation error |
| TC-API-047 | Non-existent resource returns 404 | GET /api/trips/99999 | 404 Not Found |
| TC-API-048 | Database connection error returns 503 | DB down | 503 Service Unavailable |
| TC-API-049 | Internal error returns 500 | Force exception | 500 Internal Server Error (no stack trace) |
| TC-API-050 | CORS headers present | Cross-origin request | Access-Control-Allow-Origin header set |
| TC-API-051 | Rate limiting (if implemented) | Rapid requests | 429 Too Many Requests after threshold |
| TC-API-052 | Malformed UUID returns 400 | Session ID endpoint | 400 with UUID format error |

### 2.5 Sorting and Ordering (TC-API-053 to TC-API-060)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-API-053 | GET /api/trips sort by price ASC | Varied prices | Trips ordered low to high price |
| TC-API-054 | GET /api/trips sort by price DESC | Varied prices | Trips ordered high to low price |
| TC-API-055 | GET /api/trips sort by start_date ASC | Varied dates | Earliest departure first |
| TC-API-056 | GET /api/trips sort by start_date DESC | Varied dates | Latest departure first |
| TC-API-057 | GET /api/trips sort by duration | Varied durations | Shortest trips first |
| TC-API-058 | GET /api/trips sort by match_score | After recommendation | Highest scores first |
| TC-API-059 | GET /api/trips default sort order | No sort param | Sorted by relevance/created_at |
| TC-API-060 | GET /api/trips invalid sort field | Invalid field | 400 error or ignored |

### 2.6 Concurrency & Data Integrity (TC-API-061 to TC-API-062)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-API-061 | Concurrent spots_left decrements | spots_left = 5, 10 concurrent requests | Final spots_left >= 0 (no negative) |
| TC-API-062 | Concurrent event inserts | High-volume event POSTs | All events recorded without duplicates |

---

## 3. Phase 1 Analytics & User Tracking Tests

### 3.1 Session Management (TC-ANA-001 to TC-ANA-015)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-ANA-001 | Anonymous session created on first visit | New browser session | Session record created with anonymous_id |
| TC-ANA-002 | Session ID persists across page navigations | Active session | Same session_id used for all events |
| TC-ANA-003 | Session includes user_agent | Browser request | user_agent captured correctly |
| TC-ANA-004 | Session includes referrer | External referral | referrer URL captured |
| TC-ANA-005 | Session started_at timestamp accurate | New session | started_at within 1 second of request time |
| TC-ANA-006 | Session ended_at NULL while active | Active session | ended_at remains NULL |
| TC-ANA-007 | Session device_type detection | Mobile browser | device_type = 'mobile' |
| TC-ANA-008 | Session device_type detection | Desktop browser | device_type = 'desktop' |
| TC-ANA-009 | Session device_type detection | Tablet browser | device_type = 'tablet' |
| TC-ANA-010 | Session IP anonymization | Any request | IP stored in anonymized format |
| TC-ANA-011 | Multiple tabs share session | Same browser, 2 tabs | Both tabs use same session_id |
| TC-ANA-012 | New session after browser close | Close and reopen browser | New session_id generated |
| TC-ANA-013 | Session timeout after 30 min inactivity | 30+ min idle | Session marked as ended |
| TC-ANA-014 | Session duration calculated correctly | Session with events | duration_seconds = ended_at - started_at |
| TC-ANA-015 | Session count per day accurate | Multiple sessions | Daily session count matches |

### 3.2 Event Tracking (TC-ANA-016 to TC-ANA-035)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-ANA-016 | page_view event logged on page load | Any page visit | Event with type='page_view', path recorded |
| TC-ANA-017 | trip_click event logged | Click trip card | Event with trip_id, position recorded |
| TC-ANA-018 | search event logged | Submit search | Event with search parameters in metadata |
| TC-ANA-019 | filter_change event logged | Change filter | Event with old and new filter values |
| TC-ANA-020 | sort_change event logged | Change sort order | Event with sort field and direction |
| TC-ANA-021 | impression event logged | Trip visible in viewport | Batch impression events with trip_ids |
| TC-ANA-022 | scroll_depth event logged | Scroll results page | Event at 25%, 50%, 75%, 100% thresholds |
| TC-ANA-023 | trip_dwell_time event logged | Stay on trip details | Event with seconds spent on page |
| TC-ANA-024 | contact_whatsapp event logged | Click WhatsApp button | Event with trip_id, guide_id |
| TC-ANA-025 | booking_start event logged | Click Book Now | Event with trip_id, occurrence_id |
| TC-ANA-026 | save_trip event logged | Save trip to favorites | Event with trip_id |
| TC-ANA-027 | Event timestamp accuracy | Any event | timestamp within 1 second of actual time |
| TC-ANA-028 | Event session_id linkage | Any event | session_id matches active session |
| TC-ANA-029 | Event metadata as JSONB | Complex event | Arbitrary metadata stored correctly |
| TC-ANA-030 | Event category classification | Various events | Correct category: navigation/search/engagement/conversion |
| TC-ANA-031 | Event deduplication | Rapid same events | Duplicates within 1 second ignored |
| TC-ANA-032 | Event batch POST | Multiple events | POST /api/events/batch accepts array |
| TC-ANA-033 | Event validation - required fields | Missing session_id | 400 error returned |
| TC-ANA-034 | Event validation - valid event_type | Invalid type | 400 error returned |
| TC-ANA-035 | Event query by session | Session with events | All events for session retrievable |

### 3.3 LocalStorage Sync (TC-ANA-036 to TC-ANA-045)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-ANA-036 | anonymous_id stored in localStorage | New visit | localStorage.smartrip_anonymous_id set |
| TC-ANA-037 | session_id stored in localStorage | New session | localStorage.smartrip_session_id set |
| TC-ANA-038 | Session restored from localStorage | Page refresh | Same session_id used |
| TC-ANA-039 | Anonymous ID persists across sessions | Multiple visits | Same anonymous_id maintained |
| TC-ANA-040 | Pending events queued in localStorage | Offline event | Event stored in localStorage queue |
| TC-ANA-041 | Pending events flushed on reconnect | Back online | Queued events POSTed to backend |
| TC-ANA-042 | localStorage clear creates new identity | Clear localStorage | New anonymous_id and session_id |
| TC-ANA-043 | Search history stored locally | Multiple searches | Recent searches in localStorage |
| TC-ANA-044 | Viewed trips stored locally | View trip details | Trip IDs in recently_viewed |
| TC-ANA-045 | LocalStorage quota handling | Near quota limit | Graceful degradation, no errors |

### 3.4 Identity Management (TC-ANA-046 to TC-ANA-050)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-ANA-046 | Anonymous profile created | First visit | users table entry with is_anonymous=true |
| TC-ANA-047 | Profile tracks total sessions | Multiple sessions | total_sessions incremented correctly |
| TC-ANA-048 | Profile tracks last_seen_at | Any activity | last_seen_at updated |
| TC-ANA-049 | User registration merges anonymous data | Register after browsing | Events linked to new user_id |
| TC-ANA-050 | Login associates existing anonymous ID | Login existing user | Previous anonymous events retained |

---

## 4. Automated Cron Jobs (APScheduler) Tests

### 4.1 Scheduler Initialization (TC-CRON-001 to TC-CRON-008)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-CRON-001 | Scheduler starts with Flask app | App startup | BackgroundScheduler running=True |
| TC-CRON-002 | All 3 jobs registered | Scheduler started | get_scheduler_status returns 3 jobs |
| TC-CRON-003 | Scheduler status endpoint accessible | Scheduler running | GET /api/scheduler/status returns 200 |
| TC-CRON-004 | Jobs have correct next_run_time | Scheduler started | Each job shows valid next execution time |
| TC-CRON-005 | SKIP_SCHEDULER=true prevents start | Env var set | Scheduler not initialized |
| TC-CRON-006 | Double initialization prevented | Call start_scheduler twice | Only one scheduler instance |
| TC-CRON-007 | Scheduler survives job errors | Job throws exception | Scheduler continues running |
| TC-CRON-008 | Scheduler graceful shutdown | App shutdown | shutdown(wait=True) completes cleanly |

### 4.2 Aggregate Trip Interactions Job (TC-CRON-009 to TC-CRON-016)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-CRON-009 | Job executes at minute 0 | Wait for :00 | Job runs within 60 seconds of hour |
| TC-CRON-010 | Job calculates CTR correctly | 100 impressions, 10 clicks | click_through_rate = 0.10 |
| TC-CRON-011 | Job updates unique_viewers | 50 unique sessions viewed trip | unique_viewers = 50 |
| TC-CRON-012 | Job updates unique_clickers | 20 unique sessions clicked | unique_clickers = 20 |
| TC-CRON-013 | Job updates save_count | 5 save_trip events | save_count = 5 |
| TC-CRON-014 | Job updates whatsapp_contact_count | 3 contact events | whatsapp_contact_count = 3 |
| TC-CRON-015 | Job handles trips with no events | New trip, no events | Row created with 0 counts |
| TC-CRON-016 | Job is idempotent | Run twice same hour | Same results, no duplicates |

### 4.3 Cleanup Sessions Job (TC-CRON-017 to TC-CRON-024)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-CRON-017 | Job executes every 15 minutes | Wait for interval | Job runs on schedule |
| TC-CRON-018 | Job closes sessions idle > 30 min | Session idle 35 min | ended_at set, duration calculated |
| TC-CRON-019 | Job preserves active sessions | Session active 10 min ago | Session NOT closed |
| TC-CRON-020 | Job calculates duration correctly | Session 45 min total | duration_seconds = 2700 |
| TC-CRON-021 | Job handles sessions with no events | Session started, no events | Closed with duration = 60s |
| TC-CRON-022 | Job processes multiple sessions | 100 stale sessions | All 100 closed in single run |
| TC-CRON-023 | Job handles timezone differences | UTC vs local timestamps | Correct comparison regardless of TZ |
| TC-CRON-024 | Job logs closed session count | Sessions closed | Log message shows count |

### 4.4 Aggregate Daily Metrics Job (TC-CRON-025 to TC-CRON-032)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-CRON-025 | Job executes at 02:00 UTC | Wait for 02:00 | Job runs within 60 seconds |
| TC-CRON-026 | Job aggregates previous day | Run at 02:00 Dec 16 | Metrics for Dec 15 created |
| TC-CRON-027 | Job calculates total_requests | 500 recommendations yesterday | total_requests = 500 |
| TC-CRON-028 | Job calculates unique_sessions | 200 unique sessions | unique_sessions = 200 |
| TC-CRON-029 | Job calculates response time percentiles | Various response times | p50, p95, p99 accurate |
| TC-CRON-030 | Job aggregates top_countries as JSONB | Searches with countries | top_countries JSON array |
| TC-CRON-031 | Job handles days with no data | No recommendations | Row created with 0s |
| TC-CRON-032 | Job upserts on conflict | Run twice for same date | Updates existing row |

---

## 5. Phase 0 Recommender System Tests

### 5.1 Scoring Algorithm (TC-REC-001 to TC-REC-015)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-REC-001 | Perfect budget match scores highest | Budget = trip price | Budget score component = 1.0 |
| TC-REC-002 | Budget 20% over scores lower | Budget 20% above price | Budget score reduced proportionally |
| TC-REC-003 | Budget 50% over scores very low | Budget 50% above price | Budget score < 0.5 |
| TC-REC-004 | Trip over budget excluded | Budget < trip price | Trip not in results (or score = 0) |
| TC-REC-005 | Duration exact match scores highest | Requested = actual duration | Duration score = 1.0 |
| TC-REC-006 | Duration +/- 2 days scores well | 2 day difference | Duration score > 0.8 |
| TC-REC-007 | Duration +/- 7 days scores lower | 7 day difference | Duration score < 0.5 |
| TC-REC-008 | Tag match increases score | 3 of 5 tags match | Tag score = 0.6 |
| TC-REC-009 | All tags match scores highest | All requested tags present | Tag score = 1.0 |
| TC-REC-010 | No tag match scores zero | No tags match | Tag score = 0 |
| TC-REC-011 | Country match adds bonus | Exact country match | Country score = 1.0 |
| TC-REC-012 | Continent match adds partial bonus | Same continent, different country | Continent score = 0.5 |
| TC-REC-013 | Difficulty preference affects score | Difficulty matches | Difficulty score = 1.0 |
| TC-REC-014 | Status preference (Guaranteed) bonus | Trip is Guaranteed | Status bonus applied |
| TC-REC-015 | Final score is weighted average | All components | score = sum(weight * component_score) |

### 5.2 Filter Logic (TC-REC-016 to TC-REC-025)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-REC-016 | Date range filter works | start_date, end_date provided | Only trips within range returned |
| TC-REC-017 | Departure after today filter | No past trips | All results have start_date >= today |
| TC-REC-018 | Budget filter hard cutoff | Budget = 2000 | No trips > 2000 in results |
| TC-REC-019 | Country filter is exact | country=Japan | Only Japan trips returned |
| TC-REC-020 | Continent filter includes all countries | continent=Asia | All Asian countries included |
| TC-REC-021 | Trip type filter works | type=Safari | Only Safari trips returned |
| TC-REC-022 | Multiple tag filter (OR logic) | tags=[Beach, Mountain] | Trips with Beach OR Mountain |
| TC-REC-023 | Difficulty filter range | difficulty=3 | Trips with difficulty 2-4 returned |
| TC-REC-024 | Status filter excludes Full | default | Full trips not returned |
| TC-REC-025 | Combined filters narrow results | All filters applied | Results satisfy ALL filters |

### 5.3 Edge Cases (TC-REC-026 to TC-REC-034)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-REC-026 | Zero budget returns free trips only | budget=0 | Only trips with price=0 (if any) |
| TC-REC-027 | Very high budget returns all | budget=999999 | All trips within budget |
| TC-REC-028 | 1-day duration preference | duration=1 | Day trips scored highest |
| TC-REC-029 | 30+ day duration preference | duration=45 | Long trips scored highest |
| TC-REC-030 | Empty preferences returns diverse results | No preferences | Results not empty, varied |
| TC-REC-031 | Conflicting filters returns empty | Impossible combination | Empty results, no error |
| TC-REC-032 | No matching trips triggers relaxation | Strict filters, no matches | Filters relaxed, partial matches shown |
| TC-REC-033 | Extremely long trip excluded | Trip > 90 days | Not returned for normal searches |
| TC-REC-034 | Results capped at limit | 500 matching trips | Only top N returned |

---

## 6. UI/UX & End-to-End Tests

### 6.1 Responsive Design - Desktop (TC-UI-001 to TC-UI-015)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-UI-001 | Header displays logo and navigation | Desktop viewport (1200px+) | Logo visible, nav links horizontal |
| TC-UI-002 | Search form shows all fields | Desktop viewport | Country, date, budget, tags all visible |
| TC-UI-003 | Results grid shows 3 columns | Desktop viewport | 3 trip cards per row |
| TC-UI-004 | Trip card shows image, title, price | Results page | All elements visible and readable |
| TC-UI-005 | Sidebar filters visible | Results page desktop | Filters panel on left side |
| TC-UI-006 | Sort dropdown accessible | Results page | Sort options in dropdown |
| TC-UI-007 | Trip details modal/page layout | Click trip card | Full details with large image |
| TC-UI-008 | Guide info displayed | Trip details | Guide photo, name, bio visible |
| TC-UI-009 | Company logo displayed | Trip details | Company branding visible |
| TC-UI-010 | Occurrence selector visible | Trip with multiple occurrences | Date picker/dropdown shows options |
| TC-UI-011 | Price displayed prominently | Trip card and details | Price clearly visible with currency |
| TC-UI-012 | Status badge visible | Trip card | Open/Guaranteed/Last Places badge |
| TC-UI-013 | Book Now button prominent | Trip details | CTA button clearly visible |
| TC-UI-014 | WhatsApp contact button | Trip details | WhatsApp icon/button visible |
| TC-UI-015 | Footer with company info | All pages | Footer visible with links |

### 6.2 Responsive Design - Mobile (TC-UI-016 to TC-UI-035)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-UI-016 | Hamburger menu on mobile | Mobile viewport (<768px) | Nav collapsed to hamburger |
| TC-UI-017 | Hamburger menu opens drawer | Tap hamburger | Full-screen nav drawer slides in |
| TC-UI-018 | Search form stacks vertically | Mobile viewport | Form fields stack, full width |
| TC-UI-019 | Results grid shows 1 column | Mobile viewport | 1 trip card per row, full width |
| TC-UI-020 | Filters in bottom sheet/modal | Mobile viewport | Filters hidden, accessible via button |
| TC-UI-021 | Filter button shows active count | Filters applied | "Filters (3)" badge visible |
| TC-UI-022 | Trip card touch target adequate | Mobile viewport | Card tappable area >= 44px |
| TC-UI-023 | Swipe gesture on trip images | Trip card with multiple images | Swipe to see more images |
| TC-UI-024 | Pull-to-refresh on results | Mobile results page | Pull down refreshes results |
| TC-UI-025 | Sticky header on scroll | Mobile viewport, scroll down | Header remains visible |
| TC-UI-026 | Bottom navigation bar | Mobile viewport | Home, Search, Favorites, Profile |
| TC-UI-027 | Trip details scrollable | Mobile trip details | Content scrolls, CTA fixed bottom |
| TC-UI-028 | Book Now sticky on mobile | Trip details, scroll | Book Now button stays visible |
| TC-UI-029 | Phone number tap-to-call | Mobile trip details | tel: link opens dialer |
| TC-UI-030 | WhatsApp tap opens app | Mobile trip details | Opens WhatsApp with pre-filled message |
| TC-UI-031 | Images optimized for mobile | Mobile viewport | Smaller images loaded (srcset) |
| TC-UI-032 | Font sizes readable on mobile | Mobile viewport | Min 16px body text |
| TC-UI-033 | No horizontal scroll | Any mobile page | Content fits viewport width |
| TC-UI-034 | Landscape orientation support | Rotate to landscape | Layout adjusts gracefully |
| TC-UI-035 | Virtual keyboard doesn't break layout | Open keyboard on form | Form remains usable |

### 6.3 Search Flow E2E (TC-UI-036 to TC-UI-050)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-UI-036 | Landing page loads | Navigate to / | Hero section, search CTA visible |
| TC-UI-037 | Click search navigates to /search | Click "Find Your Trip" | Search page loads |
| TC-UI-038 | Country dropdown populated | Search page | All countries selectable |
| TC-UI-039 | Date picker works | Click date field | Calendar opens, dates selectable |
| TC-UI-040 | Budget slider works | Adjust budget | Min/max values update |
| TC-UI-041 | Tags multi-select works | Click tags | Multiple tags selectable |
| TC-UI-042 | Submit search navigates to results | Click Search | /search/results with query params |
| TC-UI-043 | Results display matching trips | Valid search | Trips matching criteria shown |
| TC-UI-044 | Results show total count | Results loaded | "42 trips found" message |
| TC-UI-045 | Click trip card opens details | Click any trip | Trip details page/modal opens |
| TC-UI-046 | Back button returns to results | Trip details | Results page with scroll position |
| TC-UI-047 | Modify search returns new results | Change filter, resubmit | Updated results displayed |
| TC-UI-048 | Clear filters works | Click "Clear All" | All filters reset |
| TC-UI-049 | URL reflects search state | Apply filters | Query params updated in URL |
| TC-UI-050 | Shareable URL works | Copy URL, open in new tab | Same results displayed |

### 6.4 Trip Details & Booking Flow (TC-UI-051 to TC-UI-065)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-UI-051 | Trip details page loads | Navigate to /trip/:id | Full trip details displayed |
| TC-UI-052 | Multiple occurrences shown | Trip with 3 departures | All 3 dates visible for selection |
| TC-UI-053 | Selecting occurrence updates price | Select different date | Price updates to occurrence price |
| TC-UI-054 | Selecting occurrence updates status | Select Full occurrence | Status shows "Full", Book disabled |
| TC-UI-055 | Image gallery displays | Trip with images | Main image + thumbnails |
| TC-UI-056 | Image zoom on click | Click main image | Lightbox/zoom opens |
| TC-UI-057 | Trip description renders markdown | Description with formatting | Headers, lists render correctly |
| TC-UI-058 | Itinerary displayed | Trip with itinerary | Day-by-day breakdown visible |
| TC-UI-059 | Tags displayed | Trip with tags | Tag pills visible |
| TC-UI-060 | Difficulty indicator shown | Any trip | 1-5 difficulty visualization |
| TC-UI-061 | Spots left indicator | Trip with limited spots | "3 spots left" warning |
| TC-UI-062 | Book Now click tracks event | Click Book Now | booking_start event logged |
| TC-UI-063 | Book Now passes occurrence ID | Click Book Now | Correct occurrence_id in booking |
| TC-UI-064 | Save trip to favorites | Click save icon | Trip saved, icon filled |
| TC-UI-065 | Share trip functionality | Click share | Share modal with copy link |

### 6.5 Visual Feedback (TC-UI-066 to TC-UI-075)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-UI-066 | Loading spinner on search | Submit search | Spinner visible during load |
| TC-UI-067 | Skeleton cards on results load | Results loading | Skeleton placeholders shown |
| TC-UI-068 | Success toast on save | Save trip | "Trip saved!" toast appears |
| TC-UI-069 | Error toast on API failure | API returns 500 | "Something went wrong" toast |
| TC-UI-070 | Form validation errors inline | Submit invalid form | Error messages next to fields |
| TC-UI-071 | Button loading state | Click Book Now | Button shows spinner, disabled |
| TC-UI-072 | Empty state on no results | Search with no matches | "No trips found" illustration |
| TC-UI-073 | Hover effects on cards | Hover over trip card | Card elevates/shadows |
| TC-UI-074 | Focus states visible | Tab through page | Focus rings on interactive elements |
| TC-UI-075 | Progress indicator on multi-step | If booking is multi-step | Step indicator visible |

### 6.6 Images & Media (TC-UI-076 to TC-UI-082)

| ID | Description | Pre-conditions | Expected Result |
|----|-------------|----------------|-----------------|
| TC-UI-076 | Occurrence image override displayed | Occurrence with image_url_override | Override image shown, not template |
| TC-UI-077 | Template default image fallback | Occurrence without override | Template default_image_url shown |
| TC-UI-078 | Broken image fallback | Invalid image URL | Placeholder image displayed |
| TC-UI-079 | Lazy loading on images | Results page | Images load as scrolled into view |
| TC-UI-080 | Image alt text present | Any image | Descriptive alt text for accessibility |
| TC-UI-081 | Continent images display | Filter by continent | Correct continent illustration |
| TC-UI-082 | Company logo displayed | Trip card/details | Company logo visible |

---

## Test Summary Matrix

### Test Count by Category

| Category | Count | Priority | Automation Feasibility |
|----------|-------|----------|------------------------|
| Database Schema V2 & Migration | 52 | Critical | 100% - SQL/ORM tests |
| Backend API & Logic | 62 | Critical | 100% - API tests (Pytest) |
| Phase 1 Analytics & User Tracking | 50 | High | 90% - API + localStorage mocks |
| Automated Cron Jobs (APScheduler) | 32 | High | 80% - Unit tests + time mocks |
| Phase 0 Recommender System | 34 | High | 100% - Unit tests |
| UI/UX & End-to-End | 82 | Medium | 85% - Cypress/Playwright |
| **Total** | **312** | - | **~93%** |

### Test Priority Distribution

| Priority | Count | Percentage |
|----------|-------|------------|
| Critical | 114 | 37% |
| High | 116 | 37% |
| Medium | 82 | 26% |

### Suggested Test Execution Phases

| Phase | Tests | Duration Estimate |
|-------|-------|-------------------|
| Phase 1: Core DB & API | TC-DB-*, TC-API-* | 2-3 days |
| Phase 2: Analytics & Jobs | TC-ANA-*, TC-CRON-* | 2 days |
| Phase 3: Recommender | TC-REC-* | 1 day |
| Phase 4: UI/E2E | TC-UI-* | 3-4 days |
| **Total** | All 312 | **8-10 days** |

---

## Appendix A: Test Data Requirements

### Minimum Data Set for Testing

```sql
-- Required counts for comprehensive testing
SELECT 'companies' as entity, COUNT(*) FROM companies;          -- >= 10
SELECT 'trip_templates' as entity, COUNT(*) FROM trip_templates; -- >= 500
SELECT 'trip_occurrences' as entity, COUNT(*) FROM trip_occurrences; -- >= 700
SELECT 'countries' as entity, COUNT(*) FROM countries;          -- >= 50
SELECT 'guides' as entity, COUNT(*) FROM guides;                -- >= 20
SELECT 'trip_types' as entity, COUNT(*) FROM trip_types;        -- >= 10
SELECT 'tags' as entity, COUNT(*) FROM tags;                    -- >= 20
SELECT 'sessions' as entity, COUNT(*) FROM sessions;            -- >= 100
SELECT 'events' as entity, COUNT(*) FROM events;                -- >= 1000
```

### Test User Personas

| Persona | Description | Test Scenarios |
|---------|-------------|----------------|
| Anonymous Browser | First-time visitor, no account | TC-ANA-001 to TC-ANA-015 |
| Budget Traveler | Max budget $1000 | TC-REC-001 to TC-REC-005 |
| Adventure Seeker | Tags: Hiking, Safari, Expedition | TC-REC-008 to TC-REC-010 |
| Luxury Traveler | High budget, difficulty 1-2 | TC-REC-002, TC-REC-013 |
| Mobile User | All testing on mobile viewport | TC-UI-016 to TC-UI-035 |

---

## Appendix B: Automation Framework Recommendations

### Backend Tests (Pytest)

```python
# tests/test_db_schema.py
# tests/test_api_endpoints.py
# tests/test_analytics.py
# tests/test_recommender.py
# tests/test_scheduler.py
```

### Frontend Tests (Cypress/Playwright)

```javascript
// cypress/e2e/search-flow.cy.js
// cypress/e2e/trip-details.cy.js
// cypress/e2e/mobile-responsive.cy.js
// cypress/e2e/analytics-tracking.cy.js
```

### CI/CD Integration

```yaml
# GitHub Actions suggested workflow
- Run DB tests on PR
- Run API tests on PR
- Run E2E tests on merge to main
- Run full suite weekly
```

---

*Document End - Master Test Plan v1.0*
