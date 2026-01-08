"""
Quick script to check TripType IDs in the database

Run from backend folder: python scripts/check_types.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
# V2 Migration: Use V2 models - TripTemplate instead of Trip
from models_v2 import TripType, TripTemplate, Country

session = SessionLocal()

try:
    print("\n" + "="*60)
    print("TRIP TYPES IN DATABASE")
    print("="*60 + "\n")
    
    trip_types = session.query(TripType).order_by(TripType.id).all()
    
    for tt in trip_types:
        # V2: Count TripTemplates instead of Trips
        template_count = session.query(TripTemplate).filter(TripTemplate.trip_type_id == tt.id).count()
        print(f"ID {tt.id}: {tt.name} ({tt.name_he}) - {template_count} templates")
        
        # Show a few sample countries for this type
        sample_templates = session.query(TripTemplate).filter(TripTemplate.trip_type_id == tt.id).limit(5).all()
        if sample_templates:
            countries = []
            for template in sample_templates:
                # V2: Get primary country or first country from junction table
                if template.primary_country:
                    countries.append(template.primary_country.name)
                elif template.template_countries:
                    countries.append(template.template_countries[0].country.name)
            print(f"  Sample countries: {', '.join(countries)}")
        print()
    
    print("="*60)
    print("\nChecking ID 4 specifically:")
    type_4 = session.query(TripType).filter(TripType.id == 4).first()
    if type_4:
        print(f"ID 4 = {type_4.name} ({type_4.name_he})")
        
        # Check if there are templates in Canada with type_id=4
        canada = session.query(Country).filter(Country.name == 'Canada').first()
        if canada:
            # V2: Check TripTemplates with primary_country or via junction table
            canada_templates_type4 = session.query(TripTemplate).filter(
                TripTemplate.trip_type_id == 4,
                TripTemplate.primary_country_id == canada.id
            ).count()
            print(f"Templates with type_id=4 in Canada: {canada_templates_type4}")
    
    print("\nChecking African Safari:")
    safari = session.query(TripType).filter(TripType.name == 'African Safari').first()
    if safari:
        print(f"African Safari = ID {safari.id}")
        
finally:
    session.close()

