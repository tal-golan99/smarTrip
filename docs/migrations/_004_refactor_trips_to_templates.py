"""
Migration 004: Refactor Trips to Templates + Occurrences (Phase 2)
==================================================================

This is a BREAKING migration that:
1. Creates trip_templates table (from trips)
2. Creates trip_occurrences table (scheduled instances)
3. Creates trip_template_tags junction table
4. Creates trip_template_countries junction table (multi-country support)
5. Creates price_history table
6. Creates reviews table
7. Migrates existing data safely using legacy_trip_id
8. Backs up old tables

IMPORTANT: Run migration 003 (companies) BEFORE this migration!

Safety Features:
- Uses legacy_trip_id for reliable data migration (not string matching)
- Backs up old tables before changes
- Transaction-safe (all or nothing)
- Can be rolled back
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text
from datetime import datetime


def upgrade() -> bool:
    """
    Run the Phase 2 migration: Refactor trips to templates + occurrences.
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*70)
    print("MIGRATION 004: REFACTOR TRIPS TO TEMPLATES + OCCURRENCES (PHASE 2)")
    print("="*70)
    
    with engine.connect() as conn:
        try:
            # ============================================
            # PRE-FLIGHT CHECKS
            # ============================================
            print("\n[PRE-FLIGHT] Checking prerequisites...")
            
            # Check companies table exists
            check_companies = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'companies'
                );
            """)
            if not conn.execute(check_companies).scalar():
                print("  [ERROR] Companies table does not exist!")
                print("  Run migration 003 first: python -m migrations._003_add_companies")
                return False
            print("  -> Companies table exists")
            
            # Check trips table has company_id
            check_company_id = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'trips' AND column_name = 'company_id'
                );
            """)
            if not conn.execute(check_company_id).scalar():
                print("  [ERROR] trips.company_id column does not exist!")
                print("  Run migration 003 first")
                return False
            print("  -> trips.company_id exists")
            
            # Check if already migrated
            check_templates = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'trip_templates'
                );
            """)
            if conn.execute(check_templates).scalar():
                print("  [WARNING] trip_templates table already exists")
                print("  Migration may have already been run. Skipping creation...")
                # Continue to allow re-running for data migration fixes
            
            # ============================================
            # STEP 1: CREATE NEW TABLES
            # ============================================
            print("\n[STEP 1] Creating new tables...")
            
            # Create trip_templates
            print("  Creating trip_templates...")
            create_templates = text("""
                CREATE TABLE IF NOT EXISTS trip_templates (
                    id SERIAL PRIMARY KEY,
                    
                    -- Basic Info
                    title VARCHAR(255) NOT NULL,
                    title_he VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    description_he TEXT NOT NULL,
                    short_description VARCHAR(500),
                    short_description_he VARCHAR(500),
                    image_url VARCHAR(500),
                    
                    -- Pricing
                    base_price NUMERIC(10, 2) NOT NULL,
                    single_supplement_price NUMERIC(10, 2),
                    
                    -- Duration
                    typical_duration_days INTEGER NOT NULL,
                    
                    -- Capacity
                    default_max_capacity INTEGER NOT NULL,
                    
                    -- Difficulty (1-5)
                    difficulty_level SMALLINT NOT NULL CHECK (difficulty_level BETWEEN 1 AND 5),
                    
                    -- Foreign Keys
                    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
                    trip_type_id INTEGER REFERENCES trip_types(id) ON DELETE RESTRICT,
                    primary_country_id INTEGER REFERENCES countries(id) ON DELETE RESTRICT,
                    
                    -- Status
                    is_active BOOLEAN DEFAULT TRUE NOT NULL,
                    
                    -- Extensible properties (JSONB) - stores dynamic metadata
                    -- Examples: packing_list, requirements (visas, vaccinations), type-specific attributes
                    properties JSONB,
                    
                    -- Migration tracking (CRITICAL: for safe data migration)
                    legacy_trip_id INTEGER,
                    
                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    
                    -- Constraints
                    CONSTRAINT ck_templates_duration_positive CHECK (typical_duration_days > 0),
                    CONSTRAINT ck_templates_price_positive CHECK (base_price >= 0)
                );
                
                CREATE INDEX IF NOT EXISTS ix_trip_templates_company ON trip_templates(company_id);
                CREATE INDEX IF NOT EXISTS ix_trip_templates_type ON trip_templates(trip_type_id);
                CREATE INDEX IF NOT EXISTS ix_trip_templates_country ON trip_templates(primary_country_id);
                CREATE INDEX IF NOT EXISTS ix_trip_templates_active ON trip_templates(is_active);
                CREATE INDEX IF NOT EXISTS ix_trip_templates_difficulty ON trip_templates(difficulty_level);
                CREATE INDEX IF NOT EXISTS ix_trip_templates_legacy ON trip_templates(legacy_trip_id);
                CREATE INDEX IF NOT EXISTS ix_trip_templates_title ON trip_templates(title);
            """)
            conn.execute(create_templates)
            print("    -> trip_templates created")
            
            # Create trip_occurrences
            print("  Creating trip_occurrences...")
            create_occurrences = text("""
                CREATE TABLE IF NOT EXISTS trip_occurrences (
                    id SERIAL PRIMARY KEY,
                    
                    -- Foreign Keys
                    trip_template_id INTEGER NOT NULL REFERENCES trip_templates(id) ON DELETE RESTRICT,
                    guide_id INTEGER REFERENCES guides(id) ON DELETE SET NULL,
                    
                    -- Schedule
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    
                    -- Pricing (overrides)
                    price_override NUMERIC(10, 2),
                    single_supplement_override NUMERIC(10, 2),
                    
                    -- Capacity (override)
                    max_capacity_override INTEGER,
                    
                    -- Availability
                    spots_left INTEGER NOT NULL CHECK (spots_left >= 0),
                    status VARCHAR(20) NOT NULL DEFAULT 'Open',
                    
                    -- Image override (for seasonal variations)
                    image_url_override VARCHAR(500),
                    
                    -- Notes
                    notes TEXT,
                    notes_he TEXT,
                    
                    -- Extensible properties (JSONB) - stores occurrence-specific dynamic metadata
                    -- Examples: special_requirements, cabin_assignment, specific_equipment
                    properties JSONB,
                    
                    -- Migration tracking
                    legacy_trip_id INTEGER,
                    
                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    
                    -- Constraints
                    CONSTRAINT ck_occurrences_valid_dates CHECK (end_date >= start_date)
                );
                
                CREATE INDEX IF NOT EXISTS ix_trip_occurrences_template ON trip_occurrences(trip_template_id);
                CREATE INDEX IF NOT EXISTS ix_trip_occurrences_guide ON trip_occurrences(guide_id);
                CREATE INDEX IF NOT EXISTS ix_trip_occurrences_dates ON trip_occurrences(start_date, end_date);
                CREATE INDEX IF NOT EXISTS ix_trip_occurrences_status ON trip_occurrences(status);
                CREATE INDEX IF NOT EXISTS ix_trip_occurrences_legacy ON trip_occurrences(legacy_trip_id);
            """)
            conn.execute(create_occurrences)
            print("    -> trip_occurrences created")
            
            # Create trip_template_tags (junction)
            print("  Creating trip_template_tags...")
            create_template_tags = text("""
                CREATE TABLE IF NOT EXISTS trip_template_tags (
                    trip_template_id INTEGER NOT NULL REFERENCES trip_templates(id) ON DELETE CASCADE,
                    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    PRIMARY KEY (trip_template_id, tag_id)
                );
                
                CREATE INDEX IF NOT EXISTS ix_trip_template_tags_tag ON trip_template_tags(tag_id);
            """)
            conn.execute(create_template_tags)
            print("    -> trip_template_tags created")
            
            # Create trip_template_countries (junction for multi-country)
            print("  Creating trip_template_countries...")
            create_template_countries = text("""
                CREATE TABLE IF NOT EXISTS trip_template_countries (
                    trip_template_id INTEGER NOT NULL REFERENCES trip_templates(id) ON DELETE CASCADE,
                    country_id INTEGER NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
                    visit_order INTEGER NOT NULL DEFAULT 1,
                    days_in_country INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    PRIMARY KEY (trip_template_id, country_id)
                );
                
                CREATE INDEX IF NOT EXISTS ix_trip_template_countries_country ON trip_template_countries(country_id);
                CREATE INDEX IF NOT EXISTS ix_trip_template_countries_order ON trip_template_countries(trip_template_id, visit_order);
            """)
            conn.execute(create_template_countries)
            print("    -> trip_template_countries created")
            
            # Create price_history
            print("  Creating price_history...")
            create_price_history = text("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id SERIAL PRIMARY KEY,
                    trip_template_id INTEGER NOT NULL REFERENCES trip_templates(id) ON DELETE CASCADE,
                    old_price NUMERIC(10, 2),
                    new_price NUMERIC(10, 2) NOT NULL,
                    change_reason VARCHAR(255),
                    changed_by VARCHAR(100),
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS ix_price_history_template ON price_history(trip_template_id);
                CREATE INDEX IF NOT EXISTS ix_price_history_date ON price_history(changed_at);
            """)
            conn.execute(create_price_history)
            print("    -> price_history created")
            
            # Create reviews
            print("  Creating reviews...")
            create_reviews = text("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id SERIAL PRIMARY KEY,
                    
                    -- What is being reviewed
                    trip_template_id INTEGER NOT NULL REFERENCES trip_templates(id) ON DELETE CASCADE,
                    trip_occurrence_id INTEGER REFERENCES trip_occurrences(id) ON DELETE SET NULL,
                    
                    -- Reviewer info
                    reviewer_name VARCHAR(100),
                    reviewer_email VARCHAR(255),
                    is_anonymous BOOLEAN DEFAULT FALSE NOT NULL,
                    
                    -- Review content
                    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
                    title VARCHAR(200),
                    content TEXT,
                    content_he TEXT,
                    
                    -- Metadata
                    source VARCHAR(20) DEFAULT 'Website' NOT NULL,
                    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
                    is_approved BOOLEAN DEFAULT FALSE NOT NULL,
                    is_featured BOOLEAN DEFAULT FALSE NOT NULL,
                    
                    -- Timestamps
                    travel_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS ix_reviews_template ON reviews(trip_template_id);
                CREATE INDEX IF NOT EXISTS ix_reviews_occurrence ON reviews(trip_occurrence_id);
                CREATE INDEX IF NOT EXISTS ix_reviews_approved ON reviews(is_approved);
                CREATE INDEX IF NOT EXISTS ix_reviews_featured ON reviews(is_featured);
                CREATE INDEX IF NOT EXISTS ix_reviews_rating ON reviews(rating);
            """)
            conn.execute(create_reviews)
            print("    -> reviews created")
            
            # ============================================
            # STEP 2: MIGRATE DATA
            # ============================================
            print("\n[STEP 2] Migrating data from trips table...")
            
            # Check if data already migrated
            check_data = text("SELECT COUNT(*) FROM trip_templates")
            existing_templates = conn.execute(check_data).scalar()
            
            if existing_templates > 0:
                print(f"  -> {existing_templates} templates already exist, skipping data migration")
            else:
                # Step 2a: Create templates from trips (using legacy_trip_id!)
                print("  [2a] Creating trip_templates from trips...")
                
                # For initial migration, each trip becomes one template
                # (Future: deduplicate templates with same title/description)
                migrate_templates = text("""
                    INSERT INTO trip_templates (
                        title, title_he, description, description_he,
                        image_url, base_price, single_supplement_price,
                        typical_duration_days, default_max_capacity, difficulty_level,
                        company_id, trip_type_id, primary_country_id,
                        is_active, legacy_trip_id, created_at, updated_at
                    )
                    SELECT 
                        title, title_he, description, description_he,
                        image_url, price, single_supplement_price,
                        (end_date - start_date) + 1,
                        max_capacity, difficulty_level,
                        company_id, trip_type_id, country_id,
                        TRUE, id, created_at, updated_at
                    FROM trips
                    ORDER BY id;
                """)
                conn.execute(migrate_templates)
                
                # Get count
                count_result = conn.execute(text("SELECT COUNT(*) FROM trip_templates"))
                template_count = count_result.scalar()
                print(f"    -> Created {template_count} trip templates")
                
                # Step 2b: Create occurrences from trips (using legacy_trip_id for join!)
                print("  [2b] Creating trip_occurrences from trips...")
                
                migrate_occurrences = text("""
                    INSERT INTO trip_occurrences (
                        trip_template_id, guide_id,
                        start_date, end_date,
                        price_override, single_supplement_override,
                        max_capacity_override, spots_left, status,
                        legacy_trip_id, created_at, updated_at
                    )
                    SELECT 
                        tt.id,  -- Join via legacy_trip_id, NOT string matching!
                        t.guide_id,
                        t.start_date, t.end_date,
                        NULL,  -- No override (template has the base price)
                        NULL,
                        NULL,  -- No override (template has the default capacity)
                        t.spots_left, t.status,
                        t.id, t.created_at, t.updated_at
                    FROM trips t
                    JOIN trip_templates tt ON tt.legacy_trip_id = t.id
                    ORDER BY t.id;
                """)
                conn.execute(migrate_occurrences)
                
                count_result = conn.execute(text("SELECT COUNT(*) FROM trip_occurrences"))
                occurrence_count = count_result.scalar()
                print(f"    -> Created {occurrence_count} trip occurrences")
                
                # Step 2c: Migrate trip_tags to trip_template_tags
                print("  [2c] Migrating trip_tags to trip_template_tags...")
                
                migrate_tags = text("""
                    INSERT INTO trip_template_tags (trip_template_id, tag_id, created_at)
                    SELECT DISTINCT 
                        tt.id,  -- Join via legacy_trip_id!
                        tg.tag_id,
                        COALESCE(tg.created_at, NOW())
                    FROM trip_tags tg
                    JOIN trip_templates tt ON tt.legacy_trip_id = tg.trip_id
                    ON CONFLICT (trip_template_id, tag_id) DO NOTHING;
                """)
                conn.execute(migrate_tags)
                
                count_result = conn.execute(text("SELECT COUNT(*) FROM trip_template_tags"))
                tag_count = count_result.scalar()
                print(f"    -> Migrated {tag_count} template-tag associations")
                
                # Step 2d: Create trip_template_countries (from primary country)
                print("  [2d] Creating trip_template_countries...")
                
                migrate_countries = text("""
                    INSERT INTO trip_template_countries (trip_template_id, country_id, visit_order, created_at)
                    SELECT 
                        id,
                        primary_country_id,
                        1,  -- First country in visit order
                        NOW()
                    FROM trip_templates
                    WHERE primary_country_id IS NOT NULL
                    ON CONFLICT (trip_template_id, country_id) DO NOTHING;
                """)
                conn.execute(migrate_countries)
                
                count_result = conn.execute(text("SELECT COUNT(*) FROM trip_template_countries"))
                country_count = count_result.scalar()
                print(f"    -> Created {country_count} template-country associations")
                
                # Step 2e: Create initial price history records
                print("  [2e] Creating initial price history...")
                
                create_initial_history = text("""
                    INSERT INTO price_history (trip_template_id, old_price, new_price, change_reason, changed_by, changed_at)
                    SELECT 
                        id,
                        NULL,  -- No old price (initial record)
                        base_price,
                        'Initial migration from trips table',
                        'system_migration',
                        created_at
                    FROM trip_templates;
                """)
                conn.execute(create_initial_history)
                print("    -> Initial price history created")
            
            # ============================================
            # STEP 3: BACKUP OLD TABLES
            # ============================================
            print("\n[STEP 3] Backing up old tables...")
            
            # Check if backup already exists
            check_backup = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'trips_backup_v2'
                );
            """)
            backup_exists = conn.execute(check_backup).scalar()
            
            if backup_exists:
                print("  -> Backup tables already exist, skipping")
            else:
                backup_tables = text("""
                    -- Backup trips
                    CREATE TABLE trips_backup_v2 AS SELECT * FROM trips;
                    
                    -- Backup trip_tags
                    CREATE TABLE trip_tags_backup_v2 AS SELECT * FROM trip_tags;
                """)
                conn.execute(backup_tables)
                print("  -> Created trips_backup_v2 and trip_tags_backup_v2")
            
            # ============================================
            # STEP 4: CREATE COMPATIBILITY VIEW
            # ============================================
            print("\n[STEP 4] Creating backward compatibility view...")
            
            create_view = text("""
                CREATE OR REPLACE VIEW trips_compat AS
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
            """)
            conn.execute(create_view)
            print("  -> trips_compat view created")
            
            conn.commit()
            
            # ============================================
            # VERIFICATION
            # ============================================
            print("\n[VERIFICATION] Checking migration...")
            
            stats = {}
            stats['templates'] = conn.execute(text("SELECT COUNT(*) FROM trip_templates")).scalar()
            stats['occurrences'] = conn.execute(text("SELECT COUNT(*) FROM trip_occurrences")).scalar()
            stats['template_tags'] = conn.execute(text("SELECT COUNT(*) FROM trip_template_tags")).scalar()
            stats['template_countries'] = conn.execute(text("SELECT COUNT(*) FROM trip_template_countries")).scalar()
            stats['price_history'] = conn.execute(text("SELECT COUNT(*) FROM price_history")).scalar()
            stats['original_trips'] = conn.execute(text("SELECT COUNT(*) FROM trips")).scalar()
            
            print(f"  Original trips: {stats['original_trips']}")
            print(f"  Trip templates: {stats['templates']}")
            print(f"  Trip occurrences: {stats['occurrences']}")
            print(f"  Template tags: {stats['template_tags']}")
            print(f"  Template countries: {stats['template_countries']}")
            print(f"  Price history: {stats['price_history']}")
            
            if stats['templates'] == stats['occurrences'] == stats['original_trips']:
                print("\n  [OK] Data migration verified: 1:1 mapping maintained")
            else:
                print("\n  [WARNING] Counts don't match - please verify data manually")
            
            print("\n" + "="*70)
            print("MIGRATION 004 COMPLETED SUCCESSFULLY")
            print("="*70)
            print("\nNOTE: Old tables are preserved as trips_backup_v2 and trip_tags_backup_v2")
            print("You can drop them after verifying the migration is successful.")
            print("\nTo use the new schema, update your code to use:")
            print("  - TripTemplate (for trip definitions)")
            print("  - TripOccurrence (for scheduled instances)")
            print("  - Or use the trips_compat view for backward compatibility\n")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return False


