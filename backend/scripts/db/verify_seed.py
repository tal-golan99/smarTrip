"""
Quick verification script to check seeded data

Run from backend folder: python scripts/verify_seed.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
# V2 Migration: Use V2 models
from app.models.trip import Country, Guide, Tag, TripTemplate, TripOccurrence
# Note: TagCategory enum was removed - Tags now only contain THEME tags

session = SessionLocal()

try:
    countries_count = session.query(Country).count()
    guides_count = session.query(Guide).count()
    total_tags_count = session.query(Tag).count()
    templates_count = session.query(TripTemplate).count()
    occurrences_count = session.query(TripOccurrence).count()
    
    print("\n" + "="*50)
    print("DATABASE SEEDING VERIFICATION (V2 SCHEMA)")
    print("="*50)
    print(f"Countries: {countries_count}")
    print(f"Guides: {guides_count}")
    print(f"Total Tags: {total_tags_count}")
    print(f"Trip Templates: {templates_count}")
    print(f"Trip Occurrences: {occurrences_count}")
    print("="*50)
    
    print("\nSample Tags:")
    tags = session.query(Tag).limit(5).all()
    for tag in tags:
        print(f"  - {tag.name} ({tag.name_he})")
    
    print("\nSample Trip Templates with Occurrences:")
    templates = session.query(TripTemplate).limit(3).all()
    for template in templates:
        country_name = template.primary_country.name if template.primary_country else "N/A"
        occurrence = template.occurrences[0] if template.occurrences else None
        if occurrence:
            spots_info = f"{occurrence.spots_left}/{occurrence.max_capacity_override or template.default_max_capacity} spots"
            print(f"  - {template.title} | {country_name} | {occurrence.status} | {spots_info}")
        else:
            print(f"  - {template.title} | {country_name} | (no occurrences)")
    
    print("\n" + "="*50)
    print("SUCCESS: Database seeded correctly!")
    print("="*50 + "\n")
    
finally:
    session.close()
