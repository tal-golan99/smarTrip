"""
Export Database to CSV Files
=============================
Exports all database data to CSV files for consistent seeding across environments.

Run from backend folder: python scripts/export_data.py
"""

import sys
import os
# Add backend folder to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
from database import SessionLocal
# V2 Migration: Use V2 models
from models_v2 import (
    Country, Guide, Tag, TripType,
    TripTemplate, TripOccurrence, TripTemplateTag, TripTemplateCountry, Company
)

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
            # V2: category column removed - all tags are theme tags
            writer.writerow(['id', 'name', 'name_he', 'description'])
            for tag in tags:
                writer.writerow([
                    tag.id,
                    tag.name,
                    tag.name_he,
                    tag.description or ''
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
        
        # Export Companies (V2)
        print("[5/7] Exporting Companies...")
        companies = session.query(Company).all()
        with open('data/companies.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'name_he', 'description', 'description_he', 'is_active'])
            for c in companies:
                writer.writerow([
                    c.id,
                    c.name,
                    c.name_he,
                    c.description.replace('\n', ' ') if c.description else '',
                    c.description_he.replace('\n', ' ') if c.description_he else '',
                    c.is_active
                ])
        print(f"   [OK] Exported {len(companies)} companies\n")
        
        # Export Trip Templates (V2)
        print("[6/7] Exporting Trip Templates...")
        templates = session.query(TripTemplate).all()
        with open('data/trip_templates.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'title', 'title_he', 'description', 'description_he',
                'image_url', 'base_price', 'single_supplement_price',
                'typical_duration_days', 'default_max_capacity', 'difficulty_level',
                'company_id', 'trip_type_id', 'primary_country_id', 'is_active'
            ])
            for t in templates:
                writer.writerow([
                    t.id,
                    t.title,
                    t.title_he,
                    t.description.replace('\n', ' ') if t.description else '',
                    t.description_he.replace('\n', ' ') if t.description_he else '',
                    t.image_url or '',
                    t.base_price,
                    t.single_supplement_price or '',
                    t.typical_duration_days,
                    t.default_max_capacity,
                    t.difficulty_level,
                    t.company_id,
                    t.trip_type_id or '',
                    t.primary_country_id or '',
                    t.is_active
                ])
        print(f"   [OK] Exported {len(templates)} trip templates\n")
        
        # Export Trip Occurrences (V2)
        print("[7/7] Exporting Trip Occurrences...")
        occurrences = session.query(TripOccurrence).all()
        with open('data/trip_occurrences.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'trip_template_id', 'start_date', 'end_date',
                'guide_id', 'status', 'spots_left',
                'price_override', 'single_supplement_override', 'max_capacity_override'
            ])
            for o in occurrences:
                writer.writerow([
                    o.id,
                    o.trip_template_id,
                    o.start_date,
                    o.end_date,
                    o.guide_id or '',
                    o.status,
                    o.spots_left,
                    o.price_override or '',
                    o.single_supplement_override or '',
                    o.max_capacity_override or ''
                ])
        print(f"   [OK] Exported {len(occurrences)} trip occurrences\n")
        
        # Export Template-Tag Relationships (V2)
        print("[8/8] Exporting Template-Tag Relationships...")
        template_tags = session.query(TripTemplateTag).all()
        with open('data/trip_template_tags.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['trip_template_id', 'tag_id'])
            for tt in template_tags:
                writer.writerow([tt.trip_template_id, tt.tag_id])
        print(f"   [OK] Exported {len(template_tags)} template-tag relationships\n")
        
        # Export Template-Country Relationships (V2)
        print("[9/9] Exporting Template-Country Relationships...")
        template_countries = session.query(TripTemplateCountry).all()
        with open('data/trip_template_countries.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['trip_template_id', 'country_id', 'visit_order', 'days_in_country'])
            for tc in template_countries:
                writer.writerow([
                    tc.trip_template_id,
                    tc.country_id,
                    tc.visit_order,
                    tc.days_in_country or ''
                ])
        print(f"   [OK] Exported {len(template_countries)} template-country relationships\n")
        
        print("="*70)
        print("EXPORT COMPLETE! (V2 SCHEMA)")
        print("="*70)
        print(f"\nFiles created:")
        print(f"  - data/countries.csv ({len(countries)} rows)")
        print(f"  - data/trip_types.csv ({len(trip_types)} rows)")
        print(f"  - data/tags.csv ({len(tags)} rows)")
        print(f"  - data/guides.csv ({len(guides)} rows)")
        print(f"  - data/companies.csv ({len(companies)} rows)")
        print(f"  - data/trip_templates.csv ({len(templates)} rows)")
        print(f"  - data/trip_occurrences.csv ({len(occurrences)} rows)")
        print(f"  - data/trip_template_tags.csv ({len(template_tags)} rows)")
        print(f"  - data/trip_template_countries.csv ({len(template_countries)} rows)")
        print("\n")
        
    finally:
        session.close()

if __name__ == '__main__':
    export_to_csv()
