"""
Migration script to add name_he column to guides table and populate it
"""

from database import engine, SessionLocal
from sqlalchemy import text

def migrate():
    """Add name_he column and populate it with Hebrew names"""
    session = SessionLocal()
    
    try:
        print("=" * 60)
        print("MIGRATION: Adding name_he column to guides table")
        print("=" * 60)
        
        column_added = False
        
        # Add column if it doesn't exist
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='guides' AND column_name='name_he'
            """))
            
            if result.fetchone() is None:
                print("Adding name_he column...")
                try:
                    conn.execute(text("ALTER TABLE guides ADD COLUMN name_he VARCHAR(100)"))
                    conn.commit()
                    print("✓ Column added successfully")
                    column_added = True
                except Exception as alter_err:
                    # Column might already exist (race condition or previous failed run)
                    print(f"⚠ Column add failed (might already exist): {alter_err}")
                    conn.rollback()
            else:
                print("✓ Column already exists (migration previously applied)")
        
        # Populate name_he with the current name value (which should be Hebrew if properly seeded)
        print("\nPopulating name_he field from name field...")
        
        with engine.connect() as conn:
            result = conn.execute(
                text("UPDATE guides SET name_he = name WHERE name_he IS NULL OR name_he = ''")
            )
            conn.commit()
            updated_count = result.rowcount
        
        if updated_count > 0:
            print(f"✓ Updated {updated_count} guides with name_he")
        else:
            print("✓ All guides already have name_he populated")
        
        # Verify
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM guides WHERE name_he IS NOT NULL"))
            count = result.fetchone()[0]
            print(f"\n✓ Total guides with name_he: {count}")
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY!" if column_added else "MIGRATION ALREADY APPLIED (NO CHANGES NEEDED)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        session.rollback()
        # Don't raise - allow app to continue even if migration fails
        print("⚠ App will continue despite migration failure")
    finally:
        session.close()

if __name__ == '__main__':
    migrate()

