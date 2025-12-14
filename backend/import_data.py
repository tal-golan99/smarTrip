"""
Import Database from CSV Files
===============================
Imports all database tables from CSV files for consistent deployment.
"""

import csv
from database import SessionLocal, init_db, drop_db
from models import Country, Guide, Tag, Trip, TripTag, TripType, Continent, Gender, TripStatus, TagCategory
from datetime import datetime, date
import os

def import_database():
    """Import all database tables from CSV files"""
    
    print("\n" + "="*70)
    print("IMPORTING DATABASE FROM CSV FILES")
    print("="*70 + "\n")
    
    # Check if data directory exists
    if not os.path.exists('data'):
        print("ERROR: 'data' directory not found!")
        print("Please run export_data.py first to create CSV files.\n")
        return
    
    # Drop existing tables and recreate
    print("[SETUP] Dropping existing tables...")
    drop_db()
    print("[SETUP] Creating fresh tables...")
    init_db()
    print()
    
    session = SessionLocal()
    
    try:
        # ============================================
        # IMPORT COUNTRIES
        # ============================================
        print("[IMPORT] Countries...")
        with open('data/countries.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            countries = []
            for row in reader:
                country = Country(
                    id=int(row['id']),
                    name=row['name'],
                    name_he=row['name_he'],
                    continent=Continent(row['continent'])
                )
                countries.append(country)
            session.bulk_save_objects(countries)
            session.commit()
        print(f"  > Imported {len(countries)} countries\n")
        
        # ============================================
        # IMPORT TRIP TYPES
        # ============================================
        print("[IMPORT] Trip Types...")
        with open('data/trip_types.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            trip_types = []
            for row in reader:
                trip_type = TripType(
                    id=int(row['id']),
                    name=row['name'],
                    name_he=row['name_he'],
                    description=row['description']
                )
                trip_types.append(trip_type)
            session.bulk_save_objects(trip_types)
            session.commit()
        print(f"  > Imported {len(trip_types)} trip types\n")
        
        # ============================================
        # IMPORT TAGS
        # ============================================
        print("[IMPORT] Tags...")
        with open('data/tags.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            tags = []
            for row in reader:
                tag = Tag(
                    id=int(row['id']),
                    name=row['name'],
                    name_he=row['name_he'],
                    description=row['description'],
                    category=TagCategory(row['category'])
                )
                tags.append(tag)
            session.bulk_save_objects(tags)
            session.commit()
        print(f"  > Imported {len(tags)} tags\n")
        
        # ============================================
        # IMPORT GUIDES
        # ============================================
        print("[IMPORT] Guides...")
        with open('data/guides.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            guides = []
            for row in reader:
                guide = Guide(
                    id=int(row['id']),
                    name=row['name'],
                    name_he=row['name_he'],
                    bio=row['bio'],
                    bio_he=row['bio_he'],
                    image_url=row['image_url'],
                    gender=Gender(row['gender'])
                )
                guides.append(guide)
            session.bulk_save_objects(guides)
            session.commit()
        print(f"  > Imported {len(guides)} guides\n")
        
        # ============================================
        # IMPORT TRIPS
        # ============================================
        print("[IMPORT] Trips...")
        with open('data/trips.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            trips = []
            for row in reader:
                trip = Trip(
                    id=int(row['id']),
                    title=row['title'],
                    title_he=row['title_he'],
                    description=row['description'],
                    description_he=row['description_he'],
                    image_url=row['image_url'],
                    start_date=date.fromisoformat(row['start_date']),
                    end_date=date.fromisoformat(row['end_date']),
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
                trips.append(trip)
            session.bulk_save_objects(trips)
            session.commit()
        print(f"  > Imported {len(trips)} trips\n")
        
        # ============================================
        # IMPORT TRIP-TAG RELATIONSHIPS
        # ============================================
        print("[IMPORT] Trip-Tag relationships...")
        with open('data/trip_tags.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            trip_tags = []
            for row in reader:
                trip_tag = TripTag(
                    trip_id=int(row['trip_id']),
                    tag_id=int(row['tag_id'])
                )
                trip_tags.append(trip_tag)
            session.bulk_save_objects(trip_tags)
            session.commit()
        print(f"  > Imported {len(trip_tags)} trip-tag relationships\n")
        
        print("="*70)
        print("IMPORT COMPLETE!")
        print("="*70)
        print(f"\nDatabase loaded with:")
        print(f"  - {len(countries)} countries")
        print(f"  - {len(trip_types)} trip types")
        print(f"  - {len(tags)} tags")
        print(f"  - {len(guides)} guides")
        print(f"  - {len(trips)} trips")
        print(f"  - {len(trip_tags)} trip-tag relationships")
        print("\n")
        
    except Exception as e:
        print(f"\nERROR during import: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    import_database()

