"""
Check how many trips have GUARANTEED status

Run from backend folder: python scripts/check_guaranteed_trips.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
# V2 Migration: Use V2 models - TripOccurrence has status
from models_v2 import TripOccurrence, TripStatus

session = SessionLocal()

try:
    print("\n" + "="*60)
    print("TRIP STATUS DISTRIBUTION")
    print("="*60 + "\n")
    
    for status in TripStatus:
        # V2: Status is stored as string in TripOccurrence
        status_str = status.value if hasattr(status, 'value') else str(status)
        count = session.query(TripOccurrence).filter(TripOccurrence.status == status_str).count()
        print(f"{status_str}: {count} occurrences")
    
    print("\n" + "="*60)
    
    # Show some GUARANTEED occurrences
    guaranteed_status = TripStatus.GUARANTEED.value if hasattr(TripStatus.GUARANTEED, 'value') else 'Guaranteed'
    guaranteed_occurrences = session.query(TripOccurrence).filter(
        TripOccurrence.status == guaranteed_status
    ).limit(5).all()
    
    if guaranteed_occurrences:
        print(f"\nSample GUARANTEED occurrences:")
        for occ in guaranteed_occurrences:
            template = occ.template
            print(f"  - {template.title_he if template else 'N/A'} (Occurrence ID={occ.id})")
    else:
        print("\nNo GUARANTEED trips found!")
        print("Run: python seed.py to regenerate trips with more variety")
    
    print()
    
except Exception as e:
    print(f"ERROR: {e}")
    raise

finally:
    session.close()

