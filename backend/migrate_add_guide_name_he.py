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
                conn.execute(text("ALTER TABLE guides ADD COLUMN name_he VARCHAR(100)"))
                conn.commit()
                print("✓ Column added successfully")
            else:
                print("✓ Column already exists")
        
        # Populate name_he with the current name value (which should be Hebrew if properly seeded)
        print("\nPopulating name_he field from name field...")
        
        with engine.connect() as conn:
            result = conn.execute(
                text("UPDATE guides SET name_he = name WHERE name_he IS NULL")
            )
            conn.commit()
            updated_count = result.rowcount
        
        print(f"✓ Updated {updated_count} guides with name_he")
        
        # Verify
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM guides WHERE name_he IS NOT NULL"))
            count = result.fetchone()[0]
            print(f"\n✓ Total guides with name_he: {count}")
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == '__main__':
    migrate()

