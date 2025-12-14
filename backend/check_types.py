"""
Quick script to check TripType IDs in the database
"""

from database import SessionLocal
from models import TripType, Trip, Country

session = SessionLocal()

try:
    print("\n" + "="*60)
    print("TRIP TYPES IN DATABASE")
    print("="*60 + "\n")
    
    trip_types = session.query(TripType).order_by(TripType.id).all()
    
    for tt in trip_types:
        trip_count = session.query(Trip).filter(Trip.trip_type_id == tt.id).count()
        print(f"ID {tt.id}: {tt.name} ({tt.name_he}) - {trip_count} trips")
        
        # Show a few sample countries for this type
        sample_trips = session.query(Trip).filter(Trip.trip_type_id == tt.id).limit(5).all()
        if sample_trips:
            countries = []
            for trip in sample_trips:
                country = session.query(Country).filter(Country.id == trip.country_id).first()
                if country:
                    countries.append(country.name)
            print(f"  Sample countries: {', '.join(countries)}")
        print()
    
    print("="*60)
    print("\nChecking ID 4 specifically:")
    type_4 = session.query(TripType).filter(TripType.id == 4).first()
    if type_4:
        print(f"ID 4 = {type_4.name} ({type_4.name_he})")
        
        # Check if there are trips in Canada with type_id=4
        canada = session.query(Country).filter(Country.name == 'Canada').first()
        if canada:
            canada_trips_type4 = session.query(Trip).filter(
                Trip.trip_type_id == 4,
                Trip.country_id == canada.id
            ).count()
            print(f"Trips with type_id=4 in Canada: {canada_trips_type4}")
    
    print("\nChecking African Safari:")
    safari = session.query(TripType).filter(TripType.name == 'African Safari').first()
    if safari:
        print(f"African Safari = ID {safari.id}")
        
finally:
    session.close()

