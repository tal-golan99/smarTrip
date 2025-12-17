"""
Verification Script for TripType Schema Refactoring
Checks if the Type-to-Country logic is correctly applied

Run from backend folder: python scripts/verify_schema.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Trip, TripType, Country, Tag
# Note: TagCategory enum was removed
from sqlalchemy import func

def verify_schema():
    """Verify the schema refactoring was successful"""
    
    print("\n" + "="*70)
    print("SCHEMA VERIFICATION")
    print("="*70 + "\n")
    
    session = SessionLocal()
    
    try:
        # ============================================
        # CHECK 1: Trip Types Table
        # ============================================
        print("[CHECK 1] Trip Types Table")
        trip_types = session.query(TripType).order_by(TripType.id).all()
        print(f"Total Trip Types: {len(trip_types)}")
        for tt in trip_types:
            trip_count = session.query(Trip).filter(Trip.trip_type_id == tt.id).count()
            print(f"  ID {tt.id}: {tt.name} ({tt.name_he}) - {trip_count} trips")
        print()
        
        # ============================================
        # CHECK 2: Tags (All are now theme tags)
        # ============================================
        print("[CHECK 2] Tags (category column removed - all tags are theme tags)")
        all_tags = session.query(Tag).order_by(Tag.id).all()
        print(f"Total Tags: {len(all_tags)}")
        for tag in all_tags:
            print(f"  ID {tag.id}: {tag.name} ({tag.name_he})")
        print()
        
        # ============================================
        # CHECK 3: All Trips Have TripType
        # ============================================
        print("[CHECK 3] Trips with TripType")
        total_trips = session.query(Trip).count()
        trips_with_type = session.query(Trip).filter(Trip.trip_type_id != None).count()
        trips_without_type = session.query(Trip).filter(Trip.trip_type_id == None).count()
        
        print(f"Total Trips: {total_trips}")
        print(f"Trips with TripType: {trips_with_type}")
        print(f"Trips without TripType: {trips_without_type}")
        
        if trips_without_type > 0:
            print("\nWARNING: Some trips don't have a TripType!")
        else:
            print("\nSUCCESS: All trips have a TripType")
        print()
        
        # ============================================
        # CHECK 4: Countries Coverage
        # ============================================
        print("[CHECK 4] Countries Coverage")
        total_countries = session.query(Country).count()
        
        # Countries with trips
        countries_with_trips = session.query(Country.id).join(Trip).distinct().count()
        
        print(f"Total Countries: {total_countries}")
        print(f"Countries with Trips: {countries_with_trips}")
        print(f"Countries without Trips: {total_countries - countries_with_trips}")
        
        if countries_with_trips < total_countries:
            # Show which countries have no trips
            countries_without_trips = session.query(Country).filter(
                ~Country.id.in_(
                    session.query(Trip.country_id).distinct()
                )
            ).order_by(Country.name).all()
            print("\nCountries without trips:")
            for country in countries_without_trips[:10]:  # Show first 10
                print(f"  - {country.name} ({country.name_he})")
            if len(countries_without_trips) > 10:
                print(f"  ... and {len(countries_without_trips) - 10} more")
        else:
            print("\nSUCCESS: All countries have at least one trip")
        print()
        
        # ============================================
        # CHECK 5: Geographical Logic Verification
        # ============================================
        print("[CHECK 5] Geographical Logic Verification")
        print("Checking if trip types match their designated countries...\n")
        
        # Define the logic map (same as in seed.py)
        TYPE_TO_COUNTRY_LOGIC = {
            "African Safari": ["Kenya", "Tanzania", "South Africa", "Namibia", "Botswana", "Uganda", "Rwanda"],
            "Snowmobile Tours": ["Iceland", "Lapland", "Norway", "Canada", "Greenland", "Russia", "Antarctica"],
            "Jeep Tours": ["Jordan", "Morocco", "Namibia", "Kyrgyzstan", "Georgia", "Mongolia", "Oman", "Tunisia", "Bolivia", "Israel"],
            "Train Tours": ["Switzerland", "Japan", "India", "Russia", "Scotland", "Norway", "Peru", "Canada", "Austria", "Italy"],
            "Geographic Cruises": ["Antarctica", "Norway", "Vietnam", "Greece", "Croatia", "Iceland", "Chile", "Argentina"],
            "Carnivals & Festivals": ["Brazil", "Bolivia", "Peru", "Spain", "Italy", "India", "Japan", "Thailand", "Mexico", "Cuba"],
        }
        
        violations = []
        
        for type_name, allowed_countries in TYPE_TO_COUNTRY_LOGIC.items():
            trip_type = session.query(TripType).filter(TripType.name == type_name).first()
            if not trip_type:
                continue
            
            # Get all trips of this type
            trips = session.query(Trip).filter(Trip.trip_type_id == trip_type.id).all()
            
            for trip in trips:
                country = session.query(Country).filter(Country.id == trip.country_id).first()
                if country and country.name not in allowed_countries:
                    violations.append({
                        'trip_id': trip.id,
                        'trip_type': type_name,
                        'country': country.name,
                        'allowed': allowed_countries
                    })
        
        if violations:
            print(f"WARNING: Found {len(violations)} geographical logic violations:")
            for v in violations[:5]:  # Show first 5
                print(f"  - Trip ID {v['trip_id']}: {v['trip_type']} in {v['country']}")
                print(f"    (Allowed: {', '.join(v['allowed'][:5])}...)")
            if len(violations) > 5:
                print(f"  ... and {len(violations) - 5} more violations")
        else:
            print("SUCCESS: No geographical logic violations found!")
            print("All restricted trip types are in their designated countries.")
        print()
        
        # ============================================
        # CHECK 6: Antarctica Check
        # ============================================
        print("[CHECK 6] Antarctica Verification")
        antarctica = session.query(Country).filter(Country.name == 'Antarctica').first()
        if antarctica:
            antarctica_trips = session.query(Trip).filter(Trip.country_id == antarctica.id).count()
            print(f"Antarctica exists: ID={antarctica.id}")
            print(f"Trips to Antarctica: {antarctica_trips}")
            if antarctica_trips > 0:
                print("SUCCESS: Antarctica has trips!")
            else:
                print("INFO: Antarctica has no trips yet")
        else:
            print("WARNING: Antarctica not found in database!")
        print()
        
        # ============================================
        # CHECK 7: Sample Data
        # ============================================
        print("[CHECK 7] Sample Trips with TripType")
        sample_trips = session.query(Trip).limit(5).all()
        for trip in sample_trips:
            trip_type = session.query(TripType).filter(TripType.id == trip.trip_type_id).first()
            country = session.query(Country).filter(Country.id == trip.country_id).first()
            print(f"  Trip ID {trip.id}: {trip.title_he}")
            print(f"    Type: {trip_type.name if trip_type else 'None'}")
            print(f"    Country: {country.name if country else 'None'}")
            print()
        
        # ============================================
        # SUMMARY
        # ============================================
        print("="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)
        print(f"Trip Types: {len(trip_types)}")
        print(f"Theme Tags: {len(theme_tags)}")
        print(f"Total Trips: {total_trips}")
        print(f"Countries: {total_countries}")
        print(f"Countries with Trips: {countries_with_trips}")
        if violations:
            print(f"Geographical Violations: {len(violations)} (needs attention)")
        else:
            print(f"Geographical Violations: 0 (perfect)")
        print()
        
        if trips_without_type == 0 and type_tags == 0 and countries_with_trips == total_countries and len(violations) == 0:
            print("SUCCESS: All checks passed! Database is ready for production.")
        else:
            print("WARNING: Some checks failed. Review the issues above.")
        print()
        
    except Exception as e:
        print(f"\nERROR during verification: {e}")
        raise
    
    finally:
        session.close()


if __name__ == '__main__':
    verify_schema()

