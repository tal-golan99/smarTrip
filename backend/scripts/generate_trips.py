"""
Generate 500 Trips with Proper Constraints
==========================================
- At least 10 trips per trip type
- More than 1 trip per country
- Tags correlate with geography and trip type
- Private Groups have special handling

Run from backend folder: python scripts/generate_trips.py
"""

import sys
import os
# Add backend folder to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
# V2 Migration: Use V2 models
from models_v2 import (
    Country, Guide, Tag, TripType, TripStatus, Continent,
    TripTemplate, TripOccurrence, TripTemplateTag, TripTemplateCountry, Company
)
from datetime import datetime, timedelta
import random

# Continent-to-Theme mapping
CONTINENT_THEME_MAPPING = {
    Continent.ASIA: ['Cultural & Historical', 'Mountain', 'Tropical', 'Food & Wine'],
    Continent.AFRICA: ['Wildlife', 'Desert', 'Cultural & Historical', 'Mountain'],
    Continent.EUROPE: ['Cultural & Historical', 'Food & Wine', 'Mountain', 'Arctic & Snow', 'Hanukkah & Christmas Lights'],
    Continent.OCEANIA: ['Beach & Island', 'Wildlife', 'Tropical', 'Mountain'],
    Continent.NORTH_AND_CENTRAL_AMERICA: ['Wildlife', 'Mountain', 'Beach & Island', 'Cultural & Historical', 'Desert'],
    Continent.SOUTH_AMERICA: ['Wildlife', 'Mountain', 'Tropical', 'Cultural & Historical', 'Desert'],
    Continent.ANTARCTICA: ['Arctic & Snow', 'Wildlife', 'Extreme'],
}

# Trip Type to Theme mapping
TYPE_TO_THEME_MAPPING = {
    'African Safari': ['Wildlife', 'Desert'],
    'Photography': ['Wildlife', 'Mountain', 'Cultural & Historical', 'Arctic & Snow', 'Desert'],
    'Snowmobile Tours': ['Arctic & Snow', 'Extreme'],
    'Nature Hiking': ['Mountain', 'Tropical', 'Wildlife'],
    'Jeep Tours': ['Desert', 'Mountain', 'Extreme'],
    'Train Tours': ['Cultural & Historical', 'Mountain'],
    'Geographic Cruises': ['Beach & Island', 'Arctic & Snow', 'Tropical'],
    'Carnivals & Festivals': ['Cultural & Historical', 'Food & Wine'],
    'Geographic Depth': ['Cultural & Historical', 'Mountain', 'Desert', 'Food & Wine'],
    'Private Groups': [],  # Can have any theme
}

# Hebrew title templates
HEBREW_TITLE_TEMPLATES = [
    'טיול מאורגן ל{}',
    'חוויה ב{}',
    'גלו את {}',
    'מסע ל{}',
    'טיול עומק ב{}',
]

# Hebrew descriptions by continent
HEBREW_DESCRIPTIONS = {
    Continent.ASIA: [
        'חווית טיול אסייתית מרתקת. גלו תרבויות עתיקות ונופים עוצרי נשימה.',
        'מסע אל לב אסיה. היסטוריה, תרבות וטבע במיטבם.',
        'טיול עומק באסיה. מקדשים, הרים וחוויות בלתי נשכחות.',
    ],
    Continent.AFRICA: [
        'הרפתקה אפריקאית אותנטית. חיות בר, נופים ותרבויות מרתקות.',
        'ספארי באפריקה. צפו בחיות הבר במלוא הדרן.',
        'מסע אל לב אפריקה. טבע פראי וחוויות בלתי נשכחות.',
    ],
    Continent.EUROPE: [
        'טיול אירופאי מושלם. היסטוריה, אמנות ותרבות במיטבם.',
        'גלו את אירופה. ערים מרהיבות, נופים עוצרי נשימה ואוכל משובח.',
        'מסע אירופאי בלתי נשכח. מהרי האלפים ועד חופי הים התיכון.',
    ],
    Continent.OCEANIA: [
        'הרפתקה באוקיאניה. איים טרופיים, חופים וטבע ייחודי.',
        'גלו את אוסטרליה וניו זילנד. נופים מדהימים וחיות בר ייחודיות.',
        'מסע לאיי האוקיינוס השקט. חופים לבנים ומים טורקיז.',
    ],
    Continent.NORTH_AND_CENTRAL_AMERICA: [
        'הרפתקה אמריקאית. מהרי הרוקי ועד חופי הקריביים.',
        'גלו את אמריקה הצפונית. ערים מרהיבות ופארקים לאומיים מדהימים.',
        'מסע במרכז אמריקה. תרבויות מאיה, טבע טרופי וחופים מושלמים.',
    ],
    Continent.SOUTH_AMERICA: [
        'הרפתקה בדרום אמריקה. מהאמזונס ועד פטגוניה.',
        'גלו את דרום אמריקה. תרבויות אינקה, נופים מדהימים וחיות בר ייחודיות.',
        'מסע אל לב אמריקה הלטינית. היסטוריה, תרבות וטבע במיטבם.',
    ],
    Continent.ANTARCTICA: [
        'משלחת לאנטארקטיקה. חווית פולר ייחודית במקום הקר ביותר בעולם.',
        'מסע אל יבשת הקרח. פינגווינים, קרחונים וטבע פראי במיטבו.',
        'הרפתקה אנטארקטית. גלו את היבשת האחרונה על פני כדור הארץ.',
    ],
}

