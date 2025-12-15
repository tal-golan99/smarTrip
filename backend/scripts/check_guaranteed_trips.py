"""
Check how many trips have GUARANTEED status

Run from backend folder: python scripts/check_guaranteed_trips.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Trip, TripStatus

session = SessionLocal()

try:
    print("\n" + "="*60)
    print("TRIP STATUS DISTRIBUTION")
    print("="*60 + "\n")
    
    for status in TripStatus:
        count = session.query(Trip).filter(Trip.status == status).count()
        print(f"{status.value}: {count} trips")
    
    print("\n" + "="*60)
    
    # Show some GUARANTEED trips
    guaranteed_trips = session.query(Trip).filter(Trip.status == TripStatus.GUARANTEED).limit(5).all()
    
    if guaranteed_trips:
        print(f"\nSample GUARANTEED trips:")
        for trip in guaranteed_trips:
            print(f"  - {trip.title_he} (ID={trip.id})")
    else:
        print("\nNo GUARANTEED trips found!")
        print("Run: python seed.py to regenerate trips with more variety")
    
    print()
    
except Exception as e:
    print(f"ERROR: {e}")
    raise

finally:
    session.close()

