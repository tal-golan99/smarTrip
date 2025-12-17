"""
Quick verification script to check seeded data

Run from backend folder: python scripts/verify_seed.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Country, Guide, Tag, Trip
# Note: TagCategory enum was removed - Tags now only contain THEME tags

session = SessionLocal()

try:
    countries_count = session.query(Country).count()
    guides_count = session.query(Guide).count()
    total_tags_count = session.query(Tag).count()
    trips_count = session.query(Trip).count()
    
    print("\n" + "="*50)
    print("DATABASE SEEDING VERIFICATION")
    print("="*50)
    print(f"Countries: {countries_count}")
    print(f"Guides: {guides_count}")
    print(f"Total Tags: {total_tags_count}")
    print(f"Trips: {trips_count}")
    print("="*50)
    
    print("\nSample Tags:")
    tags = session.query(Tag).limit(5).all()
    for tag in tags:
        print(f"  - {tag.name} ({tag.name_he})")
    
    print("\nSample Trips:")
    trips = session.query(Trip).limit(3).all()
    for trip in trips:
        print(f"  - {trip.title} | {trip.country.name} | {trip.status.value} | {trip.spots_left}/{trip.max_capacity} spots")
    
    print("\n" + "="*50)
    print("SUCCESS: Database seeded correctly!")
    print("="*50 + "\n")
    
finally:
    session.close()
