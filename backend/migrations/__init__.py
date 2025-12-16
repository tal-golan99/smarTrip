"""
SmartTrip Database Migrations
=============================

Run migrations to update database schema.

Migrations:
- _001_add_recommendation_logging: Phase 0 logging tables
- _002_add_user_tracking: Phase 1 user tracking tables
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


# Alias the migration modules
try:
    from . import _001_add_recommendation_logging
    from . import _002_add_user_tracking
except ImportError:
    pass
