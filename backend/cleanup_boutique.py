"""
Cleanup script to remove Boutique Tours from trip_types
and reassign its trips to Private Groups
"""

from database import SessionLocal
from models import TripType, Trip

session = SessionLocal()

try:
    print("\n" + "="*60)
    print("REMOVING BOUTIQUE TOURS")
    print("="*60 + "\n")
    
    # Find Boutique Tours
    boutique = session.query(TripType).filter(TripType.name == 'Boutique Tours').first()
    
    if not boutique:
        print("Boutique Tours already removed!")
    else:
        print(f"Found Boutique Tours (ID={boutique.id})")
        
        # Count trips
        trip_count = session.query(Trip).filter(Trip.trip_type_id == boutique.id).count()
        print(f"Trips with Boutique Tours: {trip_count}")
        
        if trip_count > 0:
            # Find Private Groups to reassign
            private_groups = session.query(TripType).filter(TripType.name == 'Private Groups').first()
            
            if private_groups:
                print(f"\nReassigning {trip_count} trips to 'Private Groups' (ID={private_groups.id})...")
                
                # Update all trips
                session.query(Trip).filter(Trip.trip_type_id == boutique.id).update(
                    {'trip_type_id': private_groups.id}
                )
                session.commit()
                print(f"SUCCESS: Reassigned {trip_count} trips")
            else:
                print("ERROR: Private Groups not found! Cannot reassign trips.")
                session.close()
                exit(1)
        
        # Delete Boutique Tours
        print(f"\nDeleting Boutique Tours (ID={boutique.id})...")
        session.delete(boutique)
        session.commit()
        print("SUCCESS: Deleted Boutique Tours")
    
    print("\n" + "="*60)
    print("CLEANUP COMPLETE")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\nERROR: {e}")
    session.rollback()
    raise

finally:
    session.close()

