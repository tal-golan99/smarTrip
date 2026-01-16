# Database Schema Changes - Version 2.0

## IMPLEMENTATION STATUS: COMPLETE

All migrations have been implemented and are ready to run.
See "How to Run Migrations" section at the end of this document.

---

## Overview

This document outlines the database schema changes to support:
1. **Companies Table** - Travel companies that organize trips
2. **Trip Templates vs Trip Occurrences** - Separating trip definitions from scheduled instances
3. **Flexible Guide Assignments** - Same trip can run multiple times with different guides
4. **Multi-Country Support** - Trips can visit multiple countries
5. **Price History** - Track price changes for analytics
6. **Reviews System** - User reviews linked to templates and occurrences
7. **Image Overrides** - Seasonal image variations per occurrence

---

## Current Schema Analysis

### Current Tables
| Table | Purpose |
|-------|---------|
| `countries` | Destination countries with continent info |
| `guides` | Tour guide information |
| `trip_types` | Trip style categories (Safari, Cruise, etc.) |
| `tags` | Theme tags (Wildlife, Culture, etc.) |
| `trips` | **Current: Combined trip definition + schedule** |
| `trip_tags` | Many-to-many junction for trips and tags |

### Current Issues
1. **No company tracking** - Can't identify which company organizes each trip
2. **Trip data duplication** - Same trip route repeated with different dates requires duplicating all trip data
3. **Tight coupling** - Guide is permanently tied to a specific trip instance
4. **Maintenance overhead** - Updating a trip's description requires updating multiple rows

---

## Proposed Schema Changes

### New Architecture

```
COMPANIES (1) --> (many) TRIP_TEMPLATES (1) --> (many) TRIP_OCCURRENCES
                              |                           |
                              |                           +--> GUIDES (flexible)
                              |
                              +--> COUNTRIES
                              +--> TRIP_TYPES
                              +--> TAGS (via junction)
```

---

## New Table: `companies`

### Purpose
Stores information about travel companies that organize trips.

### Schema

```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    name_he VARCHAR(255) NOT NULL,
    description TEXT,
    description_he TEXT,
    logo_url VARCHAR(500),
    website_url VARCHAR(500),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes
CREATE INDEX ix_companies_name ON companies(name);
CREATE INDEX ix_companies_is_active ON companies(is_active);
```

### SQLAlchemy Model

```python
class Company(Base):
    """Companies table - stores travel company information"""
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    name_he = Column(String(255), nullable=False)
    description = Column(Text)
    description_he = Column(Text)
    logo_url = Column(String(500))
    website_url = Column(String(500))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    trip_templates = relationship('TripTemplate', back_populates='company')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'nameHe': self.name_he,
            'description': self.description,
            'descriptionHe': self.description_he,
            'logoUrl': self.logo_url,
            'websiteUrl': self.website_url,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }
```

---

## Refactored Table: `trip_templates` (formerly `trips`)

### Purpose
Stores the **definition** of a trip (route, description, base info) without specific dates.

### Key Changes
- Renamed from `trips` to `trip_templates`
- Removed date-specific fields (start_date, end_date, status, spots_left)
- Added `company_id` foreign key
- Added `base_price` (typical price, can be overridden in occurrences)
- Added `typical_duration_days` (expected length)

### Schema

```sql
CREATE TABLE trip_templates (
    id SERIAL PRIMARY KEY,
    
    -- Basic Info
    title VARCHAR(255) NOT NULL,
    title_he VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    description_he TEXT NOT NULL,
    short_description VARCHAR(500),
    short_description_he VARCHAR(500),
    image_url VARCHAR(500),
    
    -- Pricing & Duration (base/typical values)
    base_price NUMERIC(10, 2) NOT NULL,
    single_supplement_price NUMERIC(10, 2),
    typical_duration_days INTEGER NOT NULL,
    
    -- Capacity
    default_max_capacity INTEGER NOT NULL,
    
    -- Difficulty
    difficulty_level SMALLINT NOT NULL CHECK (difficulty_level BETWEEN 1 AND 5),
    
    -- Foreign Keys
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    country_id INTEGER NOT NULL REFERENCES countries(id) ON DELETE RESTRICT,
    trip_type_id INTEGER REFERENCES trip_types(id) ON DELETE RESTRICT,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes
CREATE INDEX ix_trip_templates_company ON trip_templates(company_id);
CREATE INDEX ix_trip_templates_country ON trip_templates(country_id);
CREATE INDEX ix_trip_templates_type ON trip_templates(trip_type_id);
CREATE INDEX ix_trip_templates_active ON trip_templates(is_active);
CREATE INDEX ix_trip_templates_difficulty ON trip_templates(difficulty_level);
```

