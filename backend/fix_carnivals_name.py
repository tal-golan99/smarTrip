"""
Fix Carnivals & Festivals Hebrew name in database
"""

from database import SessionLocal
from models import TripType

session = SessionLocal()

try:
    print("Updating Carnivals & Festivals Hebrew name...")
    
    carnivals = session.query(TripType).filter(TripType.name == 'Carnivals & Festivals').first()
    
    if carnivals:
        old_name = carnivals.name_he
        carnivals.name_he = 'קרנבלים ופסטיבלים'
        session.commit()
        print(f"SUCCESS: Updated from '{old_name}' to '{carnivals.name_he}'")
    else:
        print("Carnivals & Festivals type not found!")
    
except Exception as e:
    print(f"ERROR: {e}")
    session.rollback()
    raise

finally:
    session.close()

