"""
Verify that trip type names match between frontend and backend

Run from backend folder: python scripts/verify_names.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
# V2 Migration: Use V2 models
from models_v2 import TripType

# Frontend expected names
FRONTEND_NAMES = {
    1: ('Geographic Depth', 'טיולי עומק גיאוגרפיים'),
    2: ('Carnivals & Festivals', 'קרנבלים ופסטיבלים'),
    3: ('African Safari', 'ספארי באפריקה'),
    4: ('Train Tours', 'טיולי רכבות'),
    5: ('Geographic Cruises', 'טיולי שייט גיאוגרפיים'),
    6: ('Nature Hiking', 'טיולי הליכות בטבע'),
    8: ('Jeep Tours', 'טיולי ג\'יפים'),
    9: ('Snowmobile Tours', 'טיולי אופנועי שלג'),
    10: ('Private Groups', 'קבוצות סגורות'),
    11: ('Photography', 'טיולי צילום'),
}

session = SessionLocal()

try:
    print("\n" + "="*70)
    print("VERIFYING FRONTEND AND BACKEND NAMES MATCH")
    print("="*70 + "\n")
    
    trip_types = session.query(TripType).order_by(TripType.id).all()
    
    all_match = True
    
    for tt in trip_types:
        if tt.id in FRONTEND_NAMES:
            expected_name, expected_name_he = FRONTEND_NAMES[tt.id]
            
            name_match = tt.name == expected_name
            name_he_match = tt.name_he == expected_name_he
            
            if name_match and name_he_match:
                print(f"ID {tt.id}: MATCH")
                print(f"  EN: {tt.name}")
                print(f"  HE: {tt.name_he}")
            else:
                all_match = False
                print(f"ID {tt.id}: MISMATCH")
                if not name_match:
                    print(f"  EN Backend:  {tt.name}")
                    print(f"  EN Frontend: {expected_name}")
                if not name_he_match:
                    print(f"  HE Backend:  {tt.name_he}")
                    print(f"  HE Frontend: {expected_name_he}")
            print()
        else:
            print(f"ID {tt.id}: NOT IN FRONTEND")
            print(f"  {tt.name} ({tt.name_he})")
            print()
    
    # Check if frontend has IDs not in backend
    backend_ids = {tt.id for tt in trip_types}
    for frontend_id in FRONTEND_NAMES:
        if frontend_id not in backend_ids:
            print(f"WARNING: Frontend has ID {frontend_id} but backend doesn't!")
            print(f"  {FRONTEND_NAMES[frontend_id]}")
            print()
            all_match = False
    
    print("="*70)
    if all_match:
        print("SUCCESS: All names match perfectly!")
    else:
        print("WARNING: Some names don't match. Please fix.")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"ERROR: {e}")
    raise

finally:
    session.close()