---

## New Table: `trip_occurrences`

### Purpose
Stores **specific scheduled instances** of a trip template.

### Key Features
- References a trip template
- Has specific dates and guide assignment
- Tracks availability (spots_left, status)
- Can override base price for this specific occurrence

### Schema

```sql
CREATE TABLE trip_occurrences (
    id SERIAL PRIMARY KEY,
    
    -- Foreign Keys
    trip_template_id INTEGER NOT NULL REFERENCES trip_templates(id) ON DELETE RESTRICT,
    guide_id INTEGER REFERENCES guides(id) ON DELETE SET NULL,
    
    -- Schedule
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Pricing (optional override)
    price_override NUMERIC(10, 2),  -- NULL means use template's base_price
    single_supplement_override NUMERIC(10, 2),
    
    -- Capacity & Availability
    max_capacity INTEGER,  -- NULL means use template's default
    spots_left INTEGER NOT NULL,
    status trip_status NOT NULL DEFAULT 'Open',
    
    -- Additional Info
    notes TEXT,  -- Special notes for this occurrence
    notes_he TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Constraints
    CONSTRAINT valid_dates CHECK (end_date >= start_date)
);

-- Indexes
CREATE INDEX ix_trip_occurrences_template ON trip_occurrences(trip_template_id);
CREATE INDEX ix_trip_occurrences_guide ON trip_occurrences(guide_id);
CREATE INDEX ix_trip_occurrences_dates ON trip_occurrences(start_date, end_date);
CREATE INDEX ix_trip_occurrences_status ON trip_occurrences(status);
```

### SQLAlchemy Model

```python
class TripOccurrence(Base):
    """Trip Occurrences - specific scheduled instances of trip templates"""
    __tablename__ = 'trip_occurrences'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    trip_template_id = Column(Integer, ForeignKey('trip_templates.id', ondelete='RESTRICT'), nullable=False, index=True)
    guide_id = Column(Integer, ForeignKey('guides.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Schedule
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    
    # Pricing (overrides)
    price_override = Column(Numeric(10, 2), nullable=True)
    single_supplement_override = Column(Numeric(10, 2), nullable=True)
    
    # Capacity
    max_capacity = Column(Integer, nullable=True)  # NULL = use template default
    spots_left = Column(Integer, nullable=False)
    status = Column(Enum(TripStatus), default=TripStatus.OPEN, nullable=False, index=True)
    
    # Notes
    notes = Column(Text)
    notes_he = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    template = relationship('TripTemplate', back_populates='occurrences', lazy='joined')
    guide = relationship('Guide', back_populates='trip_occurrences')
    
    # Computed properties
    @property
    def effective_price(self):
        """Returns the actual price (override or template base)"""
        return self.price_override or self.template.base_price
    
    @property
    def effective_capacity(self):
        """Returns the actual capacity (override or template default)"""
        return self.max_capacity or self.template.default_max_capacity
```

---

## Updated Junction Table: `trip_template_tags`

### Purpose
Links trip templates to theme tags (renamed from `trip_tags`).

### Schema

```sql
CREATE TABLE trip_template_tags (
    trip_template_id INTEGER NOT NULL REFERENCES trip_templates(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (trip_template_id, tag_id)
);

CREATE INDEX ix_trip_template_tags_tag ON trip_template_tags(tag_id);
```

---

## Entity Relationship Diagram

```
+-------------+       +------------------+       +-------------------+
|  COMPANIES  |------>|  TRIP_TEMPLATES  |------>|  TRIP_OCCURRENCES |
+-------------+  1:N  +------------------+  1:N  +-------------------+
                              |                          |
                              |                          |
                              v                          v
                      +---------------+           +----------+
                      |   COUNTRIES   |           |  GUIDES  |
                      +---------------+           +----------+
                              ^
                              |
                      +---------------+
                      |  TRIP_TYPES   |
                      +---------------+
                              ^
                              |
                      +---------------------+
                      | TRIP_TEMPLATE_TAGS  |-----> TAGS
                      +---------------------+
```