# Type to country restrictions (from seed.py)
TYPE_TO_COUNTRY_LOGIC = {
    'African Safari': [
        'South Africa', 'Kenya', 'Tanzania', 'Uganda', 'Rwanda', 'Zimbabwe',
        'Namibia', 'Botswana', 'Zambia', 'Ethiopia', 'Madagascar'
    ],
    'Snowmobile Tours': [
        'Iceland', 'Norway', 'Scandinavia', 'Russia', 'Canada', 'Antarctica'
    ],
    'Train Tours': "ALL",
    'Carnivals & Festivals': "ALL",
    'Geographic Cruises': "ALL",
    'Geographic Depth': "ALL",
    'Nature Hiking': "ALL",
    'Jeep Tours': "ALL",
    'Photography': "ALL",
    'Private Groups': "ALL",
}

def generate_500_trips():
    """Generate exactly 500 trip templates with occurrences (V2 Schema)"""
    
    session = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("GENERATING 500 TRIP TEMPLATES WITH OCCURRENCES (V2 SCHEMA)")
        print("="*70 + "\n")
        
        # Load existing data
        print("[1/7] Loading existing data...")
        all_countries = session.query(Country).all()
        all_guides = session.query(Guide).all()
        all_trip_types = session.query(TripType).all()
        theme_tags = session.query(Tag).all()
        
        # Get or create default company
        default_company = session.query(Company).filter(Company.name == 'Ayala Geographic').first()
        if not default_company:
            default_company = Company(
                name='Ayala Geographic',
                name_he='איילה גיאוגרפית',
                description='Leading provider of niche travel experiences worldwide',
                description_he='ספקית מובילה לחוויית נסיעות נישה ברחבי העולם',
                is_active=True
            )
            session.add(default_company)
            session.commit()
        company_id = default_company.id
        
        print(f"  - {len(all_countries)} countries")
        print(f"  - {len(all_guides)} guides")
        print(f"  - {len(all_trip_types)} trip types")
        print(f"  - {len(theme_tags)} tags")
        print(f"  - Company ID: {company_id}\n")
        
        # Create lookup dictionaries
        country_by_name = {c.name: c for c in all_countries}
        tag_by_name = {t.name: t for t in theme_tags}
        
        # Track templates per type and country
        templates_per_type = {tt.id: 0 for tt in all_trip_types}
        templates_per_country = {c.id: 0 for c in all_countries}
        
        print("[2/7] Phase 1: Generating at least 50 templates per type (500 total)...\n")
        
        # Generate 50 trips per type (10 types × 50 = 500 trips)
        for trip_type in all_trip_types:
            type_name = trip_type.name
            country_restriction = TYPE_TO_COUNTRY_LOGIC.get(type_name, "ALL")
            
            # Get valid countries for this type
            if country_restriction == "ALL":
                valid_countries = all_countries
            else:
                valid_countries = [country_by_name[name] for name in country_restriction if name in country_by_name]
            
            if not valid_countries:
                print(f"  WARNING: No valid countries for {type_name}, skipping...")
                continue
            
            templates_to_generate = 50
            print(f"  [{type_name}] Generating {templates_to_generate} templates...")
            
            for _ in range(templates_to_generate):
                country = random.choice(valid_countries)
                guide = random.choice(all_guides)
                
                # Generate template/occurrence data
                is_private_group = (trip_type.id == 10)  # Private Groups
                
                # Date generation for occurrence
                if is_private_group:
                    start_date = datetime(2099, 12, 31).date()
                    end_date = datetime(2099, 12, 31).date()
                    duration_days = 1
                else:
                    days_from_now = random.randint(30, 540)  # 1-18 months
                    start_date = datetime.now().date() + timedelta(days=days_from_now)
                    duration_days = random.randint(5, 30)
                    end_date = start_date + timedelta(days=duration_days)
                
                # Price generation
                base_price = random.randint(200, 1500) * 10
                single_supplement = base_price * random.uniform(0.15, 0.25)
                
                # Capacity
                if is_private_group:
                    max_capacity = 0
                    spots_left = 0
                    status = 'Open'  # V2: status is string
                else:
                    max_capacity = random.choice([12, 15, 18, 20, 24, 25, 30])
                    spots_left = random.randint(0, max_capacity)
                    
                    if spots_left == 0:
                        status = 'Full'
                    elif spots_left <= 4:
                        status = 'Last Places'
                    elif spots_left >= max_capacity * 0.8:
                        status = 'Open'
                    else:
                        status = random.choice(['Guaranteed', 'Last Places', 'Open'])
                
                difficulty = random.randint(1, 3)
                
                # Titles
                template_title = random.choice(HEBREW_TITLE_TEMPLATES)
                title_he = template_title.format(country.name_he)
                title = f"Discover {country.name}"
                
                # Descriptions
                continent_descriptions_he = HEBREW_DESCRIPTIONS.get(country.continent, HEBREW_DESCRIPTIONS[Continent.ASIA])
                description_he = random.choice(continent_descriptions_he)
                description = f"Explore the wonders of {country.name}. An unforgettable journey awaits."
                
                # Tags: correlate with BOTH geography AND trip type
                continent_themes = CONTINENT_THEME_MAPPING.get(country.continent, [])
                type_themes = TYPE_TO_THEME_MAPPING.get(type_name, [])
                
                # Combine themes from continent and type
                combined_themes = list(set(continent_themes + type_themes))
                if combined_themes:
                    available_tags = [tag_by_name[name] for name in combined_themes if name in tag_by_name]
                else:
                    available_tags = theme_tags
                
                theme_tag_ids = []
                if available_tags:
                    num_themes = random.randint(1, min(3, len(available_tags)))
                    selected_themes = random.sample(available_tags, num_themes)
                    theme_tag_ids = [t.id for t in selected_themes]
                
                # V2: Create TripTemplate
                template = TripTemplate(
                    title=title,
                    title_he=title_he,
                    description=description,
                    description_he=description_he,
                    base_price=base_price,
                    single_supplement_price=single_supplement,
                    typical_duration_days=duration_days,
                    default_max_capacity=max_capacity,
                    difficulty_level=difficulty,
                    company_id=company_id,
                    trip_type_id=trip_type.id,
                    primary_country_id=country.id,
                    is_active=True
                )
                session.add(template)
                session.flush()
                
                # V2: Create TripOccurrence
                occurrence = TripOccurrence(
                    trip_template_id=template.id,
                    start_date=start_date,
                    end_date=end_date,
                    guide_id=guide.id,
                    status=status,
                    spots_left=spots_left,
                    max_capacity_override=None  # Use template default
                )
                session.add(occurrence)
                session.flush()
                
                # V2: Link country via TripTemplateCountry
                template_country = TripTemplateCountry(
                    trip_template_id=template.id,
                    country_id=country.id,
                    visit_order=1,
                    days_in_country=duration_days
                )
                session.add(template_country)
                
                # V2: Add tags via TripTemplateTag
                for tag_id in theme_tag_ids:
                    template_tag = TripTemplateTag(trip_template_id=template.id, tag_id=tag_id)
                    session.add(template_tag)
                
                templates_per_type[trip_type.id] += 1
                templates_per_country[country.id] += 1
        
        session.commit()
        
        print(f"\n[3/7] Phase 1 Complete!\n")
        
        # Verify
        print("[4/7] Verifying template distribution...\n")
        template_count = session.query(TripTemplate).count()
        occurrence_count = session.query(TripOccurrence).count()
        print(f"  Total templates generated: {template_count}")
        print(f"  Total occurrences generated: {occurrence_count}")
        
        print(f"\n  Templates per Type:")
        for trip_type in all_trip_types:
            count = session.query(TripTemplate).filter(TripTemplate.trip_type_id == trip_type.id).count()
            print(f"    - {trip_type.name}: {count} templates")
        
        countries_with_no_templates = [c for c in all_countries if templates_per_country[c.id] == 0]
        if countries_with_no_templates:
            print(f"\n  WARNING: {len(countries_with_no_templates)} countries have no templates")
        else:
            print(f"\n  SUCCESS: All {len(all_countries)} countries have at least 1 template")
        
        print(f"\n[5/7] Generation complete!")
        print(f"\n[6/7] Final Statistics:")
        print(f"  - Total Templates: {template_count}")
        print(f"  - Total Occurrences: {occurrence_count}")
        print(f"  - Countries covered: {len([c for c in all_countries if templates_per_country[c.id] > 0])}/{len(all_countries)}")
        print(f"  - Min templates per type: {min(templates_per_type.values())}")
        print(f"  - Max templates per type: {max(templates_per_type.values())}")
        
        print("\n[7/7] V2 Schema Migration Complete!")
        print("\n" + "="*70)
        print("TRIP GENERATION COMPLETED SUCCESSFULLY (V2 SCHEMA)")
        print("="*70 + "\n")
        
    except Exception as e:
        session.rollback()
        print(f"\nERROR: {str(e)}\n")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    generate_500_trips()

