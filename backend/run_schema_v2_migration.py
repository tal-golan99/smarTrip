"""
Schema V2 Migration Runner
==========================

This script runs the Schema V2 database migrations:
1. Phase 1: Add Companies table
2. Phase 2: Refactor trips to Templates + Occurrences

IMPORTANT: Backup your database before running this migration!

Usage:
    python run_schema_v2_migration.py                    # Run all migrations
    python run_schema_v2_migration.py --phase1-only     # Run Phase 1 only
    python run_schema_v2_migration.py --rollback        # Rollback all migrations
    python run_schema_v2_migration.py --verify          # Verify migration status
    python run_schema_v2_migration.py --backup          # Create backup first
"""

import os
import sys
import argparse
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_backup():
    """Create a database backup before migration"""
    from database import engine
    from sqlalchemy import text
    
    print("\n" + "="*70)
    print("CREATING DATABASE BACKUP")
    print("="*70)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with engine.connect() as conn:
        try:
            # Get list of tables to backup
            tables_to_backup = ['trips', 'trip_tags', 'countries', 'guides', 'trip_types', 'tags']
            
            for table in tables_to_backup:
                backup_name = f"{table}_backup_{timestamp}"
                
                # Check if table exists
                exists = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    );
                """)).scalar()
                
                if exists:
                    conn.execute(text(f"CREATE TABLE {backup_name} AS SELECT * FROM {table};"))
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {backup_name}")).scalar()
                    print(f"  Backed up {table} -> {backup_name} ({count} rows)")
                else:
                    print(f"  Skipping {table} (doesn't exist)")
            
            conn.commit()
            print(f"\nBackup completed with timestamp: {timestamp}")
            print("You can restore from these tables if needed.\n")
            return True
            
        except Exception as e:
            print(f"Backup failed: {e}")
            conn.rollback()
            return False


def run_phase1():
    """Run Phase 1: Companies table"""
    from migrations import upgrade_companies
    return upgrade_companies()


def run_phase2():
    """Run Phase 2: Templates/Occurrences"""
    from migrations import upgrade_trip_templates
    return upgrade_trip_templates()


def rollback_phase2():
    """Rollback Phase 2"""
    from migrations import downgrade_trip_templates
    return downgrade_trip_templates()


def rollback_phase1():
    """Rollback Phase 1"""
    from migrations import downgrade_companies
    return downgrade_companies()


def verify_migration():
    """Verify migration status"""
    from migrations import verify_trip_templates
    from database import engine
    from sqlalchemy import text
    
    print("\n" + "="*70)
    print("MIGRATION VERIFICATION")
    print("="*70)
    
    with engine.connect() as conn:
        # Check companies
        companies_exists = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'companies'
            );
        """)).scalar()
        
        print(f"\n[Phase 1] Companies table exists: {'YES' if companies_exists else 'NO'}")
        
        if companies_exists:
            company_count = conn.execute(text("SELECT COUNT(*) FROM companies")).scalar()
            print(f"  -> {company_count} companies")
        
        # Check templates
        templates_exists = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'trip_templates'
            );
        """)).scalar()
        
        print(f"\n[Phase 2] Trip templates table exists: {'YES' if templates_exists else 'NO'}")
        
        if templates_exists:
            results = verify_trip_templates()
            
            print("\nVerification Checks:")
            for check in results.get('checks', []):
                status = "PASS" if check['passed'] else "FAIL"
                print(f"  [{status}] {check['check']}")
            
            print("\nTable Counts:")
            for table, count in results.get('stats', {}).items():
                print(f"  {table}: {count} rows")
            
            return results.get('success', False)
        
        return companies_exists


def main():
    parser = argparse.ArgumentParser(
        description='Run Schema V2 database migrations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_schema_v2_migration.py                 # Run all migrations
  python run_schema_v2_migration.py --backup        # Backup then migrate
  python run_schema_v2_migration.py --phase1-only   # Companies only
  python run_schema_v2_migration.py --verify        # Check status
  python run_schema_v2_migration.py --rollback      # Undo migrations
        """
    )
    
    parser.add_argument('--phase1-only', action='store_true',
                        help='Run Phase 1 only (Companies table)')
    parser.add_argument('--phase2-only', action='store_true',
                        help='Run Phase 2 only (requires Phase 1)')
    parser.add_argument('--rollback', action='store_true',
                        help='Rollback all Schema V2 migrations')
    parser.add_argument('--rollback-phase2', action='store_true',
                        help='Rollback Phase 2 only')
    parser.add_argument('--verify', action='store_true',
                        help='Verify migration status')
    parser.add_argument('--backup', action='store_true',
                        help='Create backup before migration')
    parser.add_argument('--yes', '-y', action='store_true',
                        help='Skip confirmation prompts')
    
    args = parser.parse_args()
    
    # Verify mode
    if args.verify:
        success = verify_migration()
        return 0 if success else 1
    
    # Rollback mode
    if args.rollback:
        if not args.yes:
            confirm = input("\nThis will rollback all Schema V2 migrations. Continue? (y/N): ")
            if confirm.lower() != 'y':
                print("Aborted.")
                return 1
        
        print("\nRolling back Schema V2...")
        rollback_phase2()
        rollback_phase1()
        print("\nRollback complete.")
        return 0
    
    if args.rollback_phase2:
        if not args.yes:
            confirm = input("\nThis will rollback Phase 2 (Templates/Occurrences). Continue? (y/N): ")
            if confirm.lower() != 'y':
                print("Aborted.")
                return 1
        
        success = rollback_phase2()
        return 0 if success else 1
    
    # Migration mode
    if not args.yes:
        print("\n" + "="*70)
        print("SCHEMA V2 MIGRATION")
        print("="*70)
        print("\nThis will make significant changes to your database:")
        print("  - Phase 1: Add companies table")
        print("  - Phase 2: Refactor trips to templates + occurrences")
        print("\nIt is STRONGLY recommended to backup your database first.")
        
        if args.backup:
            print("\n[--backup flag detected: Will create backup before migration]")
        
        confirm = input("\nContinue with migration? (y/N): ")
        if confirm.lower() != 'y':
            print("Aborted.")
            return 1
    
    # Create backup if requested
    if args.backup:
        if not create_backup():
            print("Backup failed! Aborting migration.")
            return 1
    
    # Run migrations
    success = True
    
    if args.phase1_only:
        success = run_phase1()
    elif args.phase2_only:
        success = run_phase2()
    else:
        # Run both phases
        print("\nRunning Phase 1 (Companies)...")
        if not run_phase1():
            print("\nPhase 1 failed! Aborting.")
            return 1
        
        print("\nRunning Phase 2 (Templates/Occurrences)...")
        if not run_phase2():
            print("\nPhase 2 failed!")
            success = False
    
    if success:
        print("\n" + "="*70)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nNext steps:")
        print("  1. Run --verify to check migration status")
        print("  2. Update your application code to use new models")
        print("  3. Test thoroughly before going to production")
        print("  4. Drop backup tables when confident: trips_backup_v2, trip_tags_backup_v2")
    else:
        print("\n" + "="*70)
        print("MIGRATION FAILED")
        print("="*70)
        print("\nCheck the error messages above.")
        print("You can use --rollback to undo changes.")
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