---

## Migration Strategy

### Phase 1: Add Companies Table (Non-Breaking)

```sql
-- Step 1.1: Create companies table
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    name_he VARCHAR(255) NOT NULL,
    description TEXT,
    description_he TEXT,
    logo_url VARCHAR(500),
    website_url VARCHAR(500),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Step 1.2: Insert a default company for existing trips
INSERT INTO companies (name, name_he, description, is_active)
VALUES ('Default Company', 'חברה ברירת מחדל', 'Placeholder for existing trips', TRUE);

-- Step 1.3: Add company_id to trips table (nullable initially)
ALTER TABLE trips ADD COLUMN company_id INTEGER REFERENCES companies(id);

-- Step 1.4: Set all existing trips to default company
UPDATE trips SET company_id = (SELECT id FROM companies WHERE name = 'Default Company');

-- Step 1.5: Make company_id NOT NULL
ALTER TABLE trips ALTER COLUMN company_id SET NOT NULL;
```

### Phase 2: Implement Trip Templates (Breaking Change)

This is a larger refactoring that requires:

1. **Backup** current data
2. **Create** new tables (trip_templates, trip_occurrences)
3. **Migrate** data from trips to trip_templates + trip_occurrences
4. **Update** API endpoints
5. **Update** frontend
6. **Switch** production

Detailed migration script:

```sql
-- Step 2.1: Create trip_templates table
CREATE TABLE trip_templates (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    title_he VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    description_he TEXT NOT NULL,
    short_description VARCHAR(500),
    short_description_he VARCHAR(500),
    image_url VARCHAR(500),
    base_price NUMERIC(10, 2) NOT NULL,
    single_supplement_price NUMERIC(10, 2),
    typical_duration_days INTEGER NOT NULL,
    default_max_capacity INTEGER NOT NULL,
    difficulty_level SMALLINT NOT NULL,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    country_id INTEGER NOT NULL REFERENCES countries(id),
    trip_type_id INTEGER REFERENCES trip_types(id),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Step 2.2: Create trip_occurrences table
CREATE TABLE trip_occurrences (
    id SERIAL PRIMARY KEY,
    trip_template_id INTEGER NOT NULL REFERENCES trip_templates(id),
    guide_id INTEGER REFERENCES guides(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    price_override NUMERIC(10, 2),
    single_supplement_override NUMERIC(10, 2),
    max_capacity INTEGER,
    spots_left INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Open',
    notes TEXT,
    notes_he TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Step 2.3: Migrate data - Create unique templates from trips
INSERT INTO trip_templates (
    title, title_he, description, description_he, image_url,
    base_price, single_supplement_price, typical_duration_days,
    default_max_capacity, difficulty_level, company_id, country_id, trip_type_id,
    created_at, updated_at
)
SELECT DISTINCT ON (title, country_id, trip_type_id)
    title, title_he, description, description_he, image_url,
    price, single_supplement_price, 
    EXTRACT(DAY FROM (end_date - start_date))::INTEGER + 1,
    max_capacity, difficulty_level, company_id, country_id, trip_type_id,
    MIN(created_at), MAX(updated_at)
FROM trips
GROUP BY title, title_he, description, description_he, image_url, 
         price, single_supplement_price, max_capacity, difficulty_level, 
         company_id, country_id, trip_type_id;

-- Step 2.4: Create occurrences from trips
INSERT INTO trip_occurrences (
    trip_template_id, guide_id, start_date, end_date,
    price_override, max_capacity, spots_left, status, created_at, updated_at
)
SELECT 
    tt.id, t.guide_id, t.start_date, t.end_date,
    CASE WHEN t.price != tt.base_price THEN t.price ELSE NULL END,
    CASE WHEN t.max_capacity != tt.default_max_capacity THEN t.max_capacity ELSE NULL END,
    t.spots_left, t.status, t.created_at, t.updated_at
FROM trips t
JOIN trip_templates tt ON 
    t.title = tt.title AND 
    t.country_id = tt.country_id AND 
    COALESCE(t.trip_type_id, 0) = COALESCE(tt.trip_type_id, 0);

-- Step 2.5: Migrate trip_tags to trip_template_tags
CREATE TABLE trip_template_tags (
    trip_template_id INTEGER NOT NULL REFERENCES trip_templates(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (trip_template_id, tag_id)
);

INSERT INTO trip_template_tags (trip_template_id, tag_id, created_at)
SELECT DISTINCT tt.id, tg.tag_id, MIN(tg.created_at)
FROM trip_tags tg
JOIN trips t ON t.id = tg.trip_id
JOIN trip_templates tt ON t.title = tt.title AND t.country_id = tt.country_id
GROUP BY tt.id, tg.tag_id;

-- Step 2.6: Rename old tables (backup)
ALTER TABLE trips RENAME TO trips_backup;
ALTER TABLE trip_tags RENAME TO trip_tags_backup;

-- Step 2.7: Create views for backward compatibility (optional)
CREATE VIEW trips_compat AS
SELECT 
    o.id,
    tt.title, tt.title_he,
    tt.description, tt.description_he,
    tt.image_url,
    o.start_date, o.end_date,
    COALESCE(o.price_override, tt.base_price) as price,
    COALESCE(o.single_supplement_override, tt.single_supplement_price) as single_supplement_price,
    COALESCE(o.max_capacity, tt.default_max_capacity) as max_capacity,
    o.spots_left, o.status,
    tt.difficulty_level,
    tt.country_id, o.guide_id, tt.trip_type_id, tt.company_id,
    o.created_at, o.updated_at
FROM trip_occurrences o
JOIN trip_templates tt ON o.trip_template_id = tt.id;
```

