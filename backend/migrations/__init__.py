"""
SmartTrip Database Migrations
=============================

Run migrations to update database schema.

Migrations:
- _001_add_recommendation_logging: Phase 0 logging tables
- _002_add_user_tracking: Phase 1 user tracking tables
- _003_add_companies: Add companies table (Phase 1 of schema V2)
- _004_refactor_trips_to_templates: Refactor trips to templates + occurrences (Phase 2 of schema V2)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================
# PHASE 0: Recommendation Logging
# ============================================

def upgrade_logging_tables() -> bool:
    """
    Run the Phase 0 logging tables migration.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from migrations._001_add_recommendation_logging import upgrade
        return upgrade()
    except Exception as e:
        print(f"[MIGRATION] Error: {e}")
        return False


def downgrade_logging_tables() -> bool:
    """
    Rollback the Phase 0 logging tables migration.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from migrations._001_add_recommendation_logging import downgrade
        return downgrade()
    except Exception as e:
        print(f"[MIGRATION] Error: {e}")
        return False


# ============================================
# PHASE 1: User Tracking
# ============================================

def upgrade_user_tracking() -> bool:
    """
    Run the Phase 1 user tracking tables migration.
    
    Creates: users, sessions, events, trip_interactions tables.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from migrations._002_add_user_tracking import upgrade
        return upgrade()
    except Exception as e:
        print(f"[MIGRATION] Error: {e}")
        return False


def downgrade_user_tracking() -> bool:
    """
    Rollback the Phase 1 user tracking tables migration.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from migrations._002_add_user_tracking import downgrade
        return downgrade()
    except Exception as e:
        print(f"[MIGRATION] Error: {e}")
        return False


# ============================================
# SCHEMA V2: Companies (Phase 1)
# ============================================

def upgrade_companies() -> bool:
    """
    Run the Schema V2 Phase 1: Add companies table.
    
    Creates: companies table, adds company_id to trips.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from migrations._003_add_companies import upgrade
        return upgrade()
    except Exception as e:
        print(f"[MIGRATION] Error: {e}")
        return False


def downgrade_companies() -> bool:
    """
    Rollback the companies migration.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from migrations._003_add_companies import downgrade
        return downgrade()
    except Exception as e:
        print(f"[MIGRATION] Error: {e}")
        return False


# ============================================
# SCHEMA V2: Templates/Occurrences (Phase 2)
# ============================================

def upgrade_trip_templates() -> bool:
    """
    Run the Schema V2 Phase 2: Refactor trips to templates + occurrences.
    
    Creates: trip_templates, trip_occurrences, price_history, reviews, etc.
    
    IMPORTANT: Run upgrade_companies() BEFORE this migration!
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from migrations._004_refactor_trips_to_templates import upgrade
        return upgrade()
    except Exception as e:
        print(f"[MIGRATION] Error: {e}")
        return False


def downgrade_trip_templates() -> bool:
    """
    Rollback the templates/occurrences migration.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from migrations._004_refactor_trips_to_templates import downgrade
        return downgrade()
    except Exception as e:
        print(f"[MIGRATION] Error: {e}")
        return False


def verify_trip_templates() -> dict:
    """
    Verify the trip templates migration was successful.
    
    Returns:
        Dictionary with verification results
    """
    try:
        from migrations._004_refactor_trips_to_templates import verify_migration
        return verify_migration()
    except Exception as e:
        print(f"[MIGRATION] Error: {e}")
        return {'success': False, 'error': str(e)}


# ============================================
# ALL MIGRATIONS
# ============================================

def upgrade_all() -> bool:
    """
    Run all migrations in order.
    
    Returns:
        True if all successful, False otherwise
    """
    success = True
    
    # Phase 0
    print("\n[MIGRATIONS] Running Phase 0...")
    if not upgrade_logging_tables():
        success = False
    
    # Phase 1
    print("\n[MIGRATIONS] Running Phase 1...")
    if not upgrade_user_tracking():
        success = False
    
    return success


def upgrade_schema_v2() -> bool:
    """
    Run all Schema V2 migrations (Companies + Templates/Occurrences).
    
    This is a major schema change - backup your database first!
    
    Returns:
        True if all successful, False otherwise
    """
    success = True
    
    # Schema V2 Phase 1: Companies
    print("\n[MIGRATIONS] Running Schema V2 Phase 1 (Companies)...")
    if not upgrade_companies():
        success = False
        return success  # Don't continue if Phase 1 fails
    
    # Schema V2 Phase 2: Templates/Occurrences
    print("\n[MIGRATIONS] Running Schema V2 Phase 2 (Templates/Occurrences)...")
    if not upgrade_trip_templates():
        success = False
    
    return success


# Alias the migration modules
try:
    from . import _001_add_recommendation_logging
    from . import _002_add_user_tracking
    from . import _003_add_companies
    from . import _004_refactor_trips_to_templates
except ImportError:
    pass
