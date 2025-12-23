"""
Migration 006: Add JSONB properties column to TripTemplates and TripOccurrences
===============================================================================

This migration adds extensible `properties` JSONB columns to support dynamic
metadata without requiring future schema migrations.

Use cases:
- packing_list: Specific gear for hiking vs. swimwear for cruises
- requirements: Vaccinations, visas, fitness level
- Type-specific attributes: cabin_type for cruises, jeep_model for safaris
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text


def upgrade() -> bool:
    """
    Add properties JSONB column to trip_templates and trip_occurrences.
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*70)
    print("MIGRATION 006: ADD PROPERTIES JSONB COLUMNS")
    print("="*70)
    
    with engine.connect() as conn:
        try:
            # ============================================
            # STEP 1: Add to trip_templates
            # ============================================
            print("\n[STEP 1] Adding properties column to trip_templates...")
            
            # Check if column already exists
            col_exists = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'trip_templates' AND column_name = 'properties'
                );
            """)).scalar()
            
            if col_exists:
                print("  -> Column already exists, skipping")
            else:
                conn.execute(text("""
                    ALTER TABLE trip_templates 
                    ADD COLUMN properties JSONB;
                    
                    COMMENT ON COLUMN trip_templates.properties IS 
                        'Extensible JSONB for dynamic metadata (packing_list, requirements, type-specific attributes)';
                """))
                print("  -> Added properties column to trip_templates")
            
            # ============================================
            # STEP 2: Add to trip_occurrences
            # ============================================
            print("\n[STEP 2] Adding properties column to trip_occurrences...")
            
            col_exists = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'trip_occurrences' AND column_name = 'properties'
                );
            """)).scalar()
            
            if col_exists:
                print("  -> Column already exists, skipping")
            else:
                conn.execute(text("""
                    ALTER TABLE trip_occurrences 
                    ADD COLUMN properties JSONB;
                    
                    COMMENT ON COLUMN trip_occurrences.properties IS 
                        'Extensible JSONB for occurrence-specific metadata (special_requirements, cabin_assignment)';
                """))
                print("  -> Added properties column to trip_occurrences")
            
            conn.commit()
            
            # ============================================
            # VERIFICATION
            # ============================================
            print("\n[VERIFICATION]")
            
            # Check columns exist
            templates_col = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'trip_templates' AND column_name = 'properties'
            """)).scalar()
            
            occurrences_col = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'trip_occurrences' AND column_name = 'properties'
            """)).scalar()
            
            print(f"  trip_templates.properties: {templates_col}")
            print(f"  trip_occurrences.properties: {occurrences_col}")
            
            if templates_col == 'jsonb' and occurrences_col == 'jsonb':
                print("\n" + "="*70)
                print("MIGRATION 006 COMPLETED SUCCESSFULLY")
                print("="*70 + "\n")
                return True
            else:
                print("\n[ERROR] Column verification failed")
                return False
            
        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return False


def downgrade() -> bool:
    """
    Remove properties columns.
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*70)
    print("ROLLBACK MIGRATION 006")
    print("="*70)
    
    with engine.connect() as conn:
        try:
            print("\n[STEP 1] Removing properties from trip_templates...")
            conn.execute(text("""
                ALTER TABLE trip_templates DROP COLUMN IF EXISTS properties;
            """))
            print("  -> Done")
            
            print("\n[STEP 2] Removing properties from trip_occurrences...")
            conn.execute(text("""
                ALTER TABLE trip_occurrences DROP COLUMN IF EXISTS properties;
            """))
            print("  -> Done")
            
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
    
    parser = argparse.ArgumentParser(description='Migration 006: Add properties JSONB columns')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    args = parser.parse_args()
    
    if args.rollback:
        success = downgrade()
    else:
        success = upgrade()
    
    exit(0 if success else 1)