---

## API Changes Required

### New Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/companies` | List all active companies |
| GET | `/api/companies/:id` | Get company details |
| POST | `/api/companies` | Create new company (admin) |
| PUT | `/api/companies/:id` | Update company (admin) |
| DELETE | `/api/companies/:id` | Deactivate company (admin) |
| GET | `/api/trip-templates` | List all trip templates |
| GET | `/api/trip-templates/:id` | Get template with occurrences |
| GET | `/api/trip-templates/:id/occurrences` | List occurrences for template |
| GET | `/api/occurrences` | List all occurrences (with filters) |
| GET | `/api/occurrences/:id` | Get occurrence details |

### Modified Endpoints

| Endpoint | Change |
|----------|--------|
| `/api/recommendations` | Now returns occurrences, joined with templates |
| `/api/trips` | Becomes alias for `/api/occurrences` |
| `/api/trips/:id` | Returns occurrence with template data |

### Response Format Change

**Before (current):**
```json
{
  "trip": {
    "id": 1,
    "title": "Safari Adventure",
    "start_date": "2025-04-01",
    "guide_id": 5
  }
}
```

**After (new):**
```json
{
  "occurrence": {
    "id": 101,
    "start_date": "2025-04-01",
    "guide": { "id": 5, "name": "John" },
    "template": {
      "id": 1,
      "title": "Safari Adventure",
      "company": { "id": 1, "name": "Safari Co" }
    }
  }
}
```

---

## Frontend Impact

### Required Changes

1. **Trip Card Component**
   - Add company logo/name display
   - Link to company page (if implemented)

2. **Trip Details Page**
   - Show company information section
   - Show "Other dates for this trip" section
   - Allow viewing other occurrences of same template

3. **Search/Filter**
   - Add optional company filter
   - Filter by template properties, not occurrence

4. **Data Store**
   - Update types/interfaces for new schema
   - Handle nested template data in occurrences

### New Components (Suggested)

```tsx
// CompanyBadge - displays company logo/name on trip cards
<CompanyBadge company={trip.template.company} size="sm" />

// OtherDates - shows other occurrences of same template
<OtherDates templateId={trip.template.id} currentOccurrenceId={trip.id} />

// CompanyPage - dedicated page for company info
/company/[id]/page.tsx
```

---

## Benefits of This Architecture

### 1. Data Integrity
- No duplication of trip descriptions
- Company info centralized
- Single source of truth for trip routes

### 2. Flexibility
- Same route, different guides
- Same route, different dates
- Easy price adjustments per occurrence

### 3. Business Intelligence
- Track which companies bring most trips
- Analyze guide performance across trips
- Compare template popularity

### 4. Scalability
- Easy to add new companies
- Easy to schedule new occurrences
- Efficient queries with proper indexes

### 5. User Experience
- Show "Other dates available" for popular trips
- Filter by company
- See guide history for a route

---

## Additional Suggestions

