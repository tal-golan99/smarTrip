"""
Export Database to CSV Files
=============================
Exports all database data to CSV files for consistent seeding across environments.
"""

import csv
from database import SessionLocal
from models import Country, Guide, Tag, Trip, TripTag, TripType

def export_to_csv():
    """Export all database tables to CSV files"""
    
    session = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("EXPORTING DATABASE TO CSV FILES")
        print("="*70 + "\n")
        
        # Export Countries
        print("[1/5] Exporting Countries...")
        countries = session.query(Country).all()
        with open('data/countries.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'name_he', 'continent'])
            for c in countries:
                writer.writerow([
                    c.id,
                    c.name,
                    c.name_he,
                    c.continent.value if c.continent else ''
                ])
        print(f"   [OK] Exported {len(countries)} countries\n")
        
        # Export Trip Types
        print("[2/5] Exporting Trip Types...")
        trip_types = session.query(TripType).all()
        with open('data/trip_types.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'name_he', 'description'])
            for tt in trip_types:
                writer.writerow([
                    tt.id,
                    tt.name,
                    tt.name_he,
                    tt.description or ''
                ])
        print(f"   [OK] Exported {len(trip_types)} trip types\n")
        
        # Export Tags
        print("[3/5] Exporting Tags...")
        tags = session.query(Tag).all()
        with open('data/tags.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'name_he', 'description', 'category'])
            for tag in tags:
                writer.writerow([
                    tag.id,
                    tag.name,
                    tag.name_he,
                    tag.description or '',
                    tag.category.value if tag.category else ''
                ])
        print(f"   [OK] Exported {len(tags)} tags\n")
        
        # Export Guides
        print("[4/5] Exporting Guides...")
        guides = session.query(Guide).all()
        with open('data/guides.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'name_he', 'email', 'phone', 'gender', 'age', 'bio', 'bio_he', 'image_url'])
            for g in guides:
                writer.writerow([
                    g.id,
                    g.name,
                    g.name_he,
                    g.email or '',
                    g.phone or '',
                    g.gender.value if g.gender else '',
                    g.age or '',
                    g.bio.replace('\n', ' ') if g.bio else '',
                    g.bio_he.replace('\n', ' ') if g.bio_he else '',
                    g.image_url or ''
                ])
        print(f"   [OK] Exported {len(guides)} guides\n")
        
        # Export Trips
        print("[5/5] Exporting Trips...")
        trips = session.query(Trip).all()
        with open('data/trips.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'title', 'title_he', 'description', 'description_he',
                'image_url', 'start_date', 'end_date', 'price', 'single_supplement_price',
                'max_capacity', 'spots_left', 'status', 'difficulty_level',
                'country_id', 'guide_id', 'trip_type_id'
            ])
            for t in trips:
                writer.writerow([
                    t.id,
                    t.title,
                    t.title_he,
                    t.description.replace('\n', ' ') if t.description else '',
                    t.description_he.replace('\n', ' ') if t.description_he else '',
                    t.image_url or '',
                    t.start_date,
                    t.end_date,
                    t.price,
                    t.single_supplement_price,
                    t.max_capacity,
                    t.spots_left,
                    t.status.value if t.status else '',
                    t.difficulty_level,
                    t.country_id,
                    t.guide_id,
                    t.trip_type_id
                ])
        print(f"   [OK] Exported {len(trips)} trips\n")
        
        # Export Trip-Tag Relationships
        print("[6/6] Exporting Trip-Tag Relationships...")
        trip_tags = session.query(TripTag).all()
        with open('data/trip_tags.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['trip_id', 'tag_id'])
            for tt in trip_tags:
                writer.writerow([tt.trip_id, tt.tag_id])
        print(f"   [OK] Exported {len(trip_tags)} trip-tag relationships\n")
        
        print("="*70)
        print("EXPORT COMPLETE!")
        print("="*70)
        print(f"\nFiles created:")
        print(f"  - data/countries.csv ({len(countries)} rows)")
        print(f"  - data/trip_types.csv ({len(trip_types)} rows)")
        print(f"  - data/tags.csv ({len(tags)} rows)")
        print(f"  - data/guides.csv ({len(guides)} rows)")
        print(f"  - data/trips.csv ({len(trips)} rows)")
        print(f"  - data/trip_tags.csv ({len(trip_tags)} rows)")
        print("\n")
        
    finally:
        session.close()

if __name__ == '__main__':
    export_to_csv()
