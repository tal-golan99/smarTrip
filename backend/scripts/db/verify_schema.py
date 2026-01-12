"""
Verification Script for TripType Schema Refactoring
Checks if the Type-to-Country logic is correctly applied

Run from backend folder: python scripts/verify_schema.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
# V2 Migration: Use V2 models
from models_v2 import TripTemplate, TripOccurrence, TripType, Country, Tag, TripTemplateCountry
# Note: TagCategory enum was removed
from sqlalchemy import func, or_

def verify_schema():
    """Verify the schema refactoring was successful"""
    
    print("\n" + "="*70)
    print("SCHEMA VERIFICATION")
    print("="*70 + "\n")
    
    session = SessionLocal()
    
    try:
        # ============================================
        # CHECK 1: Trip Types Table
        # ============================================
        print("[CHECK 1] Trip Types Table")
        trip_types = session.query(TripType).order_by(TripType.id).all()
        print(f"Total Trip Types: {len(trip_types)}")
        for tt in trip_types:
            # V2: Count TripTemplates instead of Trips
            template_count = session.query(TripTemplate).filter(TripTemplate.trip_type_id == tt.id).count()
            print(f"  ID {tt.id}: {tt.name} ({tt.name_he}) - {template_count} templates")
        print()
        
        # ============================================
        # CHECK 2: Tags (All are now theme tags)
        # ============================================
        print("[CHECK 2] Tags (category column removed - all tags are theme tags)")
        all_tags = session.query(Tag).order_by(Tag.id).all()
        theme_tags = all_tags  # All tags are theme tags in V2
        print(f"Total Tags: {len(all_tags)}")
        for tag in all_tags:
            print(f"  ID {tag.id}: {tag.name} ({tag.name_he})")
        print()
        
        # ============================================
        # CHECK 3: All Templates Have TripType
        # ============================================
        print("[CHECK 3] TripTemplates with TripType")
        total_templates = session.query(TripTemplate).count()
        templates_with_type = session.query(TripTemplate).filter(TripTemplate.trip_type_id != None).count()
        templates_without_type = session.query(TripTemplate).filter(TripTemplate.trip_type_id == None).count()
        
        print(f"Total Templates: {total_templates}")
        print(f"Templates with TripType: {templates_with_type}")
        print(f"Templates without TripType: {templates_without_type}")
        
        if templates_without_type > 0:
            print("\nWARNING: Some templates don't have a TripType!")
        else:
            print("\nSUCCESS: All templates have a TripType")
        print()
        
        # ============================================
        # CHECK 4: Countries Coverage
        # ============================================
        print("[CHECK 4] Countries Coverage")
        total_countries = session.query(Country).count()
        
        # V2: Countries with templates (via primary_country_id or junction table)
        countries_with_templates = session.query(Country.id).filter(
            or_(
                Country.id.in_(session.query(TripTemplate.primary_country_id).distinct()),
                Country.id.in_(session.query(TripTemplateCountry.country_id).distinct())
            )
        ).distinct().count()
        
        print(f"Total Countries: {total_countries}")
        print(f"Countries with Templates: {countries_with_templates}")
        print(f"Countries without Templates: {total_countries - countries_with_templates}")
        
        if countries_with_templates < total_countries:
            # Show which countries have no templates
            # Get IDs from primary_country_id
            primary_country_ids = [row[0] for row in session.query(TripTemplate.primary_country_id).filter(
                TripTemplate.primary_country_id != None
            ).distinct().all()]
            # Get IDs from junction table
            junction_country_ids = [row[0] for row in session.query(TripTemplateCountry.country_id).distinct().all()]
            countries_with_templates_ids = set(primary_country_ids) | set(junction_country_ids)
            countries_without_templates = session.query(Country).filter(
                ~Country.id.in_(list(countries_with_templates_ids))
            ).order_by(Country.name).all()
            print("\nCountries without templates:")
            for country in countries_without_templates[:10]:  # Show first 10
                print(f"  - {country.name} ({country.name_he})")
            if len(countries_without_templates) > 10:
                print(f"  ... and {len(countries_without_templates) - 10} more")
        else:
            print("\nSUCCESS: All countries have at least one template")
        print()
        
        # ============================================
        # CHECK 5: Geographical Logic Verification
        # ============================================
        print("[CHECK 5] Geographical Logic Verification")
        print("Checking if trip types match their designated countries...\n")
        
        # Define the logic map (same as in seed.py)
        TYPE_TO_COUNTRY_LOGIC = {
            "African Safari": ["Kenya", "Tanzania", "South Africa", "Namibia", "Botswana", "Uganda", "Rwanda"],
            "Snowmobile Tours": ["Iceland", "Lapland", "Norway", "Canada", "Greenland", "Russia", "Antarctica"],
            "Jeep Tours": ["Jordan", "Morocco", "Namibia", "Kyrgyzstan", "Georgia", "Mongolia", "Oman", "Tunisia", "Bolivia", "Israel"],
            "Train Tours": ["Switzerland", "Japan", "India", "Russia", "Scotland", "Norway", "Peru", "Canada", "Austria", "Italy"],
            "Geographic Cruises": ["Antarctica", "Norway", "Vietnam", "Greece", "Croatia", "Iceland", "Chile", "Argentina"],
            "Carnivals & Festivals": ["Brazil", "Bolivia", "Peru", "Spain", "Italy", "India", "Japan", "Thailand", "Mexico", "Cuba"],
        }
        
        violations = []
        
        for type_name, allowed_countries in TYPE_TO_COUNTRY_LOGIC.items():
            trip_type = session.query(TripType).filter(TripType.name == type_name).first()
            if not trip_type:
                continue
            
            # V2: Get all templates of this type
            templates = session.query(TripTemplate).filter(TripTemplate.trip_type_id == trip_type.id).all()
            
            for template in templates:
                # Check primary country
                country = template.primary_country
                if country and country.name not in allowed_countries:
                    violations.append({
                        'template_id': template.id,
                        'trip_type': type_name,
                        'country': country.name,
                        'allowed': allowed_countries
                    })
        
        if violations:
            print(f"WARNING: Found {len(violations)} geographical logic violations:")
            for v in violations[:5]:  # Show first 5
                print(f"  - Trip ID {v['trip_id']}: {v['trip_type']} in {v['country']}")
                print(f"    (Allowed: {', '.join(v['allowed'][:5])}...)")
            if len(violations) > 5:
                print(f"  ... and {len(violations) - 5} more violations")
        else:
            print("SUCCESS: No geographical logic violations found!")
            print("All restricted trip types are in their designated countries.")
        print()
        
        # ============================================
        # CHECK 6: Antarctica Check
        # ============================================
        print("[CHECK 6] Antarctica Verification")
        antarctica = session.query(Country).filter(Country.name == 'Antarctica').first()
        if antarctica:
            # V2: Count templates with Antarctica as primary country
            antarctica_templates = session.query(TripTemplate).filter(
                TripTemplate.primary_country_id == antarctica.id
            ).count()
            print(f"Antarctica exists: ID={antarctica.id}")
            print(f"Templates to Antarctica: {antarctica_templates}")
            if antarctica_templates > 0:
                print("SUCCESS: Antarctica has templates!")
            else:
                print("INFO: Antarctica has no templates yet")
        else:
            print("WARNING: Antarctica not found in database!")
        print()
        
        # ============================================
        # CHECK 7: Sample Data
        # ============================================
        print("[CHECK 7] Sample Templates with TripType")
        sample_templates = session.query(TripTemplate).limit(5).all()
        for template in sample_templates:
            trip_type = template.trip_type
            country = template.primary_country
            print(f"  Template ID {template.id}: {template.title_he}")
            print(f"    Type: {trip_type.name if trip_type else 'None'}")
            print(f"    Country: {country.name if country else 'None'}")
            print(f"    Occurrences: {len(template.occurrences)}")
            print()
        
        # ============================================
        # SUMMARY
        # ============================================
        print("="*70)
        print("VERIFICATION SUMMARY (V2 SCHEMA)")
        print("="*70)
        print(f"Trip Types: {len(trip_types)}")
        print(f"Theme Tags: {len(theme_tags)}")
        print(f"Total Templates: {total_templates}")
        print(f"Countries: {total_countries}")
        print(f"Countries with Templates: {countries_with_templates}")
        if violations:
            print(f"Geographical Violations: {len(violations)} (needs attention)")
        else:
            print(f"Geographical Violations: 0 (perfect)")
        print()
        
        if templates_without_type == 0 and countries_with_templates == total_countries and len(violations) == 0:
            print("SUCCESS: All checks passed! Database is ready for production.")
        else:
            print("WARNING: Some checks failed. Review the issues above.")
        print()
        
    except Exception as e:
        print(f"\nERROR during verification: {e}")
        raise
    
    finally:
        session.close()


if __name__ == '__main__':
    verify_schema()

