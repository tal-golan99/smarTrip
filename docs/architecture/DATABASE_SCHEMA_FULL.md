# SmartTrip Database Schema - Complete Reference

**Generated:** December 16, 2025  
**Last Updated:** December 16, 2025 (Properties JSONB)  
**Database:** PostgreSQL (Render)  
**Schema Version:** 2.3 (+ Properties JSONB columns)

---

## Table of Contents

1. [Core Business Tables](#core-business-tables)
   - [companies](#companies)
   - [trip_templates](#trip_templates)
   - [trip_occurrences](#trip_occurrences)
   - [trips (legacy)](#trips-legacy)
2. [Reference Tables](#reference-tables)
   - [countries](#countries)
   - [guides](#guides)
   - [trip_types](#trip_types)
   - [tags](#tags)
3. [Junction Tables](#junction-tables)
   - [trip_template_tags](#trip_template_tags)
   - [trip_template_countries](#trip_template_countries)
   - [trip_tags (legacy)](#trip_tags-legacy)
4. [Analytics Tables](#analytics-tables)
   - [price_history](#price_history)
   - [reviews](#reviews)
5. [User Tracking Tables](#user-tracking-tables)
   - [event_categories](#event_categories) (NEW - 3NF)
   - [event_types](#event_types) (NEW - 3NF)
   - [users](#users)
   - [sessions](#sessions)
   - [events](#events)
   - [trip_interactions](#trip_interactions)
6. [Recommendation Logging Tables](#recommendation-logging-tables)
   - [recommendation_requests](#recommendation_requests)
   - [recommendation_metrics_daily](#recommendation_metrics_daily)
   - [evaluation_scenarios](#evaluation_scenarios)
7. [Entity Relationship Diagram](#entity-relationship-diagram)
8. [Views](#views)

---

## Core Business Tables

### companies

Travel companies/tour operators that organize trips.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `name` | VARCHAR(255) | NO | - | Company name (English), UNIQUE |
| `name_he` | VARCHAR(255) | NO | - | Company name (Hebrew) |
| `description` | TEXT | YES | - | Description (English) |
| `description_he` | TEXT | YES | - | Description (Hebrew) |
| `logo_url` | VARCHAR(500) | YES | - | URL to company logo |
| `website_url` | VARCHAR(500) | YES | - | Company website |
| `email` | VARCHAR(255) | YES | - | Contact email |
| `phone` | VARCHAR(50) | YES | - | Contact phone |
| `address` | TEXT | YES | - | Physical address |
| `is_active` | BOOLEAN | NO | true | Active status |
| `created_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Record creation |
| `updated_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Last update |

**Indexes:** `ix_companies_name`, `ix_companies_is_active`  
**Row Count:** 10

---

### trip_templates

Trip definitions - the "what" of a trip (route, description, base pricing).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `title` | VARCHAR(255) | NO | - | Trip title (English) |
| `title_he` | VARCHAR(255) | NO | - | Trip title (Hebrew) |
| `description` | TEXT | NO | - | Full description (English) |
| `description_he` | TEXT | NO | - | Full description (Hebrew) |
| `short_description` | VARCHAR(500) | YES | - | Brief description (English) |
| `short_description_he` | VARCHAR(500) | YES | - | Brief description (Hebrew) |
| `image_url` | VARCHAR(500) | YES | - | Default trip image |
| `base_price` | NUMERIC(10,2) | NO | - | Base price in currency |
| `single_supplement_price` | NUMERIC(10,2) | YES | - | Single room supplement |
| `typical_duration_days` | INTEGER | NO | - | Typical trip length |
| `default_max_capacity` | INTEGER | NO | - | Default group size |
| `difficulty_level` | SMALLINT | NO | - | 1-5 difficulty scale |
| `company_id` | INTEGER | NO | - | FK -> companies.id |
| `trip_type_id` | INTEGER | YES | - | FK -> trip_types.id |
| `primary_country_id` | INTEGER | YES | - | FK -> countries.id |
| `is_active` | BOOLEAN | NO | true | Active status |
| `properties` | JSONB | YES | - | Extensible metadata (packing_list, requirements, etc.) |
| `created_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Record creation |
| `updated_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Last update |

**Foreign Keys:**
- `company_id` -> `companies.id` (ON DELETE RESTRICT)
- `trip_type_id` -> `trip_types.id` (ON DELETE RESTRICT)
- `primary_country_id` -> `countries.id` (ON DELETE RESTRICT)

**Properties JSONB Examples:**
```json
{
  "packing_list": ["hiking boots", "rain jacket", "camera"],
  "requirements": {
    "visa": "Required for US citizens",
    "vaccinations": ["Yellow Fever"],
    "fitness_level": "Moderate"
  },
  "cabin_type": "Deluxe Ocean View"
}
```

**Constraints:**
- `ck_templates_duration_positive`: typical_duration_days > 0
- `ck_templates_price_positive`: base_price >= 0
- `difficulty_level BETWEEN 1 AND 5`

**Indexes:** `ix_trip_templates_company`, `ix_trip_templates_type`, `ix_trip_templates_country`, `ix_trip_templates_active`, `ix_trip_templates_difficulty`, `ix_trip_templates_title`  
**Row Count:** 500

---

### trip_occurrences

Scheduled instances of trip templates - the "when" of a trip.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `trip_template_id` | INTEGER | NO | - | FK -> trip_templates.id |
| `guide_id` | INTEGER | YES | - | FK -> guides.id |
| `start_date` | DATE | NO | - | Trip start date |
| `end_date` | DATE | NO | - | Trip end date |
| `price_override` | NUMERIC(10,2) | YES | - | Override base_price |
| `single_supplement_override` | NUMERIC(10,2) | YES | - | Override supplement |
| `max_capacity_override` | INTEGER | YES | - | Override capacity |
| `spots_left` | INTEGER | NO | - | Available spots |
| `status` | VARCHAR(20) | NO | 'Open' | Open/Guaranteed/Last Places/Full/Cancelled |
| `image_url_override` | VARCHAR(500) | YES | - | Seasonal image override |
| `notes` | TEXT | YES | - | Notes (English) |
| `notes_he` | TEXT | YES | - | Notes (Hebrew) |
| `properties` | JSONB | YES | - | Occurrence-specific metadata |
| `created_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Record creation |
| `updated_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Last update |

**Foreign Keys:**
- `trip_template_id` -> `trip_templates.id` (ON DELETE RESTRICT)
- `guide_id` -> `guides.id` (ON DELETE SET NULL)

**Properties JSONB Examples:**
```json
{
  "special_requirements": "This departure requires advanced scuba certification",
  "cabin_assignment": "Deck 5, Cabin 512",
  "equipment_provided": ["snorkeling gear", "binoculars"]
}
```

**Constraints:**
- `ck_occurrences_valid_dates`: end_date >= start_date
- `spots_left >= 0`

**Indexes:** `ix_trip_occurrences_template`, `ix_trip_occurrences_guide`, `ix_trip_occurrences_dates`, `ix_trip_occurrences_status`  
**Row Count:** 500

---

### trips (legacy)

Original trips table - kept for backward compatibility.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `title` | VARCHAR(255) | NO | - | Trip title (English) |
| `title_he` | VARCHAR(255) | NO | - | Trip title (Hebrew) |
| `description` | TEXT | NO | - | Full description (English) |
| `description_he` | TEXT | NO | - | Full description (Hebrew) |
| `image_url` | VARCHAR(500) | YES | - | Trip image |
| `start_date` | DATE | NO | - | Trip start date |
| `end_date` | DATE | NO | - | Trip end date |
| `price` | NUMERIC(10,2) | NO | - | Trip price |
| `single_supplement_price` | NUMERIC(10,2) | YES | - | Single room supplement |
| `max_capacity` | INTEGER | NO | - | Maximum group size |
| `spots_left` | INTEGER | NO | - | Available spots |
| `status` | ENUM | NO | - | TripStatus enum |
| `difficulty_level` | SMALLINT | NO | - | 1-5 difficulty scale |
| `country_id` | INTEGER | NO | - | FK -> countries.id |
| `guide_id` | INTEGER | NO | - | FK -> guides.id |
| `trip_type_id` | INTEGER | YES | - | FK -> trip_types.id |
| `company_id` | INTEGER | NO | - | FK -> companies.id |
| `created_at` | TIMESTAMP | NO | - | Record creation |
| `updated_at` | TIMESTAMP | NO | - | Last update |

**Foreign Keys:**
- `country_id` -> `countries.id`
- `guide_id` -> `guides.id`
- `trip_type_id` -> `trip_types.id`
- `company_id` -> `companies.id`

**Row Count:** 500

---

## Reference Tables

### countries

Destination countries.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `name` | VARCHAR(100) | NO | - | Country name (English), UNIQUE |
| `name_he` | VARCHAR(100) | NO | - | Country name (Hebrew) |
| `continent` | ENUM | NO | - | Continent (Africa/Asia/Europe/etc.) |
| `created_at` | TIMESTAMP | NO | - | Record creation |
| `updated_at` | TIMESTAMP | NO | - | Last update |

**Row Count:** 122

---

### guides

Tour guides.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `name` | VARCHAR(100) | NO | - | Guide name (English) |
| `name_he` | VARCHAR(100) | YES | - | Guide name (Hebrew) |
| `email` | VARCHAR(255) | NO | - | Email, UNIQUE |
| `phone` | VARCHAR(20) | YES | - | Phone number |
| `gender` | ENUM | NO | - | Male/Female/Other |
| `age` | INTEGER | YES | - | Age |
| `bio` | TEXT | YES | - | Biography (English) |
| `bio_he` | TEXT | YES | - | Biography (Hebrew) |
| `image_url` | VARCHAR(500) | YES | - | Profile image |
| `is_active` | BOOLEAN | NO | - | Active status |
| `created_at` | TIMESTAMP | NO | - | Record creation |
| `updated_at` | TIMESTAMP | NO | - | Last update |

**Row Count:** 25

---

### trip_types

Trip style categories.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `name` | VARCHAR(100) | NO | - | Type name (English), UNIQUE |
| `name_he` | VARCHAR(100) | NO | - | Type name (Hebrew) |
| `description` | TEXT | YES | - | Description |
| `created_at` | TIMESTAMP | NO | - | Record creation |
| `updated_at` | TIMESTAMP | NO | - | Last update |

**Values:** Geographic Depth, African Safari, Snowmobile Tours, Jeep Tours, Train Tours, Geographic Cruises, Nature Hiking, Carnivals & Festivals, Photography, Private Groups

**Row Count:** 10

---

### tags

Theme tags for trips.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `name` | VARCHAR(100) | NO | - | Tag name (English), UNIQUE |
| `name_he` | VARCHAR(100) | NO | - | Tag name (Hebrew) |
| `description` | TEXT | YES | - | Description |
| `created_at` | TIMESTAMP | NO | - | Record creation |
| `updated_at` | TIMESTAMP | NO | - | Last update |

**Row Count:** 10

---

## Junction Tables

### trip_template_tags

Many-to-many: TripTemplate <-> Tag

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `trip_template_id` | INTEGER | NO | - | PK, FK -> trip_templates.id |
| `tag_id` | INTEGER | NO | - | PK, FK -> tags.id |
| `created_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Record creation |

**Primary Key:** (trip_template_id, tag_id)  
**Row Count:** 971

---

### trip_template_countries

Many-to-many: TripTemplate <-> Country (multi-country support)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `trip_template_id` | INTEGER | NO | - | PK, FK -> trip_templates.id |
| `country_id` | INTEGER | NO | - | PK, FK -> countries.id |
| `visit_order` | INTEGER | NO | 1 | Order of country visit |
| `days_in_country` | INTEGER | YES | - | Days spent in country |
| `created_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Record creation |

**Primary Key:** (trip_template_id, country_id)  
**Row Count:** 500

---

### trip_tags (legacy)

Many-to-many: Trip <-> Tag (original)

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `trip_id` | INTEGER | NO | - | PK, FK -> trips.id |
| `tag_id` | INTEGER | NO | - | PK, FK -> tags.id |
| `created_at` | TIMESTAMP | NO | - | Record creation |

**Primary Key:** (trip_id, tag_id)  
**Row Count:** 971

---

## Analytics Tables

### price_history

Tracks price changes for analytics.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `trip_template_id` | INTEGER | NO | - | FK -> trip_templates.id |
| `old_price` | NUMERIC(10,2) | YES | - | Previous price |
| `new_price` | NUMERIC(10,2) | NO | - | New price |
| `change_reason` | VARCHAR(255) | YES | - | Reason for change |
| `changed_by` | VARCHAR(100) | YES | - | Who made the change |
| `changed_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | When changed |

**Foreign Keys:** `trip_template_id` -> `trip_templates.id` (ON DELETE CASCADE)  
**Row Count:** 500

---

### reviews

User reviews for trips.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `trip_occurrence_id` | INTEGER | NO | - | FK -> trip_occurrences.id |
| `reviewer_name` | VARCHAR(100) | YES | - | Reviewer name |
| `reviewer_email` | VARCHAR(255) | YES | - | Reviewer email |
| `is_anonymous` | BOOLEAN | NO | false | Hide reviewer name |
| `rating` | SMALLINT | NO | - | 1-5 stars |
| `title` | VARCHAR(200) | YES | - | Review title |
| `content` | TEXT | YES | - | Review content (English) |
| `content_he` | TEXT | YES | - | Review content (Hebrew) |
| `source` | VARCHAR(20) | NO | 'Website' | Website/App/Email/Imported |
| `is_approved` | BOOLEAN | NO | false | Moderation approved |
| `is_featured` | BOOLEAN | NO | false | Featured review |
| `created_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Record creation |
| `updated_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Last update |

**Foreign Keys:** `trip_occurrence_id` -> `trip_occurrences.id` (ON DELETE CASCADE)  
**Constraints:** `rating BETWEEN 1 AND 5`  
**Row Count:** 0

---

## User Tracking Tables

### event_categories

Event category groupings (3NF normalized).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | - | Primary Key |
| `name` | VARCHAR(50) | NO | - | Category name (English), UNIQUE |
| `name_he` | VARCHAR(50) | NO | - | Category name (Hebrew) |
| `description` | TEXT | YES | - | Description |
| `created_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Record creation |

**Values:**
| ID | Name | Hebrew | Description |
|----|------|--------|-------------|
| 1 | navigation | ניווט | Page navigation and browsing events |
| 2 | search | חיפוש | Search and filter events |
| 3 | engagement | מעורבות | User engagement with content |
| 4 | conversion | המרה | Conversion and booking events |

**Row Count:** 4

---

### event_types

Specific event types with FK to categories (3NF normalized).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | - | Primary Key |
| `name` | VARCHAR(50) | NO | - | Type name (English), UNIQUE |
| `name_he` | VARCHAR(50) | NO | - | Type name (Hebrew) |
| `category_id` | INTEGER | NO | - | FK -> event_categories.id |
| `description` | TEXT | YES | - | Description |
| `created_at` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Record creation |

**Foreign Keys:** `category_id` -> `event_categories.id` (ON DELETE RESTRICT)

**Values:**
| ID | Name | Category | Description |
|----|------|----------|-------------|
| 1 | page_view | navigation | User viewed a page |
| 2 | session_start | navigation | User started a new session |
| 3 | session_end | navigation | User session ended |
| 4 | search | search | User performed a search |
| 5 | filter_change | search | User changed a filter |
| 6 | filter_removed | search | User removed a filter |
| 7 | sort_change | search | User changed sort order |
| 8 | click_trip | engagement | User clicked on a trip |
| 9 | trip_dwell_time | engagement | Time spent on trip page |
| 10 | save_trip | engagement | User saved a trip |
| 11 | unsave_trip | engagement | User removed saved trip |
| 12 | share_trip | engagement | User shared a trip |
| 13 | impression | engagement | Trip shown in results |
| 14 | scroll_depth | engagement | How far user scrolled |
| 15 | contact_whatsapp | conversion | User contacted via WhatsApp |
| 16 | contact_phone | conversion | User contacted via phone |
| 17 | contact_email | conversion | User contacted via email |
| 18 | booking_start | conversion | User started booking process |
| 19 | booking_complete | conversion | User completed booking |
| 20 | inquiry_submit | conversion | User submitted inquiry |

**Row Count:** 20

---

### users

Tracked users (anonymous or registered).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `anonymous_id` | UUID | NO | - | Anonymous identifier |
| `email` | VARCHAR(255) | YES | - | Email (if registered) |
| `name` | VARCHAR(100) | YES | - | Name (English) |
| `name_he` | VARCHAR(100) | YES | - | Name (Hebrew) |
| `phone` | VARCHAR(20) | YES | - | Phone |
| `first_seen_at` | TIMESTAMP | YES | - | First visit |
| `last_seen_at` | TIMESTAMP | YES | - | Last visit |
| `total_sessions` | INTEGER | YES | - | Session count |
| `total_searches` | INTEGER | YES | - | Search count |
| `total_clicks` | INTEGER | YES | - | Click count |
| `is_registered` | BOOLEAN | YES | - | Has account |
| `is_active` | BOOLEAN | YES | - | Active user |
| `created_at` | TIMESTAMP | YES | - | Record creation |
| `updated_at` | TIMESTAMP | YES | - | Last update |

**Row Count:** 1

---

### sessions

User browsing sessions.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `session_id` | UUID | NO | - | Session identifier |
| `user_id` | INTEGER | YES | - | FK -> users.id |
| `anonymous_id` | UUID | NO | - | Anonymous identifier |
| `started_at` | TIMESTAMP | YES | - | Session start |
| `ended_at` | TIMESTAMP | YES | - | Session end |
| `duration_seconds` | INTEGER | YES | - | Total duration |
| `user_agent` | TEXT | YES | - | Browser/device info |
| `ip_address` | INET | YES | - | IP address |
| `referrer` | TEXT | YES | - | Traffic source |
| `device_type` | VARCHAR(20) | YES | - | desktop/mobile/tablet |
| `search_count` | INTEGER | YES | - | Searches in session |
| `click_count` | INTEGER | YES | - | Clicks in session |
| `save_count` | INTEGER | YES | - | Saves in session |
| `contact_count` | INTEGER | YES | - | Contacts in session |
| `created_at` | TIMESTAMP | YES | - | Record creation |

**Foreign Keys:** `user_id` -> `users.id`  
**Row Count:** 3

---

### events

Individual user actions/events (3NF normalized - uses FK to event_types).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | BIGINT | NO | AUTO | Primary Key |
| `user_id` | INTEGER | YES | - | FK -> users.id |
| `session_id` | UUID | NO | - | Session identifier |
| `anonymous_id` | UUID | NO | - | Anonymous identifier |
| `event_type_id` | INTEGER | NO | - | FK -> event_types.id |
| `trip_id` | INTEGER | YES | - | Related trip |
| `recommendation_request_id` | UUID | YES | - | Related recommendation |
| `source` | VARCHAR(50) | YES | - | search_results/homepage/etc. |
| `event_data` | JSONB | YES | - | Additional data |
| `position_in_results` | INTEGER | YES | - | Position when clicked |
| `score_at_time` | NUMERIC(5,2) | YES | - | Score when clicked |
| `timestamp` | TIMESTAMP | YES | - | Server timestamp |
| `client_timestamp` | TIMESTAMP | YES | - | Client timestamp |
| `page_url` | TEXT | YES | - | Current page |
| `referrer` | TEXT | YES | - | Previous page |
| `created_at` | TIMESTAMP | YES | - | Record creation |

**Foreign Keys:**
- `user_id` -> `users.id`
- `event_type_id` -> `event_types.id` (ON DELETE RESTRICT)

**Note:** Previously had `event_type` (VARCHAR) and `event_category` (VARCHAR) columns. Now normalized to use `event_type_id` FK which links to `event_types`, which links to `event_categories`.

**Row Count:** 306

---

### trip_interactions

Aggregated interaction metrics per trip.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `trip_id` | INTEGER | NO | - | Trip identifier |
| `impression_count` | INTEGER | YES | - | Total impressions |
| `unique_viewers` | INTEGER | YES | - | Unique viewers |
| `click_count` | INTEGER | YES | - | Total clicks |
| `unique_clickers` | INTEGER | YES | - | Unique clickers |
| `total_dwell_time_seconds` | INTEGER | YES | - | Total time spent |
| `avg_dwell_time_seconds` | INTEGER | YES | - | Average time spent |
| `save_count` | INTEGER | YES | - | Times saved |
| `whatsapp_contact_count` | INTEGER | YES | - | WhatsApp contacts |
| `phone_contact_count` | INTEGER | YES | - | Phone contacts |
| `booking_start_count` | INTEGER | YES | - | Booking starts |
| `click_through_rate` | NUMERIC(5,4) | YES | - | CTR |
| `save_rate` | NUMERIC(5,4) | YES | - | Save rate |
| `contact_rate` | NUMERIC(5,4) | YES | - | Contact rate |
| `impressions_7d` | INTEGER | YES | - | Last 7 days impressions |
| `clicks_7d` | INTEGER | YES | - | Last 7 days clicks |
| `last_clicked_at` | TIMESTAMP | YES | - | Last click time |
| `updated_at` | TIMESTAMP | YES | - | Last update |

**Row Count:** 4

---

## Recommendation Logging Tables

### recommendation_requests

Logged recommendation API requests.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `request_id` | UUID | NO | - | Unique request ID |
| `session_id` | VARCHAR(64) | YES | - | Session identifier |
| `user_id` | INTEGER | YES | - | User identifier |
| `created_at` | TIMESTAMP | YES | now() | Request time |
| `preferences` | JSONB | NO | - | Search preferences |
| `selected_countries` | ARRAY | YES | - | Selected countries |
| `selected_continents` | ARRAY | YES | - | Selected continents |
| `preferred_type_id` | INTEGER | YES | - | Trip type filter |
| `preferred_theme_ids` | ARRAY | YES | - | Theme filters |
| `min_duration` | INTEGER | YES | - | Min days |
| `max_duration` | INTEGER | YES | - | Max days |
| `budget` | NUMERIC(10,2) | YES | - | Max budget |
| `difficulty` | INTEGER | YES | - | Difficulty filter |
| `year` | VARCHAR(4) | YES | - | Year filter |
| `month` | VARCHAR(2) | YES | - | Month filter |
| `response_time_ms` | INTEGER | NO | - | Response time |
| `total_candidates` | INTEGER | NO | - | Trips evaluated |
| `primary_count` | INTEGER | NO | - | Primary results |
| `relaxed_count` | INTEGER | NO | 0 | Relaxed results |
| `final_count` | INTEGER | NO | - | Total results |
| `has_relaxed_results` | BOOLEAN | YES | false | Has relaxed |
| `has_no_results` | BOOLEAN | YES | false | No results |
| `top_score` | NUMERIC(5,2) | YES | - | Highest score |
| `avg_score` | NUMERIC(5,2) | YES | - | Average score |
| `min_score` | NUMERIC(5,2) | YES | - | Lowest score |
| `score_std_dev` | NUMERIC(5,2) | YES | - | Score std dev |
| `result_trip_ids` | ARRAY | NO | - | Result IDs |
| `result_scores` | ARRAY | NO | - | Result scores |
| `algorithm_version` | VARCHAR(32) | YES | 'v1.0' | Algorithm version |

**Row Count:** 7

---

### recommendation_metrics_daily

Daily aggregated recommendation metrics.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `date` | DATE | NO | - | Metrics date |
| `total_requests` | INTEGER | NO | 0 | Total requests |
| `unique_sessions` | INTEGER | NO | 0 | Unique sessions |
| `avg_response_time_ms` | NUMERIC(10,2) | YES | - | Avg response time |
| `p50_response_time_ms` | INTEGER | YES | - | Median response |
| `p95_response_time_ms` | INTEGER | YES | - | 95th percentile |
| `p99_response_time_ms` | INTEGER | YES | - | 99th percentile |
| `max_response_time_ms` | INTEGER | YES | - | Max response |
| `avg_top_score` | NUMERIC(5,2) | YES | - | Avg top score |
| `avg_result_count` | NUMERIC(5,2) | YES | - | Avg results |
| `relaxed_trigger_rate` | NUMERIC(5,4) | YES | - | Relaxed rate |
| `no_results_rate` | NUMERIC(5,4) | YES | - | No results rate |
| `low_score_rate` | NUMERIC(5,4) | YES | - | Low score rate |
| `searches_with_country` | INTEGER | YES | - | Country filter count |
| `searches_with_continent` | INTEGER | YES | - | Continent filter count |
| `searches_with_type` | INTEGER | YES | - | Type filter count |
| `searches_with_themes` | INTEGER | YES | - | Theme filter count |
| `searches_with_budget` | INTEGER | YES | - | Budget filter count |
| `searches_with_dates` | INTEGER | YES | - | Date filter count |
| `top_countries` | JSONB | YES | - | Popular countries |
| `top_continents` | JSONB | YES | - | Popular continents |
| `top_types` | JSONB | YES | - | Popular types |
| `top_themes` | JSONB | YES | - | Popular themes |
| `created_at` | TIMESTAMP | YES | now() | Record creation |
| `updated_at` | TIMESTAMP | YES | now() | Last update |

**Row Count:** 0

---

### evaluation_scenarios

Test scenarios (100 user personas) for recommendation quality and regression testing.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | AUTO | Primary Key |
| `name` | VARCHAR(100) | NO | - | Scenario name |
| `description` | TEXT | YES | - | Description |
| `category` | VARCHAR(50) | YES | - | Category (core_persona/edge_case/regional/type_specific) |
| `preferences` | JSONB | NO | - | Test preferences (budget, themes, duration, etc.) |
| `expected_min_results` | INTEGER | YES | 1 | Min expected results |
| `expected_min_top_score` | NUMERIC(5,2) | YES | - | Min expected score |
| `expected_trip_types` | ARRAY | YES | - | Expected types |
| `expected_countries` | ARRAY | YES | - | Expected countries |
| `baseline_result_ids` | ARRAY | YES | - | Baseline results |
| `baseline_scores` | ARRAY | YES | - | Baseline scores |
| `baseline_captured_at` | TIMESTAMP | YES | - | Baseline capture time |
| `is_active` | BOOLEAN | YES | true | Active status |
| `priority` | INTEGER | YES | 5 | Priority (1-10) |
| `created_at` | TIMESTAMP | YES | now() | Record creation |
| `updated_at` | TIMESTAMP | YES | now() | Last update |

**Loaded Personas by Category:**
| Category | Count | Description |
|----------|-------|-------------|
| core_persona | 58 | Main user archetypes (Student, Retiree, Family, etc.) |
| regional | 26 | Region-specific preferences |
| type_specific | 8 | Trip type specialists |
| edge_case | 8 | Boundary/edge test cases |

**Row Count:** 100

---

## Entity Relationship Diagram

```
                                    +-------------+
                                    |  COMPANIES  |
                                    +------+------+
                                           |
                                           | 1:N
                                           v
+-------------+                   +----------------+                   +--------+
|  TRIP_TYPES | 1:N ------------> | TRIP_TEMPLATES | <---------------- | GUIDES |
+-------------+                   +-------+--------+                   +--------+
                                          |                                 ^
                                          | 1:N                             |
                                          v                                 |
                                 +-----------------+                        |
                                 | TRIP_OCCURRENCES| -----------------------+
                                 +--------+--------+        N:1
                                          |
                                          | 1:N
                                          v
                                    +---------+
                                    | REVIEWS |
                                    +---------+

+----------------+     N:M     +---------------------+     N:M     +----------+
| TRIP_TEMPLATES | <---------> | TRIP_TEMPLATE_TAGS  | <---------> |   TAGS   |
+----------------+             +---------------------+             +----------+

+----------------+     N:M     +-----------------------+     N:M     +-----------+
| TRIP_TEMPLATES | <---------> | TRIP_TEMPLATE_COUNTRIES| <--------> | COUNTRIES |
+----------------+             +-----------------------+             +-----------+

+----------------+     1:N     +---------------+
| TRIP_TEMPLATES | <---------> | PRICE_HISTORY |
+----------------+             +---------------+


+---------+     1:N     +----------+     1:N     +--------+
|  USERS  | <---------> | SESSIONS | <---------> | EVENTS |
+---------+             +----------+             +--------+
```

---

## Views

### trips_compat

Backward compatibility view combining trip_templates and trip_occurrences.

```sql
CREATE VIEW trips_compat AS
SELECT 
    o.id,
    tt.title, 
    tt.title_he,
    tt.description, 
    tt.description_he,
    COALESCE(o.image_url_override, tt.image_url) as image_url,
    o.start_date, 
    o.end_date,
    COALESCE(o.price_override, tt.base_price) as price,
    COALESCE(o.single_supplement_override, tt.single_supplement_price) as single_supplement_price,
    COALESCE(o.max_capacity_override, tt.default_max_capacity) as max_capacity,
    o.spots_left, 
    o.status,
    tt.difficulty_level,
    tt.primary_country_id as country_id, 
    o.guide_id, 
    tt.trip_type_id, 
    tt.company_id,
    o.created_at, 
    o.updated_at,
    o.trip_template_id,
    tt.typical_duration_days
FROM trip_occurrences o
JOIN trip_templates tt ON o.trip_template_id = tt.id
WHERE tt.is_active = TRUE;
```

---

## Backup Tables

The following backup tables exist from migrations:

- `trips_backup_20251216_154920` (500 rows)
- `trip_tags_backup_20251216_154920` (971 rows)
- `countries_backup_20251216_154920` (122 rows)
- `guides_backup_20251216_154920` (25 rows)
- `trip_types_backup_20251216_154920` (10 rows)
- `tags_backup_20251216_154920` (10 rows)
- `trips_backup_v2` (500 rows)
- `trip_tags_backup_v2` (971 rows)

---

## Summary Statistics

| Table | Rows | Notes |
|-------|------|-------|
| companies | 10 | Travel companies |
| trip_templates | 500 | Trip definitions |
| trip_occurrences | 500 | Scheduled instances |
| trips (legacy) | 500 | Old table, kept for compatibility |
| countries | 122 | Destinations |
| guides | 25 | Tour guides |
| trip_types | 10 | Trip categories |
| tags | 10 | Theme tags |
| trip_template_tags | 971 | Template-Tag junction |
| trip_template_countries | 500 | Multi-country support |
| trip_tags (legacy) | 971 | Old junction table |
| price_history | 500 | Price change tracking |
| reviews | 0 | User reviews |
| **event_categories** | **4** | **NEW: 3NF normalized** |
| **event_types** | **20** | **NEW: 3NF normalized** |
| users | 1 | Tracked users |
| sessions | 3 | User sessions |
| events | 306 | User actions (now uses event_type_id FK) |
| trip_interactions | 4 | Aggregated metrics |
| recommendation_requests | 7 | API request logs |
| recommendation_metrics_daily | 0 | Daily analytics |
| **evaluation_scenarios** | **100** | **100 user personas loaded** |