### 1. Company-Guide Relationship
Consider adding a junction table for guides employed by companies:

```sql
CREATE TABLE company_guides (
    company_id INTEGER REFERENCES companies(id),
    guide_id INTEGER REFERENCES guides(id),
    is_primary BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (company_id, guide_id)
);
```

### 2. Trip Template Versions
For tracking changes to trip descriptions over time:

```sql
CREATE TABLE trip_template_versions (
    id SERIAL PRIMARY KEY,
    trip_template_id INTEGER REFERENCES trip_templates(id),
    version INTEGER NOT NULL,
    description TEXT,
    description_he TEXT,
    effective_from DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Multi-Country Trips
For trips that visit multiple countries:

```sql
CREATE TABLE trip_template_countries (
    trip_template_id INTEGER REFERENCES trip_templates(id),
    country_id INTEGER REFERENCES countries(id),
    visit_order INTEGER NOT NULL,
    days_in_country INTEGER,
    PRIMARY KEY (trip_template_id, country_id)
);
```

### 4. Price History
Track price changes over time:

```sql
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    trip_template_id INTEGER REFERENCES trip_templates(id),
    old_price NUMERIC(10, 2),
    new_price NUMERIC(10, 2),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100)
);
```

---

## Implementation Timeline

### Week 1: Phase 1 - Companies (Non-Breaking)
- [ ] Create companies table
- [ ] Add company_id to trips
- [ ] Create API endpoints
- [ ] Update frontend to display company info

### Week 2-3: Phase 2 - Trip Templates (Breaking)
- [ ] Create new tables
- [ ] Write migration script
- [ ] Test migration on staging
- [ ] Update all API endpoints
- [ ] Update recommendation algorithm
- [ ] Update frontend data handling

### Week 4: Testing & Deployment
- [ ] Full integration testing
- [ ] Performance testing
- [ ] Backup production data
- [ ] Execute migration
- [ ] Monitor and fix issues

---

## Rollback Plan

If issues arise after migration:

1. **Immediate**: Switch to backup tables
   ```sql
   ALTER TABLE trip_templates RENAME TO trip_templates_new;
   ALTER TABLE trips_backup RENAME TO trips;
   ```

2. **API**: Revert to previous code version

3. **Data**: All original data preserved in `*_backup` tables

---

## Questions to Consider

1. **Do all existing trips belong to one company, or multiple?**
   - If one: Create single default company
   - If multiple: Need company data before migration

2. **Should the same trip template be bookable multiple times on same dates?**
   - Yes: Allow duplicate occurrences
   - No: Add unique constraint on (template_id, start_date)

3. **What happens to guides when a company is deleted?**
   - Current: Guides are separate, not tied to companies
   - Alternative: Add company-guide relationship

4. **Should price history be tracked?**
   - For auditing: Yes, add price_history table
   - For simplicity: No, just store current price

---

## Conclusion

This schema refactoring will significantly improve data management and enable new features like:
- Company profiles and filtering
- Multiple dates for popular trips
- Flexible guide assignments
- Better business analytics

The migration can be done in phases to minimize risk, with Phase 1 (Companies) being non-breaking and providing immediate value.

---

# IMPLEMENTATION DETAILS

## Files Created/Modified

### New Files

| File | Purpose |
|------|---------|
| `backend/models_v2.py` | New SQLAlchemy models with all V2 features |
| `backend/migrations/_003_add_companies.py` | Phase 1 migration: Companies table |
| `backend/migrations/_004_refactor_trips_to_templates.py` | Phase 2 migration: Full refactoring |
| `backend/run_schema_v2_migration.py` | Convenient migration runner script |

### Modified Files

| File | Changes |
|------|---------|
| `backend/migrations/__init__.py` | Added V2 migration functions |

---

## How to Run Migrations

### Prerequisites
1. Ensure database is accessible
2. Backend dependencies installed (`pip install -r requirements.txt`)

### Option 1: Using the Migration Runner (Recommended)

```bash
cd backend

# View help
python run_schema_v2_migration.py --help

# Create backup and run all migrations
python run_schema_v2_migration.py --backup

# Or run without backup (not recommended)
python run_schema_v2_migration.py -y

# Run Phase 1 only (Companies)
python run_schema_v2_migration.py --phase1-only

# Run Phase 2 only (after Phase 1)
python run_schema_v2_migration.py --phase2-only

