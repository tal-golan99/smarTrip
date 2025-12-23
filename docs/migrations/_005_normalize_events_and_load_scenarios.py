"""
Migration 005: Normalize Events to 3NF and Load Evaluation Scenarios
=====================================================================

This migration:
1. Creates event_categories table
2. Creates event_types table with FK to categories
3. Modifies events table to use event_type_id FK instead of strings
4. Loads 100 user personas into evaluation_scenarios table

This brings the events system to Third Normal Form (3NF).
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text


# ============================================
# SEED DATA: Event Categories and Types
# ============================================

EVENT_CATEGORIES = [
    {'id': 1, 'name': 'navigation', 'name_he': 'ניווט', 'description': 'Page navigation and browsing events'},
    {'id': 2, 'name': 'search', 'name_he': 'חיפוש', 'description': 'Search and filter events'},
    {'id': 3, 'name': 'engagement', 'name_he': 'מעורבות', 'description': 'User engagement with content'},
    {'id': 4, 'name': 'conversion', 'name_he': 'המרה', 'description': 'Conversion and booking events'},
]

EVENT_TYPES = [
    # Navigation (category_id=1)
    {'id': 1, 'name': 'page_view', 'name_he': 'צפייה בדף', 'category_id': 1, 'description': 'User viewed a page'},
    {'id': 2, 'name': 'session_start', 'name_he': 'תחילת סשן', 'category_id': 1, 'description': 'User started a new session'},
    {'id': 3, 'name': 'session_end', 'name_he': 'סיום סשן', 'category_id': 1, 'description': 'User session ended'},
    
    # Search (category_id=2)
    {'id': 4, 'name': 'search', 'name_he': 'חיפוש', 'category_id': 2, 'description': 'User performed a search'},
    {'id': 5, 'name': 'filter_change', 'name_he': 'שינוי פילטר', 'category_id': 2, 'description': 'User changed a filter'},
    {'id': 6, 'name': 'filter_removed', 'name_he': 'הסרת פילטר', 'category_id': 2, 'description': 'User removed a filter'},
    {'id': 7, 'name': 'sort_change', 'name_he': 'שינוי מיון', 'category_id': 2, 'description': 'User changed sort order'},
    
    # Engagement (category_id=3)
    {'id': 8, 'name': 'click_trip', 'name_he': 'לחיצה על טיול', 'category_id': 3, 'description': 'User clicked on a trip'},
    {'id': 9, 'name': 'trip_dwell_time', 'name_he': 'זמן שהייה בטיול', 'category_id': 3, 'description': 'Time spent on trip page'},
    {'id': 10, 'name': 'save_trip', 'name_he': 'שמירת טיול', 'category_id': 3, 'description': 'User saved a trip'},
    {'id': 11, 'name': 'unsave_trip', 'name_he': 'הסרת שמירה', 'category_id': 3, 'description': 'User removed saved trip'},
    {'id': 12, 'name': 'share_trip', 'name_he': 'שיתוף טיול', 'category_id': 3, 'description': 'User shared a trip'},
    {'id': 13, 'name': 'impression', 'name_he': 'חשיפה', 'category_id': 3, 'description': 'Trip shown in results'},
    {'id': 14, 'name': 'scroll_depth', 'name_he': 'עומק גלילה', 'category_id': 3, 'description': 'How far user scrolled'},
    
    # Conversion (category_id=4)
    {'id': 15, 'name': 'contact_whatsapp', 'name_he': 'יצירת קשר וואטסאפ', 'category_id': 4, 'description': 'User contacted via WhatsApp'},
    {'id': 16, 'name': 'contact_phone', 'name_he': 'יצירת קשר טלפון', 'category_id': 4, 'description': 'User contacted via phone'},
    {'id': 17, 'name': 'contact_email', 'name_he': 'יצירת קשר אימייל', 'category_id': 4, 'description': 'User contacted via email'},
    {'id': 18, 'name': 'booking_start', 'name_he': 'התחלת הזמנה', 'category_id': 4, 'description': 'User started booking process'},
    {'id': 19, 'name': 'booking_complete', 'name_he': 'השלמת הזמנה', 'category_id': 4, 'description': 'User completed booking'},
    {'id': 20, 'name': 'inquiry_submit', 'name_he': 'שליחת פנייה', 'category_id': 4, 'description': 'User submitted inquiry'},
]


def upgrade() -> bool:
    """
    Run the migration: Normalize events to 3NF and load scenarios.
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*70)
    print("MIGRATION 005: NORMALIZE EVENTS TO 3NF + LOAD SCENARIOS")
    print("="*70)
    
    with engine.connect() as conn:
        try:
            # ============================================
            # PART 1: CREATE EVENT_CATEGORIES TABLE
            # ============================================
            print("\n[PART 1] Creating event_categories table...")
            
            # Check if table exists
            exists = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'event_categories'
                );
            """)).scalar()
            
            if exists:
                print("  -> Table already exists, skipping creation")
            else:
                conn.execute(text("""
                    CREATE TABLE event_categories (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(50) NOT NULL UNIQUE,
                        name_he VARCHAR(50) NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                    );
                    
                    CREATE INDEX ix_event_categories_name ON event_categories(name);
                """))
                print("  -> Table created")
                
                # Seed categories
                for cat in EVENT_CATEGORIES:
                    conn.execute(text("""
                        INSERT INTO event_categories (id, name, name_he, description)
                        VALUES (:id, :name, :name_he, :description)
                        ON CONFLICT (id) DO NOTHING;
                    """), cat)
                print(f"  -> Seeded {len(EVENT_CATEGORIES)} categories")
            
            # ============================================
            # PART 2: CREATE EVENT_TYPES TABLE
            # ============================================
            print("\n[PART 2] Creating event_types table...")
            
            exists = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'event_types'
                );
            """)).scalar()
            
            if exists:
                print("  -> Table already exists, skipping creation")
            else:
                conn.execute(text("""
                    CREATE TABLE event_types (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(50) NOT NULL UNIQUE,
                        name_he VARCHAR(50) NOT NULL,
                        category_id INTEGER NOT NULL REFERENCES event_categories(id) ON DELETE RESTRICT,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                    );
                    
                    CREATE INDEX ix_event_types_name ON event_types(name);
                    CREATE INDEX ix_event_types_category ON event_types(category_id);
                """))
                print("  -> Table created")
                
                # Seed types
                for et in EVENT_TYPES:
                    conn.execute(text("""
                        INSERT INTO event_types (id, name, name_he, category_id, description)
                        VALUES (:id, :name, :name_he, :category_id, :description)
                        ON CONFLICT (id) DO NOTHING;
                    """), et)
                print(f"  -> Seeded {len(EVENT_TYPES)} event types")
            
            # ============================================
            # PART 3: MODIFY EVENTS TABLE
            # ============================================
            print("\n[PART 3] Modifying events table...")
            
            # Check if event_type_id column already exists
            col_exists = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'events' AND column_name = 'event_type_id'
                );
            """)).scalar()
            
            if col_exists:
                print("  -> event_type_id column already exists, skipping")
            else:
                # Add event_type_id column (nullable first)
                conn.execute(text("""
                    ALTER TABLE events ADD COLUMN event_type_id INTEGER;
                """))
                print("  -> Added event_type_id column")
                
                # Create mapping from string to ID
                type_map = {et['name']: et['id'] for et in EVENT_TYPES}
                
                # Update existing events
                for type_name, type_id in type_map.items():
                    result = conn.execute(text("""
                        UPDATE events 
                        SET event_type_id = :type_id 
                        WHERE event_type = :type_name AND event_type_id IS NULL;
                    """), {'type_id': type_id, 'type_name': type_name})
                    if result.rowcount > 0:
                        print(f"  -> Mapped {result.rowcount} events: {type_name} -> ID {type_id}")
                
                # Handle any unmapped events (assign to page_view as default)
                result = conn.execute(text("""
                    UPDATE events 
                    SET event_type_id = 1 
                    WHERE event_type_id IS NULL;
                """))
                if result.rowcount > 0:
                    print(f"  -> Mapped {result.rowcount} unmapped events to page_view (ID 1)")
                
                # Now make it NOT NULL and add FK
                conn.execute(text("""
                    ALTER TABLE events ALTER COLUMN event_type_id SET NOT NULL;
                """))
                print("  -> Made event_type_id NOT NULL")
                
                conn.execute(text("""
                    ALTER TABLE events 
                    ADD CONSTRAINT fk_events_event_type 
                    FOREIGN KEY (event_type_id) REFERENCES event_types(id) ON DELETE RESTRICT;
                    
                    CREATE INDEX ix_events_event_type_id ON events(event_type_id);
                """))
                print("  -> Added foreign key constraint")
                
                # Drop old string columns
                conn.execute(text("""
                    ALTER TABLE events DROP COLUMN IF EXISTS event_type;
                    ALTER TABLE events DROP COLUMN IF EXISTS event_category;
                """))
                print("  -> Dropped old string columns (event_type, event_category)")
            
            # ============================================
            # PART 4: LOAD EVALUATION SCENARIOS
            # ============================================
            print("\n[PART 4] Loading evaluation scenarios...")
            
            # Check current count
            current_count = conn.execute(text("SELECT COUNT(*) FROM evaluation_scenarios")).scalar()
            
            if current_count >= 100:
                print(f"  -> Already have {current_count} scenarios, skipping load")
            else:
                # Load personas from JSON
                scenarios_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'scenarios'
                )
                personas_file = os.path.join(scenarios_dir, 'generated_personas.json')
                
                if not os.path.exists(personas_file):
                    print(f"  [WARNING] Personas file not found: {personas_file}")
                    print("  Run: python scripts/generate_personas.py")
                else:
                    with open(personas_file, 'r', encoding='utf-8') as f:
                        personas = json.load(f)
                    
                    print(f"  -> Loaded {len(personas)} personas from JSON")
                    
                    # Clear existing scenarios
                    if current_count > 0:
                        conn.execute(text("DELETE FROM evaluation_scenarios;"))
                        print(f"  -> Cleared {current_count} existing scenarios")
                    
                    # Insert personas as scenarios
                    for persona in personas:
                        prefs_json = json.dumps(persona.get('preferences', {}))
                        conn.execute(text("""
                            INSERT INTO evaluation_scenarios (
                                id, name, description, category, preferences,
                                expected_min_results, expected_min_top_score,
                                is_active, priority
                            ) VALUES (
                                :id, :name, :description, :category, CAST(:preferences AS jsonb),
                                :expected_min_results, :expected_min_top_score,
                                TRUE, 5
                            )
                            ON CONFLICT (id) DO UPDATE SET
                                name = EXCLUDED.name,
                                description = EXCLUDED.description,
                                category = EXCLUDED.category,
                                preferences = EXCLUDED.preferences,
                                expected_min_results = EXCLUDED.expected_min_results,
                                expected_min_top_score = EXCLUDED.expected_min_top_score;
                        """), {
                            'id': persona['id'],
                            'name': persona['name'],
                            'description': persona.get('description', ''),
                            'category': persona.get('category', 'core_persona'),
                            'preferences': prefs_json,
                            'expected_min_results': persona.get('expected_min_results', 1),
                            'expected_min_top_score': persona.get('expected_min_top_score'),
                        })
                    
                    final_count = conn.execute(text("SELECT COUNT(*) FROM evaluation_scenarios")).scalar()
                    print(f"  -> Loaded {final_count} scenarios into database")
            
            conn.commit()
            
            # ============================================
            # VERIFICATION
            # ============================================
            print("\n[VERIFICATION]")
            
            cat_count = conn.execute(text("SELECT COUNT(*) FROM event_categories")).scalar()
            type_count = conn.execute(text("SELECT COUNT(*) FROM event_types")).scalar()
            event_count = conn.execute(text("SELECT COUNT(*) FROM events")).scalar()
            scenario_count = conn.execute(text("SELECT COUNT(*) FROM evaluation_scenarios")).scalar()
            
            print(f"  Event categories: {cat_count}")
            print(f"  Event types: {type_count}")
            print(f"  Events: {event_count}")
            print(f"  Evaluation scenarios: {scenario_count}")
            
            print("\n" + "="*70)
            print("MIGRATION 005 COMPLETED SUCCESSFULLY")
            print("="*70 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return False


def downgrade() -> bool:
    """
    Rollback the migration.
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*70)
    print("ROLLBACK MIGRATION 005")
    print("="*70)
    
    with engine.connect() as conn:
        try:
            # Restore events columns
            print("\n[STEP 1] Restoring events table...")
            
            # Check if we need to restore
            old_col_exists = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'events' AND column_name = 'event_type'
                );
            """)).scalar()
            
            if not old_col_exists:
                # Add back string columns
                conn.execute(text("""
                    ALTER TABLE events ADD COLUMN event_type VARCHAR(50);
                    ALTER TABLE events ADD COLUMN event_category VARCHAR(30);
                """))
                
                # Populate from FK
                conn.execute(text("""
                    UPDATE events e
                    SET 
                        event_type = et.name,
                        event_category = ec.name
                    FROM event_types et
                    JOIN event_categories ec ON et.category_id = ec.id
                    WHERE e.event_type_id = et.id;
                """))
                
                # Drop FK and column
                conn.execute(text("""
                    ALTER TABLE events DROP CONSTRAINT IF EXISTS fk_events_event_type;
                    DROP INDEX IF EXISTS ix_events_event_type_id;
                    ALTER TABLE events DROP COLUMN IF EXISTS event_type_id;
                """))
                
                print("  -> Restored event_type and event_category columns")
            
            # Drop new tables
            print("\n[STEP 2] Dropping normalized tables...")
            conn.execute(text("DROP TABLE IF EXISTS event_types CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS event_categories CASCADE;"))
            print("  -> Dropped event_types and event_categories")
            
            # Note: We don't delete evaluation_scenarios as that data is valuable
            print("\n[NOTE] evaluation_scenarios data preserved")
            
            conn.commit()
            
            print("\n" + "="*70)
            print("ROLLBACK COMPLETED")
            print("="*70 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Rollback failed: {e}")
            conn.rollback()
            return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Migration 005: Normalize events + load scenarios')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    args = parser.parse_args()
    
    if args.rollback:
        success = downgrade()
    else:
        success = upgrade()
    
    exit(0 if success else 1)
