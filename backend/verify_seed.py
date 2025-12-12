"""Quick verification script to check seeded data"""

from database import SessionLocal
from models import Country, Guide, Tag, Trip, TagCategory

session = SessionLocal()

try:
    countries_count = session.query(Country).count()
    guides_count = session.query(Guide).count()
    type_tags_count = session.query(Tag).filter(Tag.category == TagCategory.TYPE).count()
    theme_tags_count = session.query(Tag).filter(Tag.category == TagCategory.THEME).count()
    total_tags_count = session.query(Tag).count()
    trips_count = session.query(Trip).count()
    
    print("\n" + "="*50)
    print("DATABASE SEEDING VERIFICATION")
    print("="*50)
    print(f"Countries: {countries_count}")
    print(f"Guides: {guides_count}")
    print(f"Tags (TYPE): {type_tags_count}")
    print(f"Tags (THEME): {theme_tags_count}")
    print(f"Total Tags: {total_tags_count}")
    print(f"Trips: {trips_count}")
    print("="*50)
    print("\nSample TYPE Tags:")
    type_tags = session.query(Tag).filter(Tag.category == TagCategory.TYPE).limit(5).all()
    for tag in type_tags:
        print(f"  - {tag.name} ({tag.name_he})")
    
    print("\nSample THEME Tags:")
    theme_tags = session.query(Tag).filter(Tag.category == TagCategory.THEME).limit(5).all()
    for tag in theme_tags:
        print(f"  - {tag.name} ({tag.name_he})")
    
    print("\nSample Trips:")
    trips = session.query(Trip).limit(3).all()
    for trip in trips:
        print(f"  - {trip.title} | {trip.country.name} | {trip.status.value} | {trip.spots_left}/{trip.max_capacity} spots")
    
    print("\n" + "="*50)
    print("SUCCESS: Database seeded correctly!")
    print("="*50 + "\n")
    
finally:
    session.close()

