"""
Database Seed Script - Import from CSV
=======================================
Imports consistent data from CSV files for identical seeding across environments.

Run from backend folder: python scripts/seed_from_csv.py
"""

import sys
import os
# Add backend folder to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
from datetime import datetime
from database import SessionLocal, init_db, drop_db
from models import Country, Guide, Tag, Trip, TripTag, TripType, Continent, Gender, TripStatus
# Note: TagCategory enum was removed - Tags now only contain THEME tags

def seed_from_csv():
    """Seed database by importing from CSV files"""
    
    print("\n" + "="*70)
    print("SMARTRIP DATABASE SEED - FROM CSV FILES")
    print("="*70 + "\n")
    
    # Drop and recreate tables
    drop_db()
    init_db()
    
    session = SessionLocal()
    
    try:
        # ============================================
        # IMPORT COUNTRIES FROM CSV
        # ============================================
        print("[IMPORTING] Countries from CSV...")
        
        with open('data/countries.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            countries_imported = 0
            for row in reader:
                country = Country(
                    id=int(row['id']),
                    name=row['name'],
                    name_he=row['name_he'],
                    continent=Continent(row['continent'])
                )
                session.add(country)
                countries_imported += 1
        
        session.commit()
        print(f"[OK] Imported {countries_imported} countries\n")
        
        # ============================================
        # IMPORT TRIP TYPES FROM CSV
        # ============================================
        print("[IMPORTING] Trip Types from CSV...")
        
        with open('data/trip_types.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            types_imported = 0
            for row in reader:
                trip_type = TripType(
                    id=int(row['id']),
                    name=row['name'],
                    name_he=row['name_he'],
                    description=row['description'] if row['description'] else None
                )
                session.add(trip_type)
                types_imported += 1
        
        session.commit()
        print(f"[OK] Imported {types_imported} trip types\n")
        
        # ============================================
        # IMPORT TAGS FROM CSV
        # ============================================
        print("[IMPORTING] Tags from CSV...")
        
        with open('data/tags.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            tags_imported = 0
            for row in reader:
                tag = Tag(
                    id=int(row['id']),
                    name=row['name'],
                    name_he=row['name_he'],
                    description=row['description'] if row['description'] else None
                    # Note: category column was removed from tags table
                )
                session.add(tag)
                tags_imported += 1
        
        session.commit()
        print(f"[OK] Imported {tags_imported} tags\n")
        
        # ============================================
        # IMPORT GUIDES FROM CSV
        # ============================================
        print("[IMPORTING] Guides from CSV...")
        
        with open('data/guides.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            guides_imported = 0
            for row in reader:
                guide = Guide(
                    id=int(row['id']),
                    name=row['name'],
                    name_he=row['name_he'],
                    email=row['email'] if row['email'] else None,
                    phone=row['phone'] if row['phone'] else None,
                    gender=Gender(row['gender']) if row['gender'] else None,
                    age=int(row['age']) if row['age'] else None,
                    bio=row['bio'] if row['bio'] else None,
                    bio_he=row['bio_he'] if row['bio_he'] else None,
                    image_url=row['image_url'] if row['image_url'] else None
                )
                session.add(guide)
                guides_imported += 1
        
        session.commit()
        print(f"[OK] Imported {guides_imported} guides\n")
        
        # ============================================
        # IMPORT TRIPS FROM CSV
        # ============================================
        print("[IMPORTING] Trips from CSV...")
        
        with open('data/trips.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            trips_imported = 0
            for row in reader:
                trip = Trip(
                    id=int(row['id']),
                    title=row['title'],
                    title_he=row['title_he'],
                    description=row['description'] if row['description'] else None,
                    description_he=row['description_he'] if row['description_he'] else None,
                    image_url=row['image_url'] if row['image_url'] else None,
                    start_date=datetime.strptime(row['start_date'], '%Y-%m-%d').date(),
                    end_date=datetime.strptime(row['end_date'], '%Y-%m-%d').date(),
                    price=float(row['price']),
                    single_supplement_price=float(row['single_supplement_price']),
                    max_capacity=int(row['max_capacity']),
                    spots_left=int(row['spots_left']),
                    status=TripStatus(row['status']),
                    difficulty_level=int(row['difficulty_level']),
                    country_id=int(row['country_id']),
                    guide_id=int(row['guide_id']),
                    trip_type_id=int(row['trip_type_id'])
                )
                session.add(trip)
                trips_imported += 1
                
                if trips_imported % 50 == 0:
                    print(f"  ... {trips_imported} trips imported")
        
        session.commit()
        print(f"[OK] Imported {trips_imported} trips\n")
        
        # ============================================
        # IMPORT TRIP-TAG RELATIONSHIPS FROM CSV
        # ============================================
        print("[IMPORTING] Trip-Tag relationships from CSV...")
        
        with open('data/trip_tags.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            relationships_imported = 0
            for row in reader:
                trip_tag = TripTag(
                    trip_id=int(row['trip_id']),
                    tag_id=int(row['tag_id'])
                )
                session.add(trip_tag)
                relationships_imported += 1
        
        session.commit()
        print(f"[OK] Imported {relationships_imported} trip-tag relationships\n")
        
        # ============================================
        # FINAL SUMMARY
        # ============================================
        country_count = session.query(Country).count()
        type_count = session.query(TripType).count()
        theme_count = session.query(Tag).count()
        guide_count = session.query(Guide).count()
        trip_count = session.query(Trip).count()
        
        print("="*70)
        print("DATABASE SEED FROM CSV COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"\nFinal Statistics:")
        print(f"   - Countries: {country_count}")
        print(f"   - Trip Types: {type_count}")
        print(f"   - Theme Tags: {theme_count}")
        print(f"   - Guides: {guide_count}")
        print(f"   - Trips: {trip_count}")
        
        print("\nSUCCESS: Database ready with consistent data!\n")
        
    except Exception as e:
        session.rollback()
        print(f"\nERROR: {str(e)}\n")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    seed_from_csv()

