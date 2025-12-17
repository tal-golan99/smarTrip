"""
Run V2 Schema Migration for Production
=======================================

This script runs the necessary migrations to set up the V2 schema:
- Migration 003: Creates companies table
- Migration 004: Creates trip_templates, trip_occurrences, and related tables

Usage:
    python run_v2_migration.py

This can also be called via HTTP by adding a route to app.py.
"""

import os
import sys

# Ensure we can import from the backend directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()


def run_migrations():
    """Run V2 schema migrations in order."""
    results = {}
    
    print("\n" + "="*70)
    print("V2 SCHEMA MIGRATION RUNNER")
    print("="*70)
    
    # Migration 003: Companies
    print("\n[1/2] Running Migration 003: Add Companies...")
    try:
        from migrations._003_add_companies import upgrade as upgrade_003
        success = upgrade_003()
        results['003_companies'] = 'SUCCESS' if success else 'FAILED'
    except Exception as e:
        print(f"  ERROR: {e}")
        results['003_companies'] = f'ERROR: {e}'
    
    # Migration 004: Templates/Occurrences
    print("\n[2/2] Running Migration 004: Templates/Occurrences...")
    try:
        from migrations._004_refactor_trips_to_templates import upgrade as upgrade_004
        success = upgrade_004()
        results['004_templates'] = 'SUCCESS' if success else 'FAILED'
    except Exception as e:
        print(f"  ERROR: {e}")
        results['004_templates'] = f'ERROR: {e}'
    
    # Summary
    print("\n" + "="*70)
    print("MIGRATION SUMMARY")
    print("="*70)
    for migration, status in results.items():
        print(f"  {migration}: {status}")
    
    all_success = all(s == 'SUCCESS' for s in results.values())
    print("\n" + ("ALL MIGRATIONS COMPLETED SUCCESSFULLY!" if all_success else "SOME MIGRATIONS FAILED - CHECK LOGS"))
    print("="*70 + "\n")
    
    return all_success, results


if __name__ == '__main__':
    success, results = run_migrations()
    sys.exit(0 if success else 1)