# Verify migration status
python run_schema_v2_migration.py --verify

# Rollback all changes
python run_schema_v2_migration.py --rollback
```

### Option 2: Using Individual Migration Files

```bash
cd backend

# Phase 1: Companies
python -m migrations._003_add_companies

# Phase 2: Templates/Occurrences
python -m migrations._004_refactor_trips_to_templates

# Verify Phase 2
python -m migrations._004_refactor_trips_to_templates --verify

# Rollback
python -m migrations._004_refactor_trips_to_templates --rollback
python -m migrations._003_add_companies --rollback
```

### Option 3: Using Python Code

```python
from migrations import (
    upgrade_companies,
    upgrade_trip_templates,
    verify_trip_templates,
    downgrade_trip_templates,
    downgrade_companies,
)

# Run Phase 1
upgrade_companies()

# Run Phase 2
upgrade_trip_templates()

# Verify
results = verify_trip_templates()
print(results)
```

---

## Key Implementation Decisions

### 1. Legacy ID Tracking (CRITICAL)
Instead of matching on string titles (risky), we use `legacy_trip_id`:
- Each `trip_template` stores the original `trips.id` 
- All joins during migration use this ID
- Ensures 100% accurate data migration
- Column can be dropped after verification

### 2. Hybrid Property for effective_price
```python
@hybrid_property
def effective_price(self):
    if self.price_override is not None:
        return self.price_override
    return self.template.base_price

@effective_price.expression
def effective_price(cls):
    return case(
        (cls.price_override.isnot(None), cls.price_override),
        else_=select(TripTemplate.base_price)
            .where(TripTemplate.id == cls.trip_template_id)
            .correlate(cls).scalar_subquery()
    )
```
This allows SQL-level sorting/filtering by calculated price.

### 3. Spots Left Concurrency Note
A TODO comment was added to TripOccurrence model:
```
TODO: For production-grade concurrency control, spots_left should be 
replaced with a Bookings table where availability is computed as:
(max_capacity - COUNT(confirmed_bookings)). This prevents race conditions
when multiple users try to book simultaneously.
```

### 4. Multi-Country Support
- `trip_template_countries` junction table
- `visit_order` column for sequence of countries visited
- `days_in_country` optional field for duration per country
- `primary_country_id` kept for backward compatibility

### 5. Image Overrides
- `image_url_override` on TripOccurrence
- Allows seasonal variations (winter vs summer photos)
- Falls back to template's `image_url` if not set

---

## Seeded Companies (10)

The migration seeds these travel companies:

1. **Global Horizons Travel** - Worldwide adventure tours
2. **Nature Path Expeditions** - Eco-friendly wildlife tours
3. **Heritage Journeys** - Cultural and historical tours
4. **Summit Adventures** - Mountain treks and hiking
5. **Blue Ocean Cruises** - Premium cruise experiences
6. **Wanderlust World Tours** - Group tours for curious travelers
7. **Safari Dreams** - African wildlife safaris
8. **Eastern Winds Travel** - Asia specialist
9. **Polar Frontiers** - Antarctica and Arctic expeditions
10. **Caravan Routes** - Overland adventures on historic routes

---

## Post-Migration Checklist

After running migrations:

- [ ] Run `--verify` to check data integrity
- [ ] Test API endpoints with new schema
- [ ] Update frontend if needed (API response format changes)
- [ ] Update recommendation algorithm to use new tables
- [ ] Test booking flow with TripOccurrences
- [ ] Review backward compatibility view (`trips_compat`)
- [ ] Drop backup tables when confident (`trips_backup_v2`, `trip_tags_backup_v2`)
- [ ] Consider dropping `legacy_trip_id` columns after verification

---

## API Migration Notes

The recommendation API should be updated to:
1. Query `trip_occurrences` joined with `trip_templates`
2. Use `COALESCE(price_override, base_price)` for price filtering
3. Include company information in responses
4. Support filtering by company

Example API response change:
```json
// Before
{"trip": {"id": 1, "title": "Safari", "price": 3000}}

// After
{
  "occurrence": {
    "id": 101,
    "startDate": "2025-04-01",
    "price": 3000,
    "template": {
      "id": 1,
      "title": "Safari",
      "company": {"id": 7, "name": "Safari Dreams"}
    }
  }
}
```
