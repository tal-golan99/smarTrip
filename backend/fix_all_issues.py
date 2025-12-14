"""
Comprehensive fix script:
1. Check current status distribution
2. Fix Private Groups trips
3. Add more GUARANTEED trips
"""

from database import SessionLocal
from models import TripType, Trip, TripStatus
from datetime import datetime
import random

session = SessionLocal()

try:
    print("\n" + "="*70)
    print("COMPREHENSIVE DATABASE FIX")
    print("="*70 + "\n")
    
    # ============================================
    # CHECK 1: Current Status Distribution
    # ============================================
    print("[CHECK 1] Current Trip Status Distribution:")
    for status in TripStatus:
        count = session.query(Trip).filter(Trip.status == status).count()
        print(f"  {status.value}: {count} trips")
    
    print()
    
    # ============================================
    # FIX 1: Private Groups Trips
    # ============================================
    print("[FIX 1] Fixing Private Groups trips...")
    
    private_groups = session.query(TripType).filter(TripType.name == 'Private Groups').first()
    
    if private_groups:
        print(f"Found Private Groups (ID={private_groups.id})")
        
        trip_count = session.query(Trip).filter(Trip.trip_type_id == private_groups.id).count()
        print(f"Private Groups trips: {trip_count}")
        
        if trip_count > 0:
            updated = session.query(Trip).filter(Trip.trip_type_id == private_groups.id).update({
                'start_date': datetime(2099, 12, 31).date(),
                'end_date': datetime(2099, 12, 31).date(),
                'max_capacity': 0,
                'spots_left': 0,
                'status': TripStatus.OPEN
            }, synchronize_session=False)
            
            session.commit()
            print(f"SUCCESS: Updated {updated} Private Groups trips")
            print("  - Start/End date: 2099-12-31")
            print("  - Capacity: 0")
            print("  - Status: OPEN")
        else:
            print("WARNING: No Private Groups trips found!")
    else:
        print("ERROR: Private Groups trip type not found!")
    
    print()
    
    # ============================================
    # FIX 2: Add More GUARANTEED Trips
    # ============================================
    print("[FIX 2] Increasing GUARANTEED trip count...")
    
    # Get current GUARANTEED count
    guaranteed_count = session.query(Trip).filter(Trip.status == TripStatus.GUARANTEED).count()
    print(f"Current GUARANTEED trips: {guaranteed_count}")
    
    # Target: at least 50 GUARANTEED trips
    target = 50
    
    if guaranteed_count < target:
        # Get OPEN trips that we can convert to GUARANTEED
        open_trips = session.query(Trip).filter(
            Trip.status == TripStatus.OPEN,
            Trip.trip_type_id != private_groups.id if private_groups else True,  # Exclude Private Groups
            Trip.spots_left > 8  # Only convert trips with decent capacity
        ).limit(target - guaranteed_count).all()
        
        converted = 0
        for trip in open_trips:
            trip.status = TripStatus.GUARANTEED
            converted += 1
        
        session.commit()
        print(f"SUCCESS: Converted {converted} OPEN trips to GUARANTEED")
        
        new_guaranteed_count = session.query(Trip).filter(Trip.status == TripStatus.GUARANTEED).count()
        print(f"New GUARANTEED trip count: {new_guaranteed_count}")
    else:
        print(f"Already have {guaranteed_count} GUARANTEED trips (target: {target})")
    
    print()
    
    # ============================================
    # FINAL STATUS CHECK
    # ============================================
    print("="*70)
    print("FINAL STATUS DISTRIBUTION")
    print("="*70 + "\n")
    
    for status in TripStatus:
        count = session.query(Trip).filter(Trip.status == status).count()
        print(f"  {status.value}: {count} trips")
    
    print()
    
    # Show sample GUARANTEED trips
    guaranteed_trips = session.query(Trip).filter(Trip.status == TripStatus.GUARANTEED).limit(5).all()
    if guaranteed_trips:
        print("Sample GUARANTEED trips:")
        for trip in guaranteed_trips:
            print(f"  - {trip.title_he} (ID={trip.id}, Type ID={trip.trip_type_id})")
    
    print()
    
    # Check Private Groups trips
    if private_groups:
        pg_trips = session.query(Trip).filter(Trip.trip_type_id == private_groups.id).limit(3).all()
        if pg_trips:
            print("Sample Private Groups trips:")
            for trip in pg_trips:
                print(f"  - {trip.title_he}")
                print(f"    Date: {trip.start_date}, Capacity: {trip.max_capacity}, Status: {trip.status.value}")
    
    print()
    print("="*70)
    print("ALL FIXES COMPLETE!")
    print("="*70 + "\n")
    print("Next steps:")
    print("1. Restart backend: python app.py")
    print("2. Test Private Groups: http://localhost:3000/search/results?type=10")
    print("3. Search for trips and look for 'יציאה מובטחת' badges")
    print()
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    session.rollback()
    raise

finally:
    session.close()

