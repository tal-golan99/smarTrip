"""
Migration 003: Add Companies Table (Phase 1)
=============================================

This is a NON-BREAKING migration that:
1. Creates the companies table
2. Seeds 10 realistic travel company names
3. Adds company_id foreign key to existing trips table
4. Assigns all existing trips to a default company

This migration can be run independently without affecting existing functionality.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text
from datetime import datetime


# ============================================
# SEED DATA: 10 Realistic Travel Companies
# ============================================

SEED_COMPANIES = [
    {
        'name': 'Global Horizons Travel',
        'name_he': 'גלובל הורייזונס טיולים',
        'description': 'Specializing in worldwide adventure tours and cultural experiences since 1995.',
        'description_he': 'מתמחים בטיולי הרפתקאות וחוויות תרבותיות ברחבי העולם מאז 1995.',
        'website_url': 'https://globalhorizons.example.com',
        'email': 'info@globalhorizons.example.com',
    },
    {
        'name': 'Nature Path Expeditions',
        'name_he': 'נתיב הטבע מסעות',
        'description': 'Eco-friendly tours focused on wildlife, nature, and sustainable travel.',
        'description_he': 'טיולים ידידותיים לסביבה המתמקדים בחיות בר, טבע וטיולים ברי קיימא.',
        'website_url': 'https://naturepath.example.com',
        'email': 'contact@naturepath.example.com',
    },
    {
        'name': 'Heritage Journeys',
        'name_he': 'מסעות מורשת',
        'description': 'Cultural and historical tours exploring ancient civilizations and heritage sites.',
        'description_he': 'סיורים תרבותיים והיסטוריים לחקירת תרבויות עתיקות ואתרי מורשת.',
        'website_url': 'https://heritagejourneys.example.com',
        'email': 'tours@heritagejourneys.example.com',
    },
    {
        'name': 'Summit Adventures',
        'name_he': 'הרפתקאות הפסגה',
        'description': 'Mountain treks, hiking expeditions, and outdoor adventures for all skill levels.',
        'description_he': 'טרקים הרריים, מסעות טיול והרפתקאות חוץ לכל רמות הכושר.',
        'website_url': 'https://summitadv.example.com',
        'email': 'climb@summitadv.example.com',
    },
    {
        'name': 'Blue Ocean Cruises',
        'name_he': 'שייט האוקיינוס הכחול',
        'description': 'Premium cruise experiences combining luxury with exploration.',
        'description_he': 'חוויות שייט פרימיום המשלבות יוקרה עם חקירה.',
        'website_url': 'https://blueoceancruises.example.com',
        'email': 'sail@blueoceancruises.example.com',
    },
    {
        'name': 'Wanderlust World Tours',
        'name_he': 'וונדרלאסט סיורי עולם',
        'description': 'Group tours designed for curious travelers seeking authentic experiences.',
        'description_he': 'טיולים קבוצתיים המיועדים למטיילים סקרנים המחפשים חוויות אותנטיות.',
        'website_url': 'https://wanderlustworld.example.com',
        'email': 'explore@wanderlustworld.example.com',
    },
    {
        'name': 'Safari Dreams',
        'name_he': 'חלומות ספארי',
        'description': 'African wildlife safaris and nature experiences across the continent.',
        'description_he': 'ספארי חיות בר אפריקאיות וחוויות טבע ברחבי היבשת.',
        'website_url': 'https://safaridreams.example.com',
        'email': 'safari@safaridreams.example.com',
    },
    {
        'name': 'Eastern Winds Travel',
        'name_he': 'רוחות המזרח טיולים',
        'description': 'Specialized tours to Asia, from ancient temples to modern metropolises.',
        'description_he': 'טיולים מתמחים לאסיה, ממקדשים עתיקים ועד מטרופולינים מודרניים.',
        'website_url': 'https://easternwinds.example.com',
        'email': 'asia@easternwinds.example.com',
    },
    {
        'name': 'Polar Frontiers',
        'name_he': 'גבולות הקוטב',
        'description': 'Expedition cruises to Antarctica, the Arctic, and remote polar regions.',
        'description_he': 'שייטי משלחות לאנטארקטיקה, הארקטי ואזורים קוטביים מרוחקים.',
        'website_url': 'https://polarfrontiers.example.com',
        'email': 'expedition@polarfrontiers.example.com',
    },
    {
        'name': 'Caravan Routes',
        'name_he': 'שבילי השיירה',
        'description': 'Overland adventures following historic trade routes and ancient paths.',
        'description_he': 'הרפתקאות יבשתיות בעקבות מסלולי סחר היסטוריים ושבילים עתיקים.',
        'website_url': 'https://caravanroutes.example.com',
        'email': 'journey@caravanroutes.example.com',
    },
]


def upgrade() -> bool:
    """
    Run the Phase 1 migration: Add companies table.
    
    Steps:
    1. Create companies table
    2. Seed 10 companies
    3. Add company_id column to trips (nullable first)
    4. Set all existing trips to first company
    5. Make company_id NOT NULL
    6. Add foreign key constraint
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*70)
    print("MIGRATION 003: ADD COMPANIES TABLE (PHASE 1)")
    print("="*70)
    
    with engine.connect() as conn:
        try:
            # ----------------------------------------
            # Step 1: Create companies table
            # ----------------------------------------
            print("\n[STEP 1] Creating companies table...")
            
            # Check if table already exists
            check_sql = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'companies'
                );
            """)
            
            result = conn.execute(check_sql)
            table_exists = result.scalar()
            
            if table_exists:
                print("  -> companies table already exists, skipping creation")
            else:
                create_sql = text("""
                    CREATE TABLE companies (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        name_he VARCHAR(255) NOT NULL,
                        description TEXT,
                        description_he TEXT,
                        logo_url VARCHAR(500),
                        website_url VARCHAR(500),
                        email VARCHAR(255),
                        phone VARCHAR(50),
                        address TEXT,
                        is_active BOOLEAN DEFAULT TRUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                    );
                    
                    CREATE INDEX ix_companies_name ON companies(name);
                    CREATE INDEX ix_companies_is_active ON companies(is_active);
                """)
                conn.execute(create_sql)
                print("  -> companies table created successfully")
            
            # ----------------------------------------
            # Step 2: Seed companies
            # ----------------------------------------
            print("\n[STEP 2] Seeding companies...")
            
            for company in SEED_COMPANIES:
                # Check if company already exists
                check_company = text("SELECT id FROM companies WHERE name = :name")
                existing = conn.execute(check_company, {'name': company['name']}).fetchone()
                
                if existing:
                    print(f"  -> Company '{company['name']}' already exists, skipping")
                    continue
                
                insert_sql = text("""
                    INSERT INTO companies (name, name_he, description, description_he, website_url, email, is_active)
                    VALUES (:name, :name_he, :description, :description_he, :website_url, :email, TRUE)
                """)
                conn.execute(insert_sql, company)
                print(f"  -> Created company: {company['name']}")
            
            # ----------------------------------------
            # Step 3: Add company_id to trips table
            # ----------------------------------------
            print("\n[STEP 3] Adding company_id to trips table...")
            
            # Check if column already exists
            check_column = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'trips' AND column_name = 'company_id'
                );
            """)
            column_exists = conn.execute(check_column).scalar()
            
            if column_exists:
                print("  -> company_id column already exists, skipping")
            else:
                # Add nullable column first
                add_column = text("""
                    ALTER TABLE trips 
                    ADD COLUMN company_id INTEGER;
                """)
                conn.execute(add_column)
                print("  -> Added company_id column (nullable)")
                
                # ----------------------------------------
                # Step 4: Set all existing trips to first company
                # ----------------------------------------
                print("\n[STEP 4] Assigning existing trips to default company...")
                
                # Get first company ID
                get_first = text("SELECT id FROM companies ORDER BY id LIMIT 1")
                first_company = conn.execute(get_first).fetchone()
                
                if first_company:
                    default_company_id = first_company[0]
                    update_trips = text("""
                        UPDATE trips 
                        SET company_id = :company_id 
                        WHERE company_id IS NULL
                    """)
                    result = conn.execute(update_trips, {'company_id': default_company_id})
                    print(f"  -> Assigned {result.rowcount} trips to company ID {default_company_id}")
                
                # ----------------------------------------
                # Step 5: Make company_id NOT NULL
                # ----------------------------------------
                print("\n[STEP 5] Making company_id NOT NULL...")
                
                alter_not_null = text("""
                    ALTER TABLE trips 
                    ALTER COLUMN company_id SET NOT NULL;
                """)
                conn.execute(alter_not_null)
                print("  -> company_id is now NOT NULL")
                
                # ----------------------------------------
                # Step 6: Add foreign key constraint
                # ----------------------------------------
                print("\n[STEP 6] Adding foreign key constraint...")
                
                add_fk = text("""
                    ALTER TABLE trips 
                    ADD CONSTRAINT fk_trips_company 
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE RESTRICT;
                    
                    CREATE INDEX ix_trips_company_id ON trips(company_id);
                """)
                conn.execute(add_fk)
                print("  -> Foreign key constraint added")
            
            conn.commit()
            
            print("\n" + "="*70)
            print("MIGRATION 003 COMPLETED SUCCESSFULLY")
            print("="*70 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            conn.rollback()
            return False


def downgrade() -> bool:
    """
    Rollback the Phase 1 migration.
    
    WARNING: This will remove the company_id from trips and drop companies table.
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*70)
    print("ROLLBACK MIGRATION 003: REMOVE COMPANIES TABLE")
    print("="*70)
    
    with engine.connect() as conn:
        try:
            # Remove foreign key and column from trips
            print("\n[STEP 1] Removing company_id from trips...")
            
            drop_fk = text("""
                ALTER TABLE trips DROP CONSTRAINT IF EXISTS fk_trips_company;
                DROP INDEX IF EXISTS ix_trips_company_id;
                ALTER TABLE trips DROP COLUMN IF EXISTS company_id;
            """)
            conn.execute(drop_fk)
            print("  -> Removed company_id column and constraints")
            
            # Drop companies table
            print("\n[STEP 2] Dropping companies table...")
            
            drop_table = text("""
                DROP TABLE IF EXISTS companies CASCADE;
            """)
            conn.execute(drop_table)
            print("  -> Dropped companies table")
            
            conn.commit()
            
            print("\n" + "="*70)
            print("ROLLBACK COMPLETED SUCCESSFULLY")
            print("="*70 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Rollback failed: {e}")
            conn.rollback()
            return False


def get_companies_count() -> int:
    """Helper to check how many companies exist"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM companies"))
        return result.scalar()


if __name__ == '__main__':
    """Run migration directly"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run migration 003: Add Companies')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    args = parser.parse_args()
    
    if args.rollback:
        success = downgrade()
    else:
        success = upgrade()
    
    exit(0 if success else 1)
