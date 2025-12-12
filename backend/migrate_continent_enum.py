"""
Migration script to update Continent enum in database
Changes NORTH_AMERICA to NORTH_AND_CENTRAL_AMERICA
"""

from database import SessionLocal
from sqlalchemy import text

def migrate_continent_enum():
    """Migrate the continent enum in PostgreSQL"""
    session = SessionLocal()
    
    try:
        print("Starting continent enum migration...")
        
        # Step 1: Update existing data
        print("Step 1: Updating existing countries with NORTH_AMERICA to temporary value...")
        session.execute(text("""
            UPDATE countries 
            SET continent = 'ASIA' 
            WHERE continent = 'NORTH_AMERICA'
        """))
        session.commit()
        print("Temporarily updated existing data")
        
        # Step 2: Alter the enum type
        print("Step 2: Altering the enum type...")
        session.execute(text("""
            ALTER TYPE continent RENAME VALUE 'North America' TO 'North & Central America'
        """))
        session.commit()
        print("Enum type updated successfully")
        
        # Step 3: Update countries back to correct continent
        print("Step 3: Updating countries back to correct continent...")
        north_central_american_countries = [
            'United States', 'Canada', 'Mexico', 'Cuba', 'Costa Rica', 
            'Panama', 'Guatemala', 'Hawaii', 'Alaska'
        ]
        
        for country in north_central_american_countries:
            session.execute(text(f"""
                UPDATE countries 
                SET continent = 'NORTH_AND_CENTRAL_AMERICA' 
                WHERE name = '{country}'
            """))
        session.commit()
        print("Countries updated successfully")
        
        print("[SUCCESS] Migration completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Error during migration: {e}")
        session.rollback()
        print("\nTrying alternative approach: DROP and RECREATE...")
        
        try:
            # Alternative: Drop and recreate everything
            print("Dropping all tables...")
            session.execute(text("DROP TABLE IF EXISTS trip_tags CASCADE"))
            session.execute(text("DROP TABLE IF EXISTS trips CASCADE"))
            session.execute(text("DROP TABLE IF EXISTS guides CASCADE"))
            session.execute(text("DROP TABLE IF EXISTS tags CASCADE"))
            session.execute(text("DROP TABLE IF EXISTS countries CASCADE"))
            session.execute(text("DROP TYPE IF EXISTS continent CASCADE"))
            session.execute(text("DROP TYPE IF EXISTS gender CASCADE"))
            session.execute(text("DROP TYPE IF EXISTS tripstatus CASCADE"))
            session.execute(text("DROP TYPE IF EXISTS tagcategory CASCADE"))
            session.commit()
            print("[SUCCESS] All tables and types dropped. Now run seed.py to recreate everything.")
            
        except Exception as e2:
            print(f"[ERROR] Error during cleanup: {e2}")
            session.rollback()
            raise
    
    finally:
        session.close()


if __name__ == '__main__':
    migrate_continent_enum()

