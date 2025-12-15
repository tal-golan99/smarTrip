# SmartTrip Recommendation Engine
## Technical Documentation & Algorithm Specification

---

**Project:** SmartTrip Travel Recommendation Platform  
**Document Type:** Technical Specification & Algorithm Documentation  
**Version:** 1.0  
**Date:** December 14, 2025  
**Status:** Production Release  

**Authors:** SmartTrip Development Team  
**Document Owner:** Technical Architecture Team  

---

### Document Purpose

This document provides comprehensive technical documentation of the SmartTrip Recommendation Engine, including architecture, algorithms, data models, and implementation details. It is intended for:

- Software developers and engineers
- System architects
- Technical product managers
- QA and testing teams
- Future maintainers and contributors

---

<div style="page-break-after: always;"></div>

## Table of Contents

### Part I: Overview & Architecture
1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Visual System Overview](#visual-system-overview)

### Part II: Data & Models
4. [Data Model](#data-model)
5. [Database Schema Diagrams](#database-schema-diagrams)
6. [Entity Relationships](#entity-relationships)

### Part III: Core Algorithm
7. [Recommendation Algorithm Overview](#recommendation-algorithm-overview)
8. [Algorithm Flowcharts](#algorithm-flowcharts)
9. [Scoring System](#scoring-system)
10. [Scoring Decision Tree](#scoring-decision-tree)
11. [Filtering Logic](#filtering-logic)

### Part IV: Implementation
12. [API Flow](#api-flow)
13. [Technical Implementation](#technical-implementation)
14. [Performance Optimizations](#performance-optimizations)

### Part V: Testing & Configuration
15. [Test Results and Validation](#test-results-and-validation)
16. [Configuration Reference](#configuration-reference)

### Appendices
- [Appendix A: Complete Scoring Matrix](#appendix-a-complete-scoring-matrix)
- [Appendix B: Algorithm Pseudocode](#appendix-b-algorithm-pseudocode)
- [Appendix C: Glossary](#appendix-c-glossary)

---

<div style="page-break-after: always;"></div>

## Part I: Overview & Architecture

---

## Executive Summary

### Overview

The SmartTrip Recommendation Engine is a sophisticated, two-tier weighted scoring system that matches trips to user preferences across multiple criteria. It processes **587+ trips** across **105+ countries** and returns personalized recommendations with match scores ranging from **0-100**.

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **Architecture** | Two-tier system: Primary (strict) + Relaxed (flexible) |
| **Scoring Range** | 0-100 points with color-coded thresholds |
| **Base Score** | 25 points for all qualifying trips |
| **Criteria** | 6 major scoring dimensions (geography, themes, duration, budget, difficulty, urgency) |
| **Fallback Mechanism** | Automatic relaxed search when results < 6 |
| **Security** | Input validation, XSS protection, SQL injection prevention |
| **Performance** | Eager loading, indexed queries, ~2s response time |
| **Internationalization** | Full bilingual support (English/Hebrew) with RTL |

### Performance Metrics

```
Test Coverage:     255 automated tests
Pass Rate:         99.2%
Database Size:     587+ trips, 105+ countries
Avg Response Time: ~2 seconds
Query Efficiency:  3-4 queries per request (with eager loading)
```

### Business Impact

The recommendation engine serves as the core matching logic for the SmartTrip platform, enabling users to discover relevant travel experiences efficiently. The two-tier approach balances **precision** (showing highly relevant matches) with **recall** (ensuring users always see options).

---

<div style="page-break-after: always;"></div>

## System Architecture

### Technology Stack

#### Backend Layer
```
┌─────────────────────────────────────────┐
│         Flask 3.x (Python 3.10+)        │
│              RESTful API                │
├─────────────────────────────────────────┤
│         SQLAlchemy 2.x ORM              │
│        Database Abstraction             │
├─────────────────────────────────────────┤
│         PostgreSQL 12+                  │
│         Relational Database             │
└─────────────────────────────────────────┘
```

#### Frontend Layer
```
┌─────────────────────────────────────────┐
│       Next.js 14 (App Router)           │
│       React 18 + TypeScript             │
├─────────────────────────────────────────┤
│         API Client Layer                │
│      HTTP Request Management            │
├─────────────────────────────────────────┤
│         UI Components                   │
│    Search Form + Results Display        │
└─────────────────────────────────────────┘
```

### System Components

```mermaid
graph TB
    subgraph "Frontend (Next.js)"
        A[User Interface]
        B[Search Form]
        C[Results Display]
        D[API Client]
    end
    
    subgraph "Backend (Flask)"
        E[API Endpoints]
        F[Input Validation]
        G[Recommendation Engine]
        H[Scoring Algorithm]
        I[Database Layer]
    end
    
    subgraph "Database (PostgreSQL)"
        J[(Trips)]
        K[(Countries)]
        L[(Guides)]
        M[(Tags)]
    end
    
    A --> B
    B --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    I --> K
    I --> L
    I --> M
    C --> D
```

---

<div style="page-break-after: always;"></div>

## Visual System Overview

### High-Level Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Engine
    participant Database
    
    User->>Frontend: Enter search criteria
    Frontend->>Frontend: Validate input
    Frontend->>API: POST /api/recommendations
    API->>API: Sanitize & validate
    API->>Engine: Process preferences
    Engine->>Database: Query trips (hard filters)
    Database-->>Engine: Return candidates
    Engine->>Engine: Score each candidate
    Engine->>Engine: Sort by score + date
    
    alt Primary results >= 6
        Engine-->>API: Return top 10
    else Primary results < 6
        Engine->>Database: Relaxed query
        Database-->>Engine: Additional candidates
        Engine->>Engine: Score with penalty
        Engine-->>API: Return primary + relaxed
    end
    
    API-->>Frontend: JSON response with scores
    Frontend-->>User: Display ranked results
```

### Component Interaction Diagram

```mermaid
graph LR
    subgraph "User Layer"
        U[User Input]
    end
    
    subgraph "Presentation Layer"
        F1[Search Form]
        F2[Results Grid]
        F3[Trip Details]
    end
    
    subgraph "API Layer"
        A1[/api/recommendations]
        A2[/api/trips]
        A3[/api/locations]
    end
    
    subgraph "Business Logic"
        B1[Recommendation Engine]
        B2[Scoring Algorithm]
        B3[Filter Manager]
    end
    
    subgraph "Data Layer"
        D1[Trip Repository]
        D2[Country Repository]
        D3[Tag Repository]
    end
    
    U --> F1
    F1 --> A1
    A1 --> B1
    B1 --> B2
    B1 --> B3
    B2 --> D1
    B3 --> D1
    D1 --> D2
    D1 --> D3
    A1 --> F2
    F2 --> A2
    A2 --> F3
```

---

<div style="page-break-after: always;"></div>

## Part II: Data & Models

---

## Data Model

### Core Entities Overview

The SmartTrip database follows a normalized relational schema with 6 core entities:

| Entity | Purpose | Key Attributes |
|--------|---------|----------------|
| **Countries** | Geographic destinations | name, continent, bilingual names |
| **Guides** | Tour guide profiles | name, bio, specializations |
| **Trip Types** | Travel styles (hard filter) | name (e.g., Safari, Cruise) |
| **Tags (Themes)** | Interest categories (soft score) | name (e.g., Wildlife, Cultural) |
| **Trips** | Core trip offerings | dates, price, difficulty, status |
| **Trip Tags** | Many-to-many junction | links trips to themes |

### Entity Details

#### 1. Countries Table

```sql
CREATE TABLE countries (
    id                INTEGER PRIMARY KEY,
    name              VARCHAR(100) UNIQUE NOT NULL,
    name_he           VARCHAR(100) NOT NULL,
    continent         ENUM(Continent) NOT NULL,
    created_at        TIMESTAMP DEFAULT NOW(),
    updated_at        TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_continent (continent),
    INDEX idx_name (name)
);
```

**Continent Enum Values:**
- AFRICA
- ASIA  
- EUROPE
- NORTH_AND_CENTRAL_AMERICA
- SOUTH_AMERICA
- OCEANIA
- ANTARCTICA

**Statistics:** 105+ countries across 7 continents

#### 2. Guides Table

```sql
CREATE TABLE guides (
    id                INTEGER PRIMARY KEY,
    name              VARCHAR(100) NOT NULL,
    name_he           VARCHAR(100),
    email             VARCHAR(255) UNIQUE NOT NULL,
    phone             VARCHAR(20),
    gender            ENUM(Gender) NOT NULL,
    age               INTEGER,
    bio               TEXT,
    bio_he            TEXT,
    image_url         VARCHAR(500),
    is_active         BOOLEAN DEFAULT TRUE,
    created_at        TIMESTAMP DEFAULT NOW(),
    updated_at        TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_email (email),
    INDEX idx_is_active (is_active)
);
```

**Gender Enum:** MALE, FEMALE, OTHER

#### 3. Trip Types Table

```sql
CREATE TABLE trip_types (
    id                INTEGER PRIMARY KEY,
    name              VARCHAR(100) UNIQUE NOT NULL,
    name_he           VARCHAR(100) NOT NULL,
    description       TEXT,
    created_at        TIMESTAMP DEFAULT NOW(),
    updated_at        TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_name (name)
);
```

**Examples:** African Safari, Train Tour, Cruise, Desert Adventure, Nature Hiking, Private Groups

**Note:** Trip Type is a **HARD FILTER** - users select exactly one type, and it strictly filters results.

#### 4. Tags (Themes) Table

```sql
CREATE TABLE tags (
    id                INTEGER PRIMARY KEY,
    name              VARCHAR(100) UNIQUE NOT NULL,
    name_he           VARCHAR(100) NOT NULL,
    description       TEXT,
    category          ENUM(TagCategory) NOT NULL,
    created_at        TIMESTAMP DEFAULT NOW(),
    updated_at        TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_name (name),
    INDEX idx_category (category)
);
```

**TagCategory Enum:** 
- THEME (content focus: Wildlife, Cultural, Photography, etc.)
- TYPE (deprecated - migrated to trip_types table)

**Examples:** Wildlife, Photography, Cultural, Historical, Food & Wine, Mountain, Desert

**Note:** Themes are **SOFT SCORED** - users can select up to 3 themes for scoring bonuses.

#### 5. Trips Table

```sql
CREATE TABLE trips (
    id                      INTEGER PRIMARY KEY,
    title                   VARCHAR(255) NOT NULL,
    title_he                VARCHAR(255) NOT NULL,
    description             TEXT NOT NULL,
    description_he          TEXT NOT NULL,
    image_url               VARCHAR(500),
    start_date              DATE NOT NULL,
    end_date                DATE NOT NULL,
    price                   NUMERIC(10,2) NOT NULL,
    single_supplement_price NUMERIC(10,2),
    max_capacity            INTEGER NOT NULL,
    spots_left              INTEGER NOT NULL,
    status                  ENUM(TripStatus) DEFAULT 'Open',
    difficulty_level        SMALLINT NOT NULL,
    
    country_id              INTEGER REFERENCES countries(id),
    guide_id                INTEGER REFERENCES guides(id),
    trip_type_id            INTEGER REFERENCES trip_types(id),
    
    created_at              TIMESTAMP DEFAULT NOW(),
    updated_at              TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_start_date (start_date),
    INDEX idx_end_date (end_date),
    INDEX idx_country_id (country_id),
    INDEX idx_guide_id (guide_id),
    INDEX idx_trip_type_id (trip_type_id),
    INDEX idx_status (status),
    INDEX idx_difficulty_level (difficulty_level),
    INDEX idx_dates (start_date, end_date)
);
```

**TripStatus Enum:**
- OPEN: Available spots
- GUARANTEED: Confirmed departure (business priority)
- LAST_PLACES: Limited availability (urgency bonus)
- FULL: Sold out (filtered out)
- CANCELLED: Not available (filtered out)

**Difficulty Levels:**
- 1: Easy
- 2: Moderate
- 3: Hard
- 4: Challenging
- 5: Extreme

#### 6. Trip Tags Junction Table

```sql
CREATE TABLE trip_tags (
    trip_id           INTEGER REFERENCES trips(id) ON DELETE CASCADE,
    tag_id            INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    created_at        TIMESTAMP DEFAULT NOW(),
    
    PRIMARY KEY (trip_id, tag_id),
    INDEX idx_tag_id (tag_id)
);
```

**Purpose:** Many-to-many relationship between trips and theme tags.

---

<div style="page-break-after: always;"></div>

## Database Schema Diagrams

### Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    COUNTRIES ||--o{ TRIPS : "has many"
    GUIDES ||--o{ TRIPS : "leads"
    TRIP_TYPES ||--o{ TRIPS : "categorizes"
    TRIPS ||--o{ TRIP_TAGS : "has"
    TAGS ||--o{ TRIP_TAGS : "tagged in"
    
    COUNTRIES {
        int id PK
        string name UK
        string name_he
        enum continent
        timestamp created_at
        timestamp updated_at
    }
    
    GUIDES {
        int id PK
        string name
        string name_he
        string email UK
        string phone
        enum gender
        int age
        text bio
        text bio_he
        string image_url
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    TRIP_TYPES {
        int id PK
        string name UK
        string name_he
        text description
        timestamp created_at
        timestamp updated_at
    }
    
    TAGS {
        int id PK
        string name UK
        string name_he
        text description
        enum category
        timestamp created_at
        timestamp updated_at
    }
    
    TRIPS {
        int id PK
        string title
        string title_he
        text description
        text description_he
        string image_url
        date start_date
        date end_date
        numeric price
        numeric single_supplement_price
        int max_capacity
        int spots_left
        enum status
        smallint difficulty_level
        int country_id FK
        int guide_id FK
        int trip_type_id FK
        timestamp created_at
        timestamp updated_at
    }
    
    TRIP_TAGS {
        int trip_id FK
        int tag_id FK
        timestamp created_at
    }
```

### Data Flow Diagram

```mermaid
graph TD
    A[User Preferences] --> B{Geographic Filter}
    B -->|Countries| C[Direct Country Match]
    B -->|Continents| D[Continent Match]
    C --> E[Trip Query]
    D --> E
    
    E --> F[Filter by Trip Type]
    F --> G[Filter by Date Range]
    G --> H[Filter by Status]
    H --> I[Filter by Difficulty]
    I --> J[Filter by Budget]
    
    J --> K[Candidate Trips]
    K --> L[Score Each Trip]
    
    L --> M[Theme Scoring]
    L --> N[Difficulty Scoring]
    L --> O[Duration Scoring]
    L --> P[Budget Scoring]
    L --> Q[Status Scoring]
    L --> R[Geography Scoring]
    
    M --> S[Aggregate Score]
    N --> S
    O --> S
    P --> S
    Q --> S
    R --> S
    
    S --> T{Score >= 50?}
    T -->|Yes| U[High/Med Match]
    T -->|No| V[Low Match]
    
    U --> W[Sort by Score]
    V --> W
    W --> X[Top 10 Results]
```

---

<div style="page-break-after: always;"></div>

## Entity Relationships

### Relationship Summary

| Parent Entity | Child Entity | Relationship Type | Constraint |
|---------------|--------------|-------------------|------------|
| Countries | Trips | One-to-Many | RESTRICT on delete |
| Guides | Trips | One-to-Many | RESTRICT on delete |
| Trip Types | Trips | One-to-Many | RESTRICT on delete |
| Trips | Trip Tags | One-to-Many | CASCADE on delete |
| Tags | Trip Tags | One-to-Many | CASCADE on delete |

### Cascade Behavior

**RESTRICT (Countries, Guides, Trip Types → Trips):**
- Cannot delete a country/guide/type if trips reference it
- Ensures data integrity
- Prevents orphaned trip records

**CASCADE (Trips → Trip Tags):**
- Deleting a trip automatically deletes its tag associations
- Keeps junction table clean
- No orphaned trip-tag relationships

### Index Strategy

#### Primary Indexes (Auto-created)
- Primary keys on all tables
- Unique constraints on names and emails

#### Query Optimization Indexes

**trips table:**
```sql
CREATE INDEX idx_start_date ON trips(start_date);
CREATE INDEX idx_end_date ON trips(end_date);
CREATE INDEX idx_country_id ON trips(country_id);
CREATE INDEX idx_guide_id ON trips(guide_id);
CREATE INDEX idx_trip_type_id ON trips(trip_type_id);
CREATE INDEX idx_status ON trips(status);
CREATE INDEX idx_difficulty_level ON trips(difficulty_level);
CREATE INDEX idx_dates ON trips(start_date, end_date);  -- Composite
```

**trip_tags table:**
```sql
CREATE INDEX idx_tag_id ON trip_tags(tag_id);  -- For reverse lookups
```

**countries table:**
```sql
CREATE INDEX idx_continent ON countries(continent);
```

**Performance Impact:**
- Date range queries: O(log n) instead of O(n)
- Foreign key joins: Indexed access
- Status filtering: Bitmap index scan
- Composite index: Efficient date range queries

---

<div style="page-break-after: always;"></div>

## Part III: Core Algorithm

---

## Recommendation Algorithm Overview

### Design Philosophy

The algorithm balances **precision** (showing highly relevant matches) with **recall** (ensuring users always see options) through a two-tier approach:

1. **Primary Tier:** Strict filters for high-precision matches
2. **Relaxed Tier:** Expanded filters when primary results are insufficient

### Core Principles

| Principle | Implementation |
|-----------|----------------|
| **Base Score Foundation** | All qualifying trips start at 25 points |
| **Weighted Criteria** | Different aspects have different importance |
| **Penalty System** | Mismatches incur negative scores |
| **Business Priorities** | Urgency and status boost scores |
| **Geographic Hierarchy** | Direct > Continent > None |
| **Automatic Fallback** | Relaxed search triggers at < 6 results |

### Algorithm Stages

```
┌─────────────────────────────────────────────────────┐
│  STAGE 1: INPUT VALIDATION & SANITIZATION           │
│  - Type checking and conversion                     │
│  - Range validation (bounds checking)               │
│  - SQL injection prevention                         │
│  - XSS protection (HTML tag removal)                │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 2: HARD FILTERING (Primary Tier)            │
│  - Geography: countries OR continents               │
│  - Trip Type: exact match (if specified)            │
│  - Date: year/month exact match                     │
│  - Status: available spots only                     │
│  - Difficulty: within +/- 1 level                   │
│  - Duration: within +/- 7 days (checked in scoring) │
│  - Budget: up to 30% over budget                    │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 3: SCORING ALGORITHM                         │
│  - Base score: 25 points                            │
│  - Theme matching: +25/-15                          │
│  - Difficulty: +15                                  │
│  - Duration: +12/+8                                 │
│  - Budget: +12/+8/+5                                │
│  - Status: +7/+15                                   │
│  - Departing soon: +7                               │
│  - Geography: +15/+5                                │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 4: SORTING & RANKING                         │
│  - Primary: Score (descending)                      │
│  - Secondary: Start date (ascending)                │
│  - Float precision to avoid ties                    │
│  - Top 10 results selected                          │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 5: RELAXED SEARCH (if primary < 6)          │
│  - Expand geography to continent level              │
│  - Extend date range by +/- 2 months                │
│  - Difficulty: +/- 2 levels                         │
│  - Budget: up to 50% over                           │
│  - Trip type: all types (with -10 penalty)          │
│  - Apply -20 base penalty                           │
│  - Fill to 10 total results                         │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 6: RESPONSE ASSEMBLY                         │
│  - Combine primary + relaxed results                │
│  - Mark relaxed with is_relaxed flag                │
│  - Include match_details (scoring breakdown)        │
│  - Add color thresholds for UI                      │
│  - Return JSON response                             │
└─────────────────────────────────────────────────────┘
```

---

<div style="page-break-after: always;"></div>

## Algorithm Flowcharts

### Main Recommendation Flow

```mermaid
flowchart TD
    Start([User Submits Search]) --> Validate[Validate & Sanitize Input]
    Validate --> Build[Build Database Query]
    
    Build --> GeoFilter{Geographic<br/>Filter?}
    GeoFilter -->|Countries| CountryFilter[Filter by Country IDs]
    GeoFilter -->|Continents| ContinentFilter[Filter by Continent]
    GeoFilter -->|Both| UnionFilter[UNION: Countries OR Continents]
    GeoFilter -->|None| NoGeoFilter[No Geographic Filter]
    
    CountryFilter --> TypeFilter
    ContinentFilter --> TypeFilter
    UnionFilter --> TypeFilter
    NoGeoFilter --> TypeFilter
    
    TypeFilter{Trip Type<br/>Selected?} -->|Yes| ApplyType[Hard Filter: Type = X]
    TypeFilter -->|No| SkipType[No Type Filter]
    
    ApplyType --> DateFilter
    SkipType --> DateFilter
    
    DateFilter{Date<br/>Selected?} -->|Yes| ApplyDate[Filter Year/Month]
    DateFilter -->|No| FutureOnly[Filter: Date >= Today]
    
    ApplyDate --> StatusFilter
    FutureOnly --> StatusFilter
    
    StatusFilter[Filter: Status != Cancelled<br/>AND Spots > 0] --> DiffFilter
    
    DiffFilter{Difficulty<br/>Selected?} -->|Yes| ApplyDiff[Filter: +/- 1 Level]
    DiffFilter -->|No| SkipDiff[No Difficulty Filter]
    
    ApplyDiff --> BudgetFilter
    SkipDiff --> BudgetFilter
    
    BudgetFilter{Budget<br/>Specified?} -->|Yes| ApplyBudget[Filter: Price <= Budget * 1.3]
    BudgetFilter -->|No| SkipBudget[No Budget Filter]
    
    ApplyBudget --> ExecuteQuery
    SkipBudget --> ExecuteQuery
    
    ExecuteQuery[Execute Query<br/>Get Candidates] --> ScoreLoop[Score Each Candidate]
    
    ScoreLoop --> Score1[Base Score: +25]
    Score1 --> Score2[Theme Scoring]
    Score2 --> Score3[Difficulty Scoring]
    Score3 --> Score4[Duration Scoring]
    Score4 --> Score5[Budget Scoring]
    Score5 --> Score6[Status Scoring]
    Score6 --> Score7[Geography Scoring]
    Score7 --> Clamp[Clamp Score: 0-100]
    
    Clamp --> Sort[Sort by Score DESC,<br/>Date ASC]
    Sort --> Top10[Select Top 10]
    
    Top10 --> CheckCount{Count >= 6?}
    CheckCount -->|Yes| ReturnPrimary[Return Primary Results]
    CheckCount -->|No| RelaxedSearch[Run Relaxed Search]
    
    RelaxedSearch --> RelaxedGeo[Expand Geographic Scope]
    RelaxedGeo --> RelaxedDate[Expand Date Range +/- 2 months]
    RelaxedDate --> RelaxedDiff[Expand Difficulty +/- 2]
    RelaxedDiff --> RelaxedBudget[Expand Budget to 50% over]
    RelaxedBudget --> RelaxedType[Remove Type Filter]
    RelaxedType --> RelaxedScore[Score with -20 Penalty]
    RelaxedScore --> FillTop10[Fill to 10 Total]
    
    FillTop10 --> ReturnBoth[Return Primary + Relaxed]
    
    ReturnPrimary --> Response[JSON Response]
    ReturnBoth --> Response
    Response --> End([Return to User])
```

### Scoring Subflow

```mermaid
flowchart TD
    Start([Begin Scoring]) --> Init[Score = BASE_SCORE<br/>25 points]
    
    Init --> ThemeCheck{User Selected<br/>Themes?}
    ThemeCheck -->|No| SkipTheme[Skip Theme Scoring]
    ThemeCheck -->|Yes| CountMatches[Count Matching Themes]
    
    CountMatches --> ThemeDecision{How Many<br/>Matches?}
    ThemeDecision -->|2+| ThemeFull[+25: Excellent Match]
    ThemeDecision -->|1| ThemePartial[+12: Good Match]
    ThemeDecision -->|0| ThemePenalty[-15: No Match Penalty]
    
    ThemeFull --> DiffCheck
    ThemePartial --> DiffCheck
    ThemePenalty --> DiffCheck
    SkipTheme --> DiffCheck
    
    DiffCheck{User Selected<br/>Difficulty?}
    DiffCheck -->|No| SkipDiff[Skip Difficulty Scoring]
    DiffCheck -->|Yes| DiffCompare{Trip Difficulty<br/>== User Pref?}
    
    DiffCompare -->|Yes| DiffPerfect[+15: Perfect Match]
    DiffCompare -->|No| SkipDiff
    
    DiffPerfect --> DurationCheck
    SkipDiff --> DurationCheck
    
    DurationCheck{Duration<br/>Specified?}
    DurationCheck -->|No| SkipDuration[Skip Duration Scoring]
    DurationCheck -->|Yes| CalcDuration[Calculate Trip Duration]
    
    CalcDuration --> DurationDecision{Within<br/>Range?}
    DurationDecision -->|Exact| DurationIdeal[+12: Ideal Duration]
    DurationDecision -->|Within 4 days| DurationGood[+8: Good Duration]
    DurationDecision -->|Within 7 days| DurationOK[+0: Acceptable]
    DurationDecision -->|Outside 7 days| DurationFail[Skip Trip]
    
    DurationIdeal --> BudgetCheck
    DurationGood --> BudgetCheck
    DurationOK --> BudgetCheck
    SkipDuration --> BudgetCheck
    DurationFail --> End
    
    BudgetCheck{Budget<br/>Specified?}
    BudgetCheck -->|No| SkipBudget[Skip Budget Scoring]
    BudgetCheck -->|Yes| BudgetCompare{Price vs<br/>Budget?}
    
    BudgetCompare -->|<= Budget| BudgetPerfect[+12: Within Budget]
    BudgetCompare -->|<= 110%| BudgetGood[+8: Slightly Over]
    BudgetCompare -->|<= 120%| BudgetAccept[+5: Acceptable]
    BudgetCompare -->|> 120%| SkipBudget
    
    BudgetPerfect --> StatusCheck
    BudgetGood --> StatusCheck
    BudgetAccept --> StatusCheck
    SkipBudget --> StatusCheck
    
    StatusCheck{Trip<br/>Status?}
    StatusCheck -->|Guaranteed| StatusGuaranteed[+7: Guaranteed Bonus]
    StatusCheck -->|Last Places| StatusUrgent[+15: Urgency Bonus]
    StatusCheck -->|Open| SkipStatus[No Status Bonus]
    
    StatusGuaranteed --> DepartCheck
    StatusUrgent --> DepartCheck
    SkipStatus --> DepartCheck
    
    DepartCheck{Departs<br/>Within 30d?}
    DepartCheck -->|Yes| DepartSoon[+7: Departing Soon]
    DepartCheck -->|No| SkipDepart[No Departure Bonus]
    
    DepartSoon --> GeoCheck
    SkipDepart --> GeoCheck
    
    GeoCheck{Geographic<br/>Match?}
    GeoCheck -->|Direct Country| GeoDirect[+15: Country Match]
    GeoCheck -->|Continent| GeoContinent[+5: Continent Match]
    GeoCheck -->|None| SkipGeo[No Geography Bonus]
    
    GeoDirect --> Finalize
    GeoContinent --> Finalize
    SkipGeo --> Finalize
    
    Finalize[Clamp Score: MAX 0, MIN 100] --> End([Return Final Score])
```

---

<div style="page-break-after: always;"></div>

## Scoring System

### Scoring Weights Configuration

The scoring system uses a weighted point accumulation model with a maximum score of 100 (clamped).

```
┌──────────────────────────────────────────────────────────────┐
│                    SCORING WEIGHTS TABLE                      │
├────────────────────────────┬────────┬──────────────────────────┤
│ Category                   │ Points │ Condition                │
├────────────────────────────┼────────┼──────────────────────────┤
│ BASE SCORE                 │  +25   │ All trips passing filters│
│ RELAXED PENALTY            │  -20   │ Relaxed search results   │
├────────────────────────────┼────────┼──────────────────────────┤
│ THEME SCORING:                                                 │
│   Theme Full Match         │  +25   │ 2+ matching themes       │
│   Theme Partial Match      │  +12   │ 1 matching theme         │
│   Theme Penalty            │  -15   │ No matching themes       │
├────────────────────────────┼────────┼──────────────────────────┤
│ DIFFICULTY SCORING:                                            │
│   Perfect Match            │  +15   │ Exact difficulty level   │
│   Close Match              │   +0   │ Within tolerance (no pts)│
├────────────────────────────┼────────┼──────────────────────────┤
│ DURATION SCORING:                                              │
│   Ideal Duration           │  +12   │ Within specified range   │
│   Good Duration            │   +8   │ Within 4 days of range   │
│   Acceptable Duration      │   +0   │ Within 7 days (no bonus) │
├────────────────────────────┼────────┼──────────────────────────┤
│ BUDGET SCORING:                                                │
│   Perfect Budget           │  +12   │ Within budget            │
│   Good Budget              │   +8   │ Within 110% of budget    │
│   Acceptable Budget        │   +5   │ Within 120% of budget    │
├────────────────────────────┼────────┼──────────────────────────┤
│ STATUS/URGENCY SCORING:                                        │
│   Status: Guaranteed       │   +7   │ Confirmed departure      │
│   Status: Last Places      │  +15   │ Limited availability     │
│   Departing Soon           │   +7   │ Within 30 days           │
├────────────────────────────┼────────┼──────────────────────────┤
│ GEOGRAPHY SCORING:                                             │
│   Direct Country Match     │  +15   │ Selected country         │
│   Continent Match          │   +5   │ Selected continent       │
└────────────────────────────┴────────┴──────────────────────────┘
```

### Score Thresholds (Color Coding)

```
┌─────────────────────────────────────────────────────────┐
│              SCORE THRESHOLD VISUALIZATION               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  100 ████████████████████████████████████████████████   │
│   90 ██████████████████████████████████████████████     │
│   80 ████████████████████████████████████████           │
│   70 ██████████████████████████████████ ◄─── TURQUOISE │
│   60 ████████████████████████████                       │
│   50 ██████████████████████ ◄────────────── ORANGE     │
│   40 ████████████████                                   │
│   30 ██████████                                         │
│   20 ████                                               │
│   10 ██                                                 │
│    0 ◄─────────────────────────────────────── RED      │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  TURQUOISE (70-100): Excellent Match                    │
│  ORANGE (50-69):     Medium Match                       │
│  RED (0-49):         Low Match                          │
└─────────────────────────────────────────────────────────┘
```

### Maximum Theoretical Score

```python
BASE_SCORE:          25
THEME_FULL:         +25
DIFFICULTY_PERFECT: +15
DURATION_IDEAL:     +12
BUDGET_PERFECT:     +12
STATUS_LAST_PLACES: +15
DEPARTING_SOON:     +7
GEO_DIRECT_COUNTRY: +15
─────────────────────────
THEORETICAL MAX:    126
ACTUAL MAX:         100 (clamped in code)
```

**Note:** The code applies clamping to keep scores within 0-100:
```python
final_score = max(0.0, min(100.0, current_score))
```

---

<div style="page-break-after: always;"></div>

## Scoring Decision Tree

### Visual Decision Tree for Scoring

```mermaid
graph TD
    Start([Trip Candidate]) --> Base[Base Score: 25]
    
    Base --> Q1{User Selected<br/>Themes?}
    Q1 -->|No| D1[Skip Theme Scoring]
    Q1 -->|Yes| Q2{Trip Has<br/>Matching Themes?}
    
    Q2 -->|2+ Matches| T1[+25 Points<br/>Excellent Theme Match]
    Q2 -->|1 Match| T2[+12 Points<br/>Good Theme Match]
    Q2 -->|0 Matches| T3[-15 Points<br/>Theme Penalty]
    
    D1 --> Q3
    T1 --> Q3
    T2 --> Q3
    T3 --> Q3
    
    Q3{User Selected<br/>Difficulty?}
    Q3 -->|No| D2[Skip Difficulty]
    Q3 -->|Yes| Q4{Exact<br/>Match?}
    
    Q4 -->|Yes| T4[+15 Points<br/>Perfect Difficulty]
    Q4 -->|No| D2
    
    D2 --> Q5
    T4 --> Q5
    
    Q5{Duration<br/>Specified?}
    Q5 -->|No| D3[Skip Duration]
    Q5 -->|Yes| Q6{Trip Duration<br/>vs Range?}
    
    Q6 -->|Within Range| T5[+12 Points<br/>Ideal Duration]
    Q6 -->|Within 4 Days| T6[+8 Points<br/>Good Duration]
    Q6 -->|Within 7 Days| T7[+0 Points<br/>Acceptable]
    Q6 -->|> 7 Days Off| SKIP[Skip Trip Entirely]
    
    D3 --> Q7
    T5 --> Q7
    T6 --> Q7
    T7 --> Q7
    
    Q7{Budget<br/>Specified?}
    Q7 -->|No| D4[Skip Budget]
    Q7 -->|Yes| Q8{Price vs<br/>Budget?}
    
    Q8 -->|<= Budget| T8[+12 Points<br/>Perfect Budget]
    Q8 -->|<= 110%| T9[+8 Points<br/>Good Budget]
    Q8 -->|<= 120%| T10[+5 Points<br/>Acceptable]
    Q8 -->|> 120%| D4
    
    D4 --> Q9
    T8 --> Q9
    T9 --> Q9
    T10 --> Q9
    
    Q9{Trip<br/>Status?}
    Q9 -->|Guaranteed| T11[+7 Points<br/>Guaranteed]
    Q9 -->|Last Places| T12[+15 Points<br/>Last Places]
    Q9 -->|Open| D5[No Status Bonus]
    
    T11 --> Q10
    T12 --> Q10
    D5 --> Q10
    
    Q10{Departs<br/>Within 30 Days?}
    Q10 -->|Yes| T13[+7 Points<br/>Departing Soon]
    Q10 -->|No| D6[No Departure Bonus]
    
    T13 --> Q11
    D6 --> Q11
    
    Q11{Geography<br/>Match?}
    Q11 -->|Direct Country| T14[+15 Points<br/>Country Match]
    Q11 -->|Continent| T15[+5 Points<br/>Continent Match]
    Q11 -->|No Match| D7[No Geography Bonus]
    
    T14 --> Final
    T15 --> Final
    D7 --> Final
    
    Final[Clamp Score<br/>MIN: 0, MAX: 100]
    Final --> Result([Final Score])
    
    SKIP --> Discard([Trip Discarded])
    
    style Base fill:#e1f5fe
    style T1 fill:#a5d6a7
    style T2 fill:#a5d6a7
    style T3 fill:#ef9a9a
    style T4 fill:#a5d6a7
    style T5 fill:#a5d6a7
    style T6 fill:#a5d6a7
    style T7 fill:#fff59d
    style T8 fill:#a5d6a7
    style T9 fill:#a5d6a7
    style T10 fill:#a5d6a7
    style T11 fill:#a5d6a7
    style T12 fill:#a5d6a7
    style T13 fill:#a5d6a7
    style T14 fill:#a5d6a7
    style T15 fill:#a5d6a7
    style SKIP fill:#ef9a9a
    style Discard fill:#ef9a9a
    style Final fill:#e1f5fe
    style Result fill:#4caf50
```

### Scoring Example Walkthrough

**Scenario: Perfect Match**

```
User Preferences:
- Location: Japan
- Themes: Wildlife + Photography
- Duration: 10-14 days
- Budget: $12,000
- Difficulty: Moderate (2)

Trip Details:
- Location: Japan
- Themes: Wildlife + Photography + Nature
- Duration: 12 days
- Price: $11,500
- Difficulty: Moderate (2)
- Status: Last Places
- Departs: In 20 days

Score Calculation:
┌────────────────────────────────────┬────────┐
│ Component                          │ Points │
├────────────────────────────────────┼────────┤
│ Base Score                         │  +25   │
│ Theme Full (2+ matches)            │  +25   │
│ Difficulty Perfect (2 = 2)         │  +15   │
│ Duration Ideal (12 in 10-14)       │  +12   │
│ Budget Perfect ($11.5k <= $12k)    │  +12   │
│ Status Last Places                 │  +15   │
│ Departing Soon (<30 days)          │  +7    │
│ Geography Direct (Japan = Japan)   │  +15   │
├────────────────────────────────────┼────────┤
│ TOTAL                              │  126   │
│ CLAMPED                            │  100   │
└────────────────────────────────────┴────────┘

Result: TURQUOISE (100) - Perfect Match
```

---

<div style="page-break-after: always;"></div>

## Filtering Logic

### Primary Tier (Strict Filters)

The primary tier applies narrow filters to ensure high-precision results.

```mermaid
graph LR
    Input[User Input] --> F1{Geographic<br/>Filter}
    F1 -->|Applied| F2{Trip Type<br/>Filter}
    F1 -->|Skipped| F2
    
    F2 -->|Applied| F3{Date Range<br/>Filter}
    F2 -->|Skipped| F3
    
    F3 -->|Applied| F4{Status<br/>Filter}
    F3 -->|Skipped| F4
    
    F4 --> F5{Difficulty<br/>Filter}
    F5 -->|Applied| F6{Budget<br/>Filter}
    F5 -->|Skipped| F6
    
    F6 -->|Applied| Result[Candidate<br/>Trips]
    F6 -->|Skipped| Result
    
    style F1 fill:#bbdefb
    style F2 fill:#bbdefb
    style F3 fill:#bbdefb
    style F4 fill:#bbdefb
    style F5 fill:#bbdefb
    style F6 fill:#bbdefb
    style Result fill:#c8e6c9
```

#### Filter Specifications

| Filter | Logic | Tolerance |
|--------|-------|-----------|
| **Geography** | Countries OR Continents (UNION) | Exact match required |
| **Trip Type** | Exact match | No tolerance (hard filter) |
| **Date** | Year AND/OR Month | Exact match required |
| **Status** | Available spots only | Excludes: Cancelled, Full |
| **Difficulty** | Within range | +/- 1 level |
| **Budget** | Max price ceiling | Up to 30% over budget |
| **Duration** | Checked during scoring | Within 7 days (hard limit) |

### Relaxed Tier (Expanded Filters)

Triggers when primary results < 6 trips.

```mermaid
graph TD
    Primary[Primary Search] --> Check{Results < 6?}
    Check -->|No| Return[Return Primary<br/>Results]
    Check -->|Yes| Relaxed[Trigger Relaxed<br/>Search]
    
    Relaxed --> R1[Expand Geography<br/>to Continent]
    R1 --> R2[Extend Date Range<br/>+/- 2 Months]
    R2 --> R3[Widen Difficulty<br/>+/- 2 Levels]
    R3 --> R4[Increase Budget<br/>to 50% Over]
    R4 --> R5[Remove Trip Type<br/>Filter]
    R5 --> R6[Apply -20 Base<br/>Penalty]
    R6 --> R7[Score & Sort<br/>Candidates]
    R7 --> R8[Fill to 10<br/>Total Results]
    R8 --> Return2[Return Primary<br/>+ Relaxed]
    
    style Check fill:#fff59d
    style Relaxed fill:#ffcc80
    style R1 fill:#ffcc80
    style R2 fill:#ffcc80
    style R3 fill:#ffcc80
    style R4 fill:#ffcc80
    style R5 fill:#ffcc80
    style R6 fill:#ef9a9a
    style R7 fill:#ffcc80
    style R8 fill:#ffcc80
    style Return fill:#c8e6c9
    style Return2 fill:#c8e6c9
```

#### Relaxed Tier Modifications

| Criterion | Primary Tier | Relaxed Tier | Change |
|-----------|--------------|--------------|--------|
| **Geography** | Selected countries | Entire continents | Expanded |
| **Date Range** | Exact year/month | +/- 2 months | Expanded |
| **Difficulty** | +/- 1 level | +/- 2 levels | Expanded |
| **Budget** | Up to 30% over | Up to 50% over | Expanded |
| **Trip Type** | Exact match | All types | Removed |
| **Base Score** | 25 points | 5 points (25 - 20) | Penalized |
| **Type Mismatch** | N/A | Additional -10 | Penalized |

### Filter Comparison Table

```
┌───────────────┬──────────────────────┬──────────────────────┐
│   Criterion   │   Primary Tier       │   Relaxed Tier       │
├───────────────┼──────────────────────┼──────────────────────┤
│ Geography     │ Exact countries      │ Full continent       │
│               │ Continent match      │ (expand 1 level)     │
├───────────────┼──────────────────────┼──────────────────────┤
│ Date Range    │ Year/Month exact     │ +/- 2 months         │
│               │ (e.g., March 2026)   │ (Jan-May 2026)       │
├───────────────┼──────────────────────┼──────────────────────┤
│ Difficulty    │ User pref +/- 1      │ User pref +/- 2      │
│               │ (e.g., 2: 1-3)       │ (e.g., 2: 0-4)       │
├───────────────┼──────────────────────┼──────────────────────┤
│ Budget        │ Up to 130% of budget │ Up to 150% of budget │
│               │ ($10k -> $13k)       │ ($10k -> $15k)       │
├───────────────┼──────────────────────┼──────────────────────┤
│ Trip Type     │ Exact match required │ All types allowed    │
│               │ (Safari only)        │ (Safari, Hiking...)  │
├───────────────┼──────────────────────┼──────────────────────┤
│ Base Score    │ 25 points            │ 5 points (25-20)     │
├───────────────┼──────────────────────┼──────────────────────┤
│ Penalty       │ None                 │ -10 for type mismatch│
└───────────────┴──────────────────────┴──────────────────────┘
```

---

<div style="page-break-after: always;"></div>

## Part IV: Implementation

---

## API Flow

### Request/Response Architecture

```mermaid
sequenceDiagram
    participant C as Client (Frontend)
    participant A as API Endpoint
    participant V as Validator
    participant E as Engine
    participant S as Scorer
    participant D as Database
    
    C->>A: POST /api/recommendations<br/>{preferences}
    A->>V: Validate input
    
    alt Validation fails
        V-->>A: ValidationError
        A-->>C: 400 Bad Request
    else Validation succeeds
        V->>E: Sanitized preferences
        E->>D: Query with hard filters
        D-->>E: Candidate trips
        
        loop For each candidate
            E->>S: Score trip
            S-->>E: Score + details
        end
        
        E->>E: Sort by score, date
        E->>E: Select top 10
        
        alt Results < 6
            E->>D: Relaxed query
            D-->>E: Additional candidates
            E->>S: Score with penalty
            S-->>E: Relaxed scores
            E->>E: Fill to 10 total
        end
        
        E-->>A: Scored results
        A-->>C: 200 OK<br/>{success, data, scores}
    end
```

### API Request Format

```http
POST /api/recommendations HTTP/1.1
Host: api.smarttrip.com
Content-Type: application/json
Accept: application/json

{
  "selected_countries": [12, 15, 20],
  "selected_continents": ["Asia", "Europe"],
  "preferred_type_id": 5,
  "preferred_theme_ids": [10, 12, 18],
  "min_duration": 7,
  "max_duration": 14,
  "budget": 10000,
  "difficulty": 2,
  "year": "2026",
  "month": "3"
}
```

**All parameters are optional.**

### API Response Format

```json
{
  "success": true,
  "count": 10,
  "primary_count": 7,
  "relaxed_count": 3,
  "total_candidates": 45,
  "total_trips": 587,
  "has_relaxed_results": true,
  "score_thresholds": {
    "HIGH": 70,
    "MID": 50
  },
  "show_refinement_message": false,
  "message": "Found 7 recommended trips + 3 expanded results",
  "data": [
    {
      "id": 123,
      "title": "Japan Cherry Blossom Tour",
      "titleHe": "טיול פריחת הדובדבן ביפן",
      "startDate": "2026-03-15",
      "endDate": "2026-03-25",
      "price": 12500,
      "status": "Guaranteed",
      "difficultyLevel": 2,
      "spotsLeft": 8,
      "maxCapacity": 15,
      
      "country": {
        "id": 45,
        "name": "Japan",
        "nameHe": "יפן",
        "continent": "Asia"
      },
      
      "guide": {
        "id": 10,
        "name": "Sarah Cohen"
      },
      
      "type": {
        "id": 3,
        "name": "Cultural Discovery"
      },
      
      "tags": [
        {"id": 12, "name": "Cultural"},
        {"id": 15, "name": "Photography"}
      ],
      
      "match_score": 88,
      "is_relaxed": false,
      "match_details": [
        "Excellent Theme Match (2 interests) [+25]",
        "Perfect Difficulty [+15]",
        "Ideal Duration (10d) [+12]",
        "Within Budget [+12]",
        "Guaranteed [+7]",
        "Country Match [+15]"
      ]
    }
  ]
}
```

### Input Validation Diagram

```mermaid
graph TD
    Input[Raw Input] --> V1{Type Check}
    V1 -->|Invalid| E1[Return Error]
    V1 -->|Valid| V2{Range Check}
    
    V2 -->|Out of bounds| E2[Use Default/<br/>Reject]
    V2 -->|Valid| V3{SQL Injection<br/>Check}
    
    V3 -->|Detected| E3[Sanitize/<br/>Reject]
    V3 -->|Clean| V4{XSS Check}
    
    V4 -->|Detected| E4[Remove Tags]
    V4 -->|Clean| V5{Length Check}
    
    V5 -->|Too long| E5[Truncate/<br/>Reject]
    V5 -->|Valid| Safe[Safe Input]
    
    E1 --> Fail[Validation Failed]
    E2 --> Safe
    E3 --> Fail
    E4 --> Safe
    E5 --> Safe
    
    Safe --> Process[Process Request]
    
    style V1 fill:#fff59d
    style V2 fill:#fff59d
    style V3 fill:#fff59d
    style V4 fill:#fff59d
    style V5 fill:#fff59d
    style Safe fill:#c8e6c9
    style Process fill:#c8e6c9
    style Fail fill:#ef9a9a
```

---

<div style="page-break-after: always;"></div>

## Technical Implementation

### Database Query Optimization

#### Problem: N+1 Query Issue

Without optimization, fetching trips with relationships causes N+1 queries:

```python
# Bad: N+1 queries
trips = query.all()  # 1 query
for trip in trips:
    country = trip.country  # N queries!
    guide = trip.guide      # N queries!
    tags = trip.trip_tags   # N queries!

# Total queries for 200 trips: 1 + (200 * 3) = 601 queries
```

#### Solution: Eager Loading

```python
# Good: 3-4 queries total
query = db_session.query(Trip).options(
    joinedload(Trip.country),           # Load in single query
    joinedload(Trip.guide),             # Load in single query
    selectinload(Trip.trip_tags).joinedload(TripTag.tag)  # Load efficiently
)

# Total queries: 3-4 regardless of result size
```

### Performance Impact

```
┌────────────────────────┬──────────────┬─────────────┐
│ Optimization           │ Before       │ After       │
├────────────────────────┼──────────────┼─────────────┤
│ Queries per request    │ 601          │ 3-4         │
│ Response time (avg)    │ ~8-10s       │ ~2s         │
│ Database load          │ High         │ Low         │
│ Scalability            │ Poor         │ Good        │
└────────────────────────┴──────────────┴─────────────┘
```

### Security Implementation

```mermaid
graph TD
    Input[User Input] --> S1[Type Validation]
    S1 --> S2[Range Validation]
    S2 --> S3[SQL Injection Prevention]
    S3 --> S4[XSS Protection]
    S4 --> S5[Length Limits]
    S5 --> S6[Whitelist Validation]
    S6 --> Safe[Safe for Processing]
    
    S1 -.->|Integer check| I1[safe_int]
    S1 -.->|Float check| I2[safe_float]
    S1 -.->|Array check| I3[safe_int_list]
    
    S3 -.->|Remove chars| P1["Remove ; ' \" \\"]
    S4 -.->|Remove tags| P2[Remove HTML tags]
    S5 -.->|Truncate| P3[Max 100 chars]
    S6 -.->|Check list| P4[Allowed continents]
    
    style Input fill:#ffcdd2
    style Safe fill:#c8e6c9
    style S1 fill:#fff59d
    style S2 fill:#fff59d
    style S3 fill:#fff59d
    style S4 fill:#fff59d
    style S5 fill:#fff59d
    style S6 fill:#fff59d
```

#### Security Functions

```python
def safe_int(value, default=None, min_val=None, max_val=None):
    """
    Safely convert to int with bounds checking
    
    Examples:
      safe_int("5", min_val=1, max_val=10)     -> 5
      safe_int("15", min_val=1, max_val=10)    -> None
      safe_int("abc", default=0)               -> 0
    """
    if value is None:
        return default
    try:
        result = int(float(value))
        if min_val is not None and result < min_val:
            return default
        if max_val is not None and result > max_val:
            return default
        return result
    except (TypeError, ValueError):
        return default

def sanitize_string(value):
    """
    Remove potentially dangerous characters
    
    Examples:
      sanitize_string("<script>alert('xss')</script>")  -> "alertxss"
      sanitize_string("DROP TABLE; --")                 -> "DROP TABLE --"
      sanitize_string("A" * 200)                        -> "A" * 100
    """
    if value is None or not isinstance(value, str):
        return None
    
    # Remove HTML tags
    value = re.sub(r'<[^>]*>', '', value)
    
    # Remove SQL injection characters
    value = re.sub(r'[;\'"\\]', '', value)
    
    # Limit string length
    if len(value) > 100:
        value = value[:100]
    
    return value.strip()
```

### Special Case: Private Groups

```mermaid
graph TD
    Start[Trip Detected] --> Check{Trip Type =<br/>Private Groups?}
    
    Check -->|No| RegularDate[Apply Date Filter:<br/>start_date >= today]
    Check -->|Yes| SkipDate[Skip Date Filter]
    
    RegularDate --> RegularSpots[Filter: spots_left > 0]
    SkipDate --> PrivateSpots[Allow: spots = 0]
    
    RegularSpots --> RegularScore[Normal Scoring]
    PrivateSpots --> PrivateScore[Give Full Duration Points:<br/>+12 automatically]
    
    RegularScore --> Result[Candidate Trip]
    PrivateScore --> Result
    
    style Check fill:#fff59d
    style SkipDate fill:#ffcc80
    style PrivateSpots fill:#ffcc80
    style PrivateScore fill:#ffcc80
```

---

<div style="page-break-after: always;"></div>

## Performance Optimizations

### Current Optimizations

```
┌──────────────────────────────────────────────────────────┐
│              OPTIMIZATION SUMMARY                         │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  1. EAGER LOADING                                        │
│     - Eliminates N+1 queries                             │
│     - Reduces queries from 600+ to 3-4                   │
│                                                           │
│  2. DATABASE INDEXES                                     │
│     - All filtered columns indexed                       │
│     - Composite index on date range                      │
│     - O(log n) query performance                         │
│                                                           │
│  3. RESULT LIMITING                                      │
│     - Max 10 results returned                            │
│     - Reduces data transfer                              │
│     - Improves response time                             │
│                                                           │
│  4. SHORT-CIRCUIT EVALUATION                             │
│     - Trips failing hard filters skipped early           │
│     - No scoring for excluded trips                      │
│     - Reduces CPU usage                                  │
│                                                           │
│  5. FLOAT PRECISION SORTING                              │
│     - Avoids tie-breaking overhead                       │
│     - Deterministic ordering                             │
│     - Consistent results                                 │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Performance Metrics

```
Current Performance:
┌─────────────────────────┬─────────────┐
│ Metric                  │ Value       │
├─────────────────────────┼─────────────┤
│ Average Response Time   │ ~2 seconds  │
│ Database Queries        │ 3-4         │
│ Bottleneck              │ DB Connect  │
│ Memory Usage            │ Low         │
│ CPU Usage               │ Moderate    │
└─────────────────────────┴─────────────┘
```

### Future Optimization Opportunities

```mermaid
graph TD
    Current[Current State<br/>~2s response] --> Opt1[Connection Pooling]
    Current --> Opt2[Redis Caching]
    Current --> Opt3[Materialized Views]
    Current --> Opt4[Query Result Cache]
    
    Opt1 --> I1[SQLAlchemy Pool<br/>Size: 10-20]
    Opt2 --> I2[Cache static data<br/>TTL: 1 hour]
    Opt3 --> I3[Pre-computed views<br/>Refresh: Daily]
    Opt4 --> I4[Cache frequent searches<br/>Hit rate: 60-70%]
    
    I1 --> Future[Future State<br/>~200-500ms response]
    I2 --> Future
    I3 --> Future
    I4 --> Future
    
    style Current fill:#ffcdd2
    style Future fill:#c8e6c9
    style Opt1 fill:#fff59d
    style Opt2 fill:#fff59d
    style Opt3 fill:#fff59d
    style Opt4 fill:#fff59d
```

#### Optimization Proposals

**1. Connection Pooling**
```python
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

**Expected Impact:** -500ms to -1s response time

**2. Redis Caching**
```python
@cache.cached(timeout=3600, key_prefix='countries')
def get_all_countries():
    return db_session.query(Country).all()

@cache.cached(timeout=3600, key_prefix='tags')
def get_all_tags():
    return db_session.query(Tag).all()
```

**Expected Impact:** -200ms to -400ms for cached requests

**3. Materialized Views**
```sql
CREATE MATERIALIZED VIEW trip_search_view AS
SELECT
    t.*,
    c.name as country_name,
    c.continent,
    array_agg(tt.tag_id) as tag_ids
FROM trips t
JOIN countries c ON t.country_id = c.id
LEFT JOIN trip_tags tt ON t.id = tt.trip_id
GROUP BY t.id, c.name, c.continent;

CREATE INDEX ON trip_search_view(country_name);
CREATE INDEX ON trip_search_view(continent);
CREATE INDEX ON trip_search_view(start_date);

REFRESH MATERIALIZED VIEW trip_search_view;
```

**Expected Impact:** -300ms to -600ms query time

**4. Query Result Caching**
```python
def get_recommendations(preferences):
    cache_key = f"recs:{hash(json.dumps(preferences, sort_keys=True))}"
    cached = redis.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    results = run_recommendation_engine(preferences)
    redis.setex(cache_key, 300, json.dumps(results))  # 5 min TTL
    return results
```

**Expected Impact:** -1.5s to -2s for cache hits (60-70% of requests)

---

<div style="page-break-after: always;"></div>

## Part V: Testing & Configuration

---

## Test Results and Validation

### Test Coverage Summary

```
┌──────────────────────────────────────────────────────────┐
│                  TEST COVERAGE REPORT                     │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Total Tests:           255                              │
│  Passed:                253                              │
│  Failed:                2                                │
│  Pass Rate:             99.2%                            │
│                                                           │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  API Endpoint Tests:    40 tests                         │
│    - Health checks                                       │
│    - CRUD operations                                     │
│    - Error handling                                      │
│    - Authentication                                      │
│                                                           │
│  Search Scenario Tests: 215 tests                       │
│    - Recommendation algorithm                            │
│    - Scoring calculations                                │
│    - Filter combinations                                 │
│    - Edge cases                                          │
│    - Security validation                                 │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Test Categories

```mermaid
pie title Test Distribution
    "Search Scenarios" : 215
    "API Endpoints" : 40
```

### Validation Scenarios

#### Persona 1: Classic Africa Traveler

```
Input:
  - Continent: Africa
  - Trip Type: African Safari
  - Themes: Wildlife + Photography
  - Budget: $20,000
  - Duration: 10-14 days
  - Difficulty: Moderate (2)

Expected Results:
  ✓ High scores (70+) for Africa safari trips with wildlife themes
  ✓ Lower scores for Africa trips without wildlife/photography
  ✓ No trips from other continents
  ✓ Trips within 10-14 days prioritized
  ✓ Status bonuses (Guaranteed, Last Places) apply correctly

Actual Results: PASS
```

#### Persona 2: Young Backpacker

```
Input:
  - Continent: Asia
  - Trip Type: Nature Hiking
  - Themes: Mountain + Cultural
  - Budget: $8,000
  - Duration: 10-18 days
  - Difficulty: Hard (3)

Expected Results:
  ✓ Prioritizes lower-priced trips
  ✓ Favors difficulty level 3 (hard)
  ✓ Mountain/cultural themes score higher
  ✓ Asia continent trips only
  ✓ Budget filtering works correctly

Actual Results: PASS
```

#### Persona 3: Mismatch Tester

```
Input:
  - Continent: Antarctica
  - Trip Type: Desert (wrong for Antarctica!)
  - Themes: Desert theme
  - Budget: $5,000 (way too low for Antarctica)
  - Duration: 7-10 days
  - Difficulty: Easy (1) (Antarctica trips are usually hard)

Expected Results:
  ✓ Few or no primary results
  ✓ Low scores due to theme penalty and budget mismatch
  ✓ Relaxed search may find Antarctica trips with poor scores
  ✓ Algorithm handles impossible criteria gracefully

Actual Results: PASS (Demonstrates robustness)
```

### Score Distribution Analysis

From automated testing of 30 scenarios:

```
┌──────────────────────────────────────────────────────────┐
│           SCORE DISTRIBUTION (30 SCENARIOS)              │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  TURQUOISE (70-100):  10 scenarios (33%)                 │
│  ████████████████████████████████                        │
│                                                           │
│  ORANGE (50-69):      13 scenarios (43%)                 │
│  ██████████████████████████████████████████              │
│                                                           │
│  RED (0-49):          7 scenarios (23%)                  │
│  ███████████████████████                                 │
│                                                           │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Interpretation:                                         │
│  - 76% of realistic searches score 50+ (acceptable)      │
│  - 23% of searches yield weak matches (as expected)      │
│  - Base score prevents "zero score" issue                │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

<div style="page-break-after: always;"></div>

## Configuration Reference

### Environment Variables

```bash
# Backend (.env)
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/smarttrip
PORT=5000
HOST=0.0.0.0
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### Scoring Weights Configuration

```python
# app.py: SCORING_WEIGHTS
SCORING_WEIGHTS = {
    'BASE_SCORE': 25.0,
    'RELAXED_PENALTY': -20.0,
    
    'THEME_FULL': 25.0,
    'THEME_PARTIAL': 12.0,
    'THEME_PENALTY': -15.0,
    
    'DIFFICULTY_PERFECT': 15.0,
    
    'DURATION_IDEAL': 12.0,
    'DURATION_GOOD': 8.0,
    
    'BUDGET_PERFECT': 12.0,
    'BUDGET_GOOD': 8.0,
    'BUDGET_ACCEPTABLE': 5.0,
    
    'STATUS_GUARANTEED': 7.0,
    'STATUS_LAST_PLACES': 15.0,
    'DEPARTING_SOON': 7.0,
    
    'GEO_DIRECT_COUNTRY': 15.0,
    'GEO_CONTINENT': 5.0,
}

# app.py: SCORE_THRESHOLDS
SCORE_THRESHOLDS = {
    'HIGH': 70,  # Turquoise
    'MID': 50,   # Orange
}
```

### Algorithm Configuration

```python
# app.py: RecommendationConfig
class RecommendationConfig:
    # Primary tier filtering
    DIFFICULTY_TOLERANCE = 1
    BUDGET_MAX_MULTIPLIER = 1.3
    DURATION_GOOD_DAYS = 4
    DURATION_HARD_FILTER_DAYS = 7
    DEPARTING_SOON_DAYS = 30
    
    # Relaxed tier filtering
    RELAXED_DIFFICULTY_TOLERANCE = 2
    RELAXED_BUDGET_MULTIPLIER = 1.5
    RELAXED_DURATION_DAYS = 10
    
    # Result limits
    MAX_RESULTS = 10
    MIN_RESULTS_THRESHOLD = 6
    THEME_MATCH_THRESHOLD = 2
```

### Tuning Guide

#### To Increase High-Score Results

```python
# Option 1: Increase base score
'BASE_SCORE': 30.0,  # Was 25.0

# Option 2: Increase key bonuses
'GEO_DIRECT_COUNTRY': 20.0,  # Was 15.0
'THEME_FULL': 30.0,          # Was 25.0

# Option 3: Lower thresholds
SCORE_THRESHOLDS = {
    'HIGH': 65,  # Was 70
    'MID': 45,   # Was 50
}
```

#### To Make Scoring More Strict

```python
# Option 1: Lower base score
'BASE_SCORE': 20.0,  # Was 25.0

# Option 2: Increase penalties
'THEME_PENALTY': -20.0,  # Was -15.0

# Option 3: Raise thresholds
SCORE_THRESHOLDS = {
    'HIGH': 75,  # Was 70
    'MID': 55,   # Was 50
}
```

#### To Adjust Relaxed Search Trigger

```python
# More aggressive (more relaxed results)
MIN_RESULTS_THRESHOLD = 8  # Was 6

# Less aggressive (fewer relaxed results)
MIN_RESULTS_THRESHOLD = 4  # Was 6
```

---

<div style="page-break-after: always;"></div>

## Appendices

---

## Appendix A: Complete Scoring Matrix

| User Input | Trip Attributes | Points | Category |
|------------|----------------|--------|----------|
| Any valid search | Passes hard filters | +25 | BASE_SCORE |
| Relaxed search | Any trip | -20 | RELAXED_PENALTY |
| Selected country: Japan | Trip in Japan | +15 | GEO_DIRECT_COUNTRY |
| Selected continent: Asia | Trip in Asia | +5 | GEO_CONTINENT |
| Themes: Wildlife, Photography | Trip has Wildlife + Photography | +25 | THEME_FULL |
| Themes: Wildlife, Photography | Trip has only Wildlife | +12 | THEME_PARTIAL |
| Themes: Wildlife, Photography | Trip has Mountain, Desert | -15 | THEME_PENALTY |
| Difficulty: 2 (Moderate) | Trip difficulty: 2 | +15 | DIFFICULTY_PERFECT |
| Difficulty: 2 (Moderate) | Trip difficulty: 1 or 3 | +0 | Within tolerance |
| Duration: 10-14 days | Trip duration: 12 days | +12 | DURATION_IDEAL |
| Duration: 10-14 days | Trip duration: 8 or 16 days | +8 | DURATION_GOOD |
| Budget: $10,000 | Trip price: $9,500 | +12 | BUDGET_PERFECT |
| Budget: $10,000 | Trip price: $10,800 (108%) | +8 | BUDGET_GOOD |
| Budget: $10,000 | Trip price: $11,500 (115%) | +5 | BUDGET_ACCEPTABLE |
| Any | Trip status: Guaranteed | +7 | STATUS_GUARANTEED |
| Any | Trip status: Last Places | +15 | STATUS_LAST_PLACES |
| Any | Trip starts in 20 days | +7 | DEPARTING_SOON |
| Preferred type: Safari | Relaxed trip type: Hiking | -10 | Type mismatch |

---

## Appendix B: Algorithm Pseudocode

```python
FUNCTION get_recommendations(preferences):
    # STEP 1: Validate and sanitize inputs
    countries = safe_int_list(preferences.countries)
    continents = safe_string_list(preferences.continents, ALLOWED_CONTINENTS)
    type_id = safe_int(preferences.type_id, min=1, max=100)
    theme_ids = safe_int_list(preferences.theme_ids, max_length=3)
    min_duration = safe_int(preferences.min_duration, min=0, max=365)
    max_duration = safe_int(preferences.max_duration, min=0, max=365)
    budget = safe_float(preferences.budget, min=0)
    difficulty = safe_int(preferences.difficulty, min=1, max=5)
    year = safe_int(preferences.year, min=2020, max=2050)
    month = safe_int(preferences.month, min=1, max=12)
    
    # STEP 2: Build base query with eager loading
    query = SELECT Trip
        JOIN Country
        JOIN Guide
        JOIN TripTags
        WHERE Trip.start_date >= today
          AND Trip.status != CANCELLED
          AND Trip.spots_left > 0
    
    # STEP 3: Apply hard filters
    IF countries OR continents:
        query = query.WHERE (
            Trip.country_id IN countries
            OR Country.continent IN continents
        )
    
    IF type_id:
        query = query.WHERE Trip.trip_type_id = type_id
    
    IF year:
        query = query.WHERE YEAR(Trip.start_date) = year
        IF month:
            query = query.WHERE MONTH(Trip.start_date) = month
    
    IF difficulty:
        query = query.WHERE Trip.difficulty_level BETWEEN (difficulty - 1) AND (difficulty + 1)
    
    IF budget:
        query = query.WHERE Trip.price <= (budget * 1.3)
    
    candidates = query.execute()
    
    # STEP 4: Score each candidate
    scored_trips = []
    FOR EACH trip IN candidates:
        score = BASE_SCORE (25)
        details = []
        
        # Theme scoring
        trip_themes = trip.get_theme_ids()
        matching_themes = theme_ids INTERSECT trip_themes
        IF len(matching_themes) >= 2:
            score += THEME_FULL (25)
            details.append("Excellent Theme Match")
        ELSE IF len(matching_themes) == 1:
            score += THEME_PARTIAL (12)
            details.append("Good Theme Match")
        ELSE IF theme_ids AND len(matching_themes) == 0:
            score += THEME_PENALTY (-15)
            details.append("No Theme Match")
        
        # Difficulty scoring
        IF trip.difficulty == difficulty:
            score += DIFFICULTY_PERFECT (15)
            details.append("Perfect Difficulty")
        
        # Duration scoring
        trip_duration = trip.end_date - trip.start_date
        IF trip_duration BETWEEN min_duration AND max_duration:
            score += DURATION_IDEAL (12)
            details.append("Ideal Duration")
        ELSE IF abs(trip_duration - min_duration) <= 4 OR abs(trip_duration - max_duration) <= 4:
            score += DURATION_GOOD (8)
            details.append("Good Duration")
        ELSE IF abs(trip_duration - min_duration) > 7 AND abs(trip_duration - max_duration) > 7:
            CONTINUE  // Skip trip
        
        # Budget scoring
        IF trip.price <= budget:
            score += BUDGET_PERFECT (12)
            details.append("Within Budget")
        ELSE IF trip.price <= budget * 1.1:
            score += BUDGET_GOOD (8)
            details.append("Slightly Over Budget")
        ELSE IF trip.price <= budget * 1.2:
            score += BUDGET_ACCEPTABLE (5)
            details.append("Acceptable Budget")
        
        # Status scoring
        IF trip.status == GUARANTEED:
            score += STATUS_GUARANTEED (7)
            details.append("Guaranteed")
        ELSE IF trip.status == LAST_PLACES:
            score += STATUS_LAST_PLACES (15)
            details.append("Last Places")
        
        # Departing soon
        days_until = trip.start_date - today
        IF days_until <= 30:
            score += DEPARTING_SOON (7)
            details.append("Departing Soon")
        
        # Geography scoring
        IF trip.country_id IN countries:
            score += GEO_DIRECT_COUNTRY (15)
            details.append("Country Match")
        ELSE IF trip.country.continent IN continents:
            score += GEO_CONTINENT (5)
            details.append("Continent Match")
        
        # Clamp score
        final_score = CLAMP(score, 0, 100)
        
        scored_trips.append({
            trip: trip,
            score: final_score,
            details: details
        })
    
    # STEP 5: Sort by score (desc) then date (asc)
    scored_trips.SORT BY (score DESC, start_date ASC)
    top_results = scored_trips[0:10]
    
    # STEP 6: Relaxed search if needed
    IF len(top_results) < 6:
        relaxed_trips = run_relaxed_search(preferences, exclude=top_results.ids)
        top_results = top_results + relaxed_trips[0:(10 - len(top_results))]
    
    # STEP 7: Return results
    RETURN {
        success: true,
        count: len(top_results),
        data: top_results,
        score_thresholds: {HIGH: 70, MID: 50}
    }
```

---

## Appendix C: Glossary

**Base Score**: Starting score awarded to all trips that pass hard filters (25 points)

**Hard Filter**: Strict constraint that excludes trips (e.g., trip type, date range)

**Soft Filter**: Preference that influences scoring but doesn't exclude (e.g., themes)

**Primary Tier**: Initial strict search with narrow filters

**Relaxed Tier**: Expanded search with looser filters, triggered when primary results < 6

**Match Score**: Final 0-100 score indicating trip relevance

**Theme Match**: Overlap between user-selected theme interests and trip themes

**Theme Penalty**: Negative score when trip has none of user's selected themes

**Urgency Bonus**: Additional points for trips with limited availability or soon departure

**Geography Bonus**: Points for trips matching user's location preferences

**Eager Loading**: Database optimization technique to load relationships in advance

**Score Clamping**: Constraining score to 0-100 range

**N+1 Query Problem**: Performance issue where separate queries are made for each relationship

**ORM**: Object-Relational Mapping (SQLAlchemy)

**RTL**: Right-to-Left (for Hebrew language support)

**CORS**: Cross-Origin Resource Sharing

**XSS**: Cross-Site Scripting (security vulnerability)

**SQL Injection**: Security vulnerability where malicious SQL is injected into queries

**Materialized View**: Pre-computed database view for performance

**Connection Pool**: Reusable database connections to reduce overhead

---

<div style="page-break-after: always;"></div>

## Conclusion

The SmartTrip Recommendation Engine is a production-ready system that balances precision and recall through a two-tier approach. With comprehensive validation, security features, and performance optimizations, it provides users with relevant trip recommendations while handling edge cases gracefully.

The scoring system is transparent and tunable, allowing for easy adjustments based on business priorities and user feedback. The algorithm has been extensively tested and validated across 255 test scenarios with a 99.2% pass rate.

### Key Takeaways

1. **Two-Tier System**: Primary (strict) + Relaxed (flexible) ensures users always see results
2. **Weighted Scoring**: 6 major criteria with configurable weights (0-100 point scale)
3. **Performance Optimized**: Eager loading, indexes, and caching reduce response time
4. **Security Focused**: Input validation, XSS protection, SQL injection prevention
5. **Highly Testable**: 99.2% pass rate across 255 automated tests
6. **Easily Tunable**: All weights and thresholds configurable via constants

### Future Enhancements

- Connection pooling for improved database performance
- Redis caching for static data and frequent searches
- Materialized views for complex queries
- Machine learning integration for personalized scoring
- A/B testing framework for algorithm tuning

---

**Document Version:** 1.0  
**Last Updated:** December 14, 2025  
**Maintained By:** SmartTrip Development Team  

**For questions or modifications, refer to the Configuration Reference section.**

---

END OF DOCUMENT