def downgrade() -> bool:
    """
    Rollback the Phase 2 migration.
    
    WARNING: This will drop all new tables. Data can be restored from backups.
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*70)
    print("ROLLBACK MIGRATION 004: REMOVE TEMPLATES/OCCURRENCES")
    print("="*70)
    
    with engine.connect() as conn:
        try:
            print("\n[STEP 1] Dropping views...")
            conn.execute(text("DROP VIEW IF EXISTS trips_compat CASCADE;"))
            print("  -> Dropped trips_compat view")
            
            print("\n[STEP 2] Dropping tables (in dependency order)...")
            
            tables = [
                'reviews',
                'price_history',
                'trip_template_countries',
                'trip_template_tags',
                'trip_occurrences',
                'trip_templates',
            ]
            
            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
                print(f"  -> Dropped {table}")
            
            print("\n[STEP 3] Note: Backup tables preserved")
            print("  -> trips_backup_v2 and trip_tags_backup_v2 are still available")
            print("  -> Original trips and trip_tags tables are unchanged")
            
            conn.commit()
            
            print("\n" + "="*70)
            print("ROLLBACK COMPLETED SUCCESSFULLY")
            print("="*70 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Rollback failed: {e}")
            conn.rollback()
            return False


def verify_migration() -> dict:
    """
    Verify the migration was successful by comparing counts and data.
    
    Returns:
        Dictionary with verification results
    """
    with engine.connect() as conn:
        results = {
            'success': True,
            'checks': [],
            'stats': {}
        }
        
        # Check all tables exist
        tables = ['trip_templates', 'trip_occurrences', 'trip_template_tags', 
                  'trip_template_countries', 'price_history', 'reviews']
        
        for table in tables:
            exists = conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table}'
                );
            """)).scalar()
            
            results['checks'].append({
                'check': f'Table {table} exists',
                'passed': exists
            })
            
            if not exists:
                results['success'] = False
        
        # Get counts
        for table in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            results['stats'][table] = count
        
        # Verify data integrity
        original_count = conn.execute(text("SELECT COUNT(*) FROM trips")).scalar()
        template_count = results['stats']['trip_templates']
        occurrence_count = results['stats']['trip_occurrences']
        
        results['checks'].append({
            'check': 'All trips migrated to templates',
            'passed': original_count == template_count
        })
        
        results['checks'].append({
            'check': 'All trips have occurrences',
            'passed': original_count == occurrence_count
        })
        
        # Check no orphaned occurrences
        orphans = conn.execute(text("""
            SELECT COUNT(*) FROM trip_occurrences o
            LEFT JOIN trip_templates t ON o.trip_template_id = t.id
            WHERE t.id IS NULL
        """)).scalar()
        
        results['checks'].append({
            'check': 'No orphaned occurrences',
            'passed': orphans == 0
        })
        
        return results


if __name__ == '__main__':
    """Run migration directly"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run migration 004: Templates/Occurrences')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    parser.add_argument('--verify', action='store_true', help='Verify the migration')
    args = parser.parse_args()
    
    if args.verify:
        results = verify_migration()
        print("\n" + "="*70)
        print("MIGRATION VERIFICATION RESULTS")
        print("="*70)
        for check in results['checks']:
            status = "PASS" if check['passed'] else "FAIL"
            print(f"  [{status}] {check['check']}")
        print("\nStatistics:")
        for table, count in results['stats'].items():
            print(f"  {table}: {count} rows")
        exit(0 if results['success'] else 1)
    elif args.rollback:
        success = downgrade()
    else:
        success = upgrade()
    
    exit(0 if success else 1)
