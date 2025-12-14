"""
Fix existing Private Groups trips to have:
- No date (2099-12-31)
- 0 participants
- OPEN status
"""

from database import SessionLocal
from models import TripType, Trip, TripStatus
from datetime import datetime

session = SessionLocal()

try:
    print("\n" + "="*60)
    print("FIXING PRIVATE GROUPS TRIPS")
    print("="*60 + "\n")
    
    # Find Private Groups trip type
    private_groups = session.query(TripType).filter(TripType.name == 'Private Groups').first()
    
    if not private_groups:
        print("Private Groups trip type not found!")
    else:
        print(f"Found Private Groups (ID={private_groups.id})")
        
        # Count trips
        trip_count = session.query(Trip).filter(Trip.trip_type_id == private_groups.id).count()
        print(f"Private Groups trips: {trip_count}")
        
        if trip_count > 0:
            # Update all Private Groups trips
            updated = session.query(Trip).filter(Trip.trip_type_id == private_groups.id).update({
                'start_date': datetime(2099, 12, 31).date(),
                'end_date': datetime(2099, 12, 31).date(),
                'max_capacity': 0,
                'spots_left': 0,
                'status': TripStatus.OPEN
            }, synchronize_session=False)
            
            session.commit()
            print(f"\nSUCCESS: Updated {updated} Private Groups trips")
            print("  - Start/End date: 2099-12-31 (no fixed date)")
            print("  - Capacity: 0 (entire group booking)")
            print("  - Status: OPEN")
        else:
            print("No Private Groups trips to update")
    
    print("\n" + "="*60)
    print("FIX COMPLETE")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\nERROR: {e}")
    session.rollback()
    raise

finally:
    session.close()

