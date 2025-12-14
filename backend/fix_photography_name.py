"""
Fix Photography Hebrew name in database
"""

from database import SessionLocal
from models import TripType

session = SessionLocal()

try:
    print("Updating Photography Hebrew name...")
    
    photography = session.query(TripType).filter(TripType.name == 'Photography').first()
    
    if photography:
        old_name = photography.name_he
        photography.name_he = 'טיולי צילום'
        session.commit()
        print(f"SUCCESS: Updated from '{old_name}' to '{photography.name_he}'")
    else:
        print("Photography type not found!")
    
except Exception as e:
    print(f"ERROR: {e}")
    session.rollback()
    raise

finally:
    session.close()

