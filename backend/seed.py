"""
Database Seed Script with TripType Foreign Key Logic
=====================================================
Populates the database with realistic data using the new TripType model
and strict Type-to-Country mapping for geographical accuracy.
"""

from database import SessionLocal, init_db
from models import Country, Guide, Tag, Trip, TripTag, TripType, Continent, Gender, TripStatus, TagCategory
from faker import Faker
from datetime import datetime, timedelta
import random
import csv
import os

# Initialize Faker for Hebrew and English
fake_he = Faker('he_IL')
fake_en = Faker('en_US')


# ============================================
# TYPE TO COUNTRY LOGIC MAP
# ============================================
TYPE_TO_COUNTRY_LOGIC = {
    "Geographic Depth": "ALL",  # Can go anywhere
    "African Safari": ["Kenya", "Tanzania", "South Africa", "Namibia", "Botswana", "Uganda", "Rwanda"],
    "Snowmobile Tours": ["Iceland", "Lapland", "Norway", "Canada", "Greenland", "Russia", "Antarctica"],
    "Jeep Tours": ["Jordan", "Morocco", "Namibia", "Kyrgyzstan", "Georgia", "Mongolia", "Oman", "Tunisia", "Bolivia", "Israel"],
    "Train Tours": ["Switzerland", "Japan", "India", "Russia", "Scotland", "Norway", "Peru", "Canada", "Austria", "Italy"],
    "Geographic Cruises": ["Antarctica", "Norway", "Vietnam", "Greece", "Croatia", "Iceland", "Chile", "Argentina"],
    "Nature Hiking": "ALL",  # Can go anywhere with nature
    "Carnivals & Festivals": ["Brazil", "Bolivia", "Peru", "Spain", "Italy", "India", "Japan", "Thailand", "Mexico", "Cuba"],
    "Photography": "ALL",  # Can go anywhere
    "Private Groups": "ALL",  # Can go anywhere
}


def seed_database():
    """Seed the database with realistic data using TripType logic"""
    
    print("\n" + "="*70)
    print("SMARTRIP DATABASE SEED - WITH TRIPTYPE FOREIGN KEY LOGIC")
    print("="*70 + "\n")
    
    # Initialize database (create tables)
    init_db()
    
    # Create session
    session = SessionLocal()
    
    try:
        # ============================================
        # SEED COUNTRIES (Including Antarctica)
        # ============================================
        print("[SEEDING] Countries...")
        
        countries_data = [
            # AFRICA
            ('Uganda', 'אוגנדה', Continent.AFRICA),
            ('Ethiopia', 'אתיופיה', Continent.AFRICA),
            ('Botswana', 'בוטסוואנה', Continent.AFRICA),
            ('South Africa', 'דרום אפריקה', Continent.AFRICA),
            ('Tunisia', 'טוניסיה', Continent.AFRICA),
            ('Tanzania', 'טנזניה', Continent.AFRICA),
            ('Madagascar', 'מדגסקר', Continent.AFRICA),
            ('Egypt', 'מצרים', Continent.AFRICA),
            ('Morocco', 'מרוקו', Continent.AFRICA),
            ('Namibia', 'נמיביה', Continent.AFRICA),
            ('Kenya', 'קניה', Continent.AFRICA),
            ('Rwanda', 'רואנדה', Continent.AFRICA),
            
            # ASIA (including Middle East)
            ('Uzbekistan', 'אוזבקיסטן', Continent.ASIA),
            ('Azerbaijan', 'אזרבייג\'ן', Continent.ASIA),
            ('United Arab Emirates', 'איחוד האמירויות', Continent.ASIA),
            ('Indonesia', 'אינדונזיה', Continent.ASIA),
            ('Bhutan', 'בהוטן', Continent.ASIA),
            ('Myanmar', 'בורמה', Continent.ASIA),
            ('India', 'הודו', Continent.ASIA),
            ('Hong Kong', 'הונג קונג', Continent.ASIA),
            ('Vietnam', 'וייטנאם', Continent.ASIA),
            ('Taiwan', 'טאיוואן', Continent.ASIA),
            ('Tajikistan', 'טג\'יקיסטן', Continent.ASIA),
            ('Turkey', 'טורקיה', Continent.ASIA),
            ('Tibet', 'טיבט', Continent.ASIA),
            ('Japan', 'יפן', Continent.ASIA),
            ('Jordan', 'ירדן', Continent.ASIA),
            ('Israel', 'ישראל', Continent.ASIA),
            ('Laos', 'לאוס', Continent.ASIA),
            ('Mongolia', 'מונגוליה', Continent.ASIA),
            ('Nepal', 'נפאל', Continent.ASIA),
            ('China', 'סין', Continent.ASIA),
            ('Singapore', 'סינגפור', Continent.ASIA),
            ('Sri Lanka', 'סרי לנקה', Continent.ASIA),
            ('Oman', 'עומאן', Continent.ASIA),
            ('Philippines', 'פיליפינים', Continent.ASIA),
            ('North Korea', 'צפון קוריאה', Continent.ASIA),
            ('South Korea', 'קוריאה הדרומית', Continent.ASIA),
            ('Kyrgyzstan', 'קירגיזסטן', Continent.ASIA),
            ('Cambodia', 'קמבודיה', Continent.ASIA),
            ('Thailand', 'תאילנד', Continent.ASIA),
            
            # EUROPE
            ('Austria', 'אוסטריה', Continent.EUROPE),
            ('Ukraine', 'אוקראינה', Continent.EUROPE),
            ('Italy', 'איטליה', Continent.EUROPE),
            ('Azores', 'איים האזורים', Continent.EUROPE),
            ('Canary Islands', 'איים הקנריים', Continent.EUROPE),
            ('Iceland', 'איסלנד', Continent.EUROPE),
            ('Ireland', 'אירלנד', Continent.EUROPE),
            ('Albania', 'אלבניה', Continent.EUROPE),
            ('England', 'אנגליה', Continent.EUROPE),
            ('Estonia', 'אסטוניה', Continent.EUROPE),
            ('Armenia', 'ארמניה', Continent.EUROPE),
            ('Scotland', 'סקוטלנד', Continent.EUROPE),
            ('Bulgaria', 'בולגריה', Continent.EUROPE),
            ('Bosnia and Herzegovina', 'בוסניה והרצגובינה', Continent.EUROPE),
            ('Belgium', 'בלגיה', Continent.EUROPE),
            ('Georgia', 'גאורגיה', Continent.EUROPE),
            ('Greenland', 'גרינלנד', Continent.EUROPE),
            ('Germany', 'גרמניה', Continent.EUROPE),
            ('Dagestan', 'דגסטאן', Continent.EUROPE),
            ('Netherlands', 'הולנד', Continent.EUROPE),
            ('Hungary', 'הונגריה', Continent.EUROPE),
            ('Greece', 'יוון', Continent.EUROPE),
            ('Crete', 'כרתים ואיי יוון', Continent.EUROPE),
            ('Latvia', 'לטביה', Continent.EUROPE),
            ('Lithuania', 'ליטא', Continent.EUROPE),
            ('Lapland', 'לפלנד', Continent.EUROPE),
            ('Madeira', 'מדירה', Continent.EUROPE),
            ('Mont Blanc', 'מון בלאן', Continent.EUROPE),
            ('Montenegro', 'מונטנגרו', Continent.EUROPE),
            ('Malta', 'מלטה', Continent.EUROPE),
            ('Macedonia', 'מקדוניה', Continent.EUROPE),
            ('Norway', 'נורבגיה', Continent.EUROPE),
            ('Sicily', 'סיציליה', Continent.EUROPE),
            ('Slovenia', 'סלובניה', Continent.EUROPE),
            ('Slovakia', 'סלובקיה', Continent.EUROPE),
            ('Spain', 'ספרד', Continent.EUROPE),
            ('Scandinavia', 'סקנדינביה', Continent.EUROPE),
            ('Serbia', 'סרביה', Continent.EUROPE),
            ('Sardinia', 'סרדיניה', Continent.EUROPE),
            ('Poland', 'פולין', Continent.EUROPE),
            ('Portugal', 'פורטוגל', Continent.EUROPE),
            ('Czech Republic', 'צ\'כיה', Continent.EUROPE),
            ('France', 'צרפת', Continent.EUROPE),
            ('Corsica', 'קורסיקה', Continent.EUROPE),
            ('Croatia', 'קרואטיה', Continent.EUROPE),
            ('Romania', 'רומניה', Continent.EUROPE),
            ('Russia', 'רוסיה', Continent.EUROPE),
            ('Switzerland', 'שוויץ', Continent.EUROPE),
            
            # NORTH & CENTRAL AMERICA
            ('United States', 'ארצות הברית', Continent.NORTH_AND_CENTRAL_AMERICA),
            ('Guatemala', 'גואטמלה', Continent.NORTH_AND_CENTRAL_AMERICA),
            ('Hawaii', 'הוואי', Continent.NORTH_AND_CENTRAL_AMERICA),
            ('Mexico', 'מקסיקו', Continent.NORTH_AND_CENTRAL_AMERICA),
            ('Panama', 'פנמה', Continent.NORTH_AND_CENTRAL_AMERICA),
            ('Cuba', 'קובה', Continent.NORTH_AND_CENTRAL_AMERICA),
            ('Costa Rica', 'קוסטה ריקה', Continent.NORTH_AND_CENTRAL_AMERICA),
            ('Canada', 'קנדה', Continent.NORTH_AND_CENTRAL_AMERICA),
            
            # SOUTH AMERICA
            ('Ecuador', 'אקוודור', Continent.SOUTH_AMERICA),
            ('Argentina', 'ארגנטינה', Continent.SOUTH_AMERICA),
            ('Bolivia', 'בוליביה', Continent.SOUTH_AMERICA),
            ('Brazil', 'ברזיל', Continent.SOUTH_AMERICA),
            ('Peru', 'פרו', Continent.SOUTH_AMERICA),
            ('Chile', 'צ\'ילה', Continent.SOUTH_AMERICA),
            ('Colombia', 'קולומביה', Continent.SOUTH_AMERICA),
            
            # ANTARCTICA
            ('Antarctica', 'אנטארקטיקה', Continent.ANTARCTICA),
        ]
        
        for name, name_he, continent in countries_data:
            existing = session.query(Country).filter(Country.name == name).first()
            if not existing:
                country = Country(name=name, name_he=name_he, continent=continent)
                session.add(country)
        
        session.commit()
        country_count = session.query(Country).count()
        print(f"SUCCESS: Seeded {country_count} countries (including Antarctica)\n")
        
        # ============================================
        # SEED TRIP TYPES (New Model - Foreign Key)
        # ============================================
        print("[SEEDING] Trip Types (Foreign Key Model)...")
        
        # Use EXPLICIT IDs to ensure consistency across environments
        trip_types_data = [
            (1, 'Geographic Depth', 'טיולי עומק גיאוגרפיים', 'In-depth geographical exploration tours'),
            (2, 'Carnivals & Festivals', 'קרנבלים ופסטיבלים', 'Cultural carnivals and festivals'),
            (3, 'African Safari', 'ספארי באפריקה', 'Wildlife safari adventures in Africa'),
            (4, 'Train Tours', 'טיולי רכבות', 'Scenic railway journeys'),
            (5, 'Geographic Cruises', 'טיולי שייט גיאוגרפיים', 'Maritime exploration cruises'),
            (6, 'Nature Hiking', 'טיולי הליכות בטבע', 'Nature walks and hiking'),
            (7, 'Jeep Tours', 'טיולי ג\'יפים', '4x4 off-road adventures'),
            (8, 'Snowmobile Tours', 'טיולי אופנועי שלג', 'Arctic snowmobile expeditions'),
            (9, 'Photography', 'טיולי צילום', 'Photography-focused tours'),
            (10, 'Private Groups', 'קבוצות סגורות', 'Exclusive private group tours'),
        ]
        
        for type_id, name, name_he, description in trip_types_data:
            existing = session.query(TripType).filter(TripType.id == type_id).first()
            if not existing:
                trip_type = TripType(id=type_id, name=name, name_he=name_he, description=description)
                session.add(trip_type)
            else:
                # Update existing to ensure correct names
                existing.name = name
                existing.name_he = name_he
                existing.description = description
        
        session.commit()
        type_count = session.query(TripType).count()
        print(f"SUCCESS: Seeded {type_count} Trip Types with consistent IDs (Foreign Key)\n")
        
        # ============================================
        # SEED THEME TAGS (THEME Category Only)
        # ============================================
        print("[SEEDING] Theme Tags (THEME Category Only)...")
        
        # Use EXPLICIT IDs to ensure consistency across environments
        theme_tags_data = [
            (1, 'Cultural & Historical', 'תרבות והיסטוריה', 'Cultural immersion and historical heritage sites'),
            (2, 'Wildlife', 'חיות בר', 'Wildlife observation tours'),
            (3, 'Extreme', 'אקסטרים', 'Extreme adventure and challenge'),
            (4, 'Food & Wine', 'אוכל ויין', 'Culinary and wine tours'),
            (5, 'Beach & Island', 'חופים ואיים', 'Beach and island getaways'),
            (6, 'Mountain', 'הרים', 'Mountain expeditions'),
            (7, 'Desert', 'מדבר', 'Desert exploration'),
            (8, 'Arctic & Snow', 'קרח ושלג', 'Arctic and winter expeditions'),
            (9, 'Tropical', 'טרופי', 'Tropical destinations'),
            (11, 'Hanukkah & Christmas Lights', 'אורות חנוכה וכריסמס', 'Holiday lights and festive tours'),
        ]
        
        for tag_id, name, name_he, description in theme_tags_data:
            existing = session.query(Tag).filter(Tag.id == tag_id).first()
            if not existing:
                tag = Tag(id=tag_id, name=name, name_he=name_he, description=description, category=TagCategory.THEME)
                session.add(tag)
            else:
                # Update existing to ensure correct names
                existing.name = name
                existing.name_he = name_he
                existing.description = description
        
        session.commit()
        theme_count = session.query(Tag).count()
        print(f"SUCCESS: Seeded {theme_count} Theme Tags with consistent IDs\n")
        
        # ============================================
        # IMPORT GUIDES FROM CSV
        # ============================================
        print("[IMPORTING] Guides from CSV...")
        
        # 5 Specific hardcoded guides
        specific_guides = [
            ('איילה כהן', 'ayala@ayalageo.co.il', '+972-3-9436030', Gender.FEMALE, 45,
             'Founder of Ayala Geographic, specializing in geographic depth tours worldwide',
             'מייסדת איילה גיאוגרפית, מתמחה בטיולי עומק גיאוגרפיים ברחבי העולם'),
            ('דוד לוי', 'david@ayalageo.co.il', '+972-50-1234567', Gender.MALE, 38,
             'Expert in African safaris and wildlife tours',
             'מומחה לספארי אפריקאי וטיולי חיות בר'),
            ('שרה מזרחי', 'sarah@ayalageo.co.il', '+972-52-9876543', Gender.FEMALE, 42,
             'Specialist in Asian cultural tours and trekking',
             'מומחית לטיולי תרבות אסייתיים וטרקים'),
            ('משה אמיר', 'moshe@ayalageo.co.il', '+972-54-5556666', Gender.MALE, 50,
             'Expert in European historical and cultural tours',
             'מומחה לטיולי היסטוריה ותרבות באירופה'),
            ('רחל גרין', 'rachel@ayalageo.co.il', '+972-53-7778888', Gender.FEMALE, 35,
             'Specialist in South American adventures and nature tours',
             'מומחית להרפתקאות וטיולי טבע בדרום אמריקה'),
        ]
        
        for name_he, email, phone, gender, age, bio, bio_he in specific_guides:
            existing = session.query(Guide).filter(Guide.email == email).first()
            if not existing:
                guide = Guide(
                    name=name_he,
                    name_he=name_he,
                    email=email,
                    phone=phone,
                    gender=gender,
                    age=age,
                    bio=bio,
                    bio_he=bio_he,
                    is_active=True
                )
                session.add(guide)
        
        # Generate 20 additional guides
        specializations_en = [
            'Expert in mountain trekking and high-altitude expeditions',
            'Specialist in cultural heritage and archaeological sites',
            'Wildlife photography and safari guide',
            'Marine biology and coastal ecosystems expert',
            'Culinary tourism and wine tasting specialist',
            'Adventure sports and extreme activities guide',
            'Historical architecture and urban exploration expert',
            'Botanical gardens and nature conservation specialist',
            'Religious sites and spiritual tourism guide',
            'Photography workshops and landscape expert',
            'Family-friendly tours and educational travel',
            'Luxury travel and boutique experiences specialist',
            'Eco-tourism and sustainable travel advocate',
            'Winter sports and Arctic expeditions expert',
            'Desert survival and Bedouin culture specialist',
            'Island hopping and tropical destinations guide',
            'Train journeys and railway heritage expert',
            'Festival and carnival celebrations specialist',
            'Art museums and contemporary culture guide',
            'Indigenous cultures and tribal communities expert'
        ]
        
        specializations_he = [
            'מומחה לטיולי הרים ומשלחות לגבהים',
            'מתמחה במורשת תרבותית ואתרים ארכיאולוגיים',
            'מדריך צילום חיות בר וספארי',
            'מומחה לביולוגיה ימית ומערכות אקולוגיות חופיות',
            'מתמחה בתיירות קולינרית וטעימות יין',
            'מדריך ספורט אתגרי ופעילויות אקסטרים',
            'מומחה לארכיטקטורה היסטורית וחקר עירוני',
            'מתמחה בגנים בוטניים ושימור טבע',
            'מדריך אתרים דתיים ותיירות רוחנית',
            'מומחה לסדנאות צילום ונופים',
            'טיולים משפחתיים ונסיעות חינוכיות',
            'מתמחה בנסיעות יוקרה וחוויות בוטיק',
            'תומך אקו-תיירות ונסיעות בר-קיימא',
            'מומחה לספורט חורף ומשלחות ארקטיות',
            'מתמחה בהישרדות במדבר ותרבות בדואית',
            'מדריך אי-הופינג ויעדים טרופיים',
            'מומחה למסעות רכבת ומורשת רכבות',
            'מתמחה בפסטיבלים וחגיגות קרנבל',
            'מדריך מוזיאוני אמנות ותרבות עכשווית',
            'מומחה לתרבויות ילידים וקהילות שבטיות'
        ]
        
        for i in range(20):
            first_name_he = fake_he.first_name()
            last_name_he = fake_he.last_name()
            name_he = f"{first_name_he} {last_name_he}"
            email_name = f"guide{i+6}@ayalageo.co.il"
            phone = f"+972-{random.choice(['50', '52', '53', '54'])}-{random.randint(1000000, 9999999)}"
            gender = random.choice([Gender.MALE, Gender.FEMALE])
            age = random.randint(28, 60)
            spec_index = i % len(specializations_en)
            
            existing = session.query(Guide).filter(Guide.email == email_name).first()
            if not existing:
                guide = Guide(
                    name=name_he,
                    name_he=name_he,
                    email=email_name,
                    phone=phone,
                    gender=gender,
                    age=age,
                    bio=specializations_en[spec_index],
                    bio_he=specializations_he[spec_index],
                    is_active=True
                )
                session.add(guide)
        
        session.commit()
        guide_count = session.query(Guide).count()
        print(f"SUCCESS: Seeded {guide_count} guides\n")
        
        # ============================================
        # SMART TRIP GENERATION WITH TRIPTYPE LOGIC
        # ============================================
        print("[GENERATING] Trips with TripType-Country logic...\n")
        
        # Get all data
        all_countries = session.query(Country).all()
        all_guides = session.query(Guide).filter(Guide.is_active == True).all()
        all_trip_types = session.query(TripType).all()
        theme_tags = session.query(Tag).filter(Tag.category == TagCategory.THEME).all()
        
        # Build country name lookup
        country_by_name = {c.name: c for c in all_countries}
        
        # Smart tag mapping by continent
        CONTINENT_THEME_MAPPING = {
            Continent.AFRICA: ['Wildlife', 'Cultural & Historical', 'Desert', 'Photography', 'Extreme'],
            Continent.ASIA: ['Cultural & Historical', 'Food & Wine', 'Mountain', 'Tropical', 'Beach & Island'],
            Continent.EUROPE: ['Cultural & Historical', 'Food & Wine', 'Mountain', 'Arctic & Snow', 'Hanukkah & Christmas Lights'],
            Continent.NORTH_AND_CENTRAL_AMERICA: ['Mountain', 'Desert', 'Beach & Island', 'Wildlife', 'Cultural & Historical'],
            Continent.SOUTH_AMERICA: ['Mountain', 'Tropical', 'Wildlife', 'Cultural & Historical', 'Extreme'],
            Continent.OCEANIA: ['Beach & Island', 'Tropical', 'Wildlife', 'Mountain', 'Extreme'],
            Continent.ANTARCTICA: ['Arctic & Snow', 'Wildlife', 'Extreme', 'Photography'],
        }
        
        # Premium Hebrew Title Templates
        HEBREW_TITLE_TEMPLATES = [
            'הקסם של {}',
            'מסע אל מעמקי {}',
            '{}: טבע ותרבות',
            'גלה את {}',
            'חוויה של פעם בחיים ב{}',
            '{} המרתקת',
            'הרפתקה ב{}',
            'סיור מעמיק ב{}',
            '{}: מסע בלתי נשכח',
            'פלאי {}',
            'אוצרות {}',
            '{} – מסע חלומות',
        ]
        
        # Premium Hebrew Description Templates by Continent
        HEBREW_DESCRIPTIONS = {
            Continent.ASIA: [
                'מסע צבעוני בלב המזרח הקסום, בין טרסות אורז, כפרים מסורתיים ונופים עוצרי נשימה.',
                'מסע מעמיק אל הלב, הרוח, הטעמים והצבעים של תת-היבשת המרתקת.',
                'גלו את קסמה של תרבות עתיקה ששרדה אלפי שנים. בין מקדשים מפוארים וטבע בראשיתי.',
            ],
            Continent.AFRICA: [
                'מסע אל הלב הפועם של היבשת הפראית. ספארי מרהיב, שקיעות אדומות ועולם חי עשיר.',
                'חוויה אפריקאית אמיתית: בין סוואנות אינסופיות, חיות בר מרהיבות ותרבויות שבטיות עתיקות.',
                'גלו את קסם המדבר האפריקאי, דיונות זהב אינסופיות ושקיעות עוצרות נשימה.',
            ],
            Continent.EUROPE: [
                'מסע תרבותי מרתק בין ארמונות מפוארים, כנסיות גותיות ומוזיאונים עשירים.',
                'גלו את קסמה של היבשת העתיקה: אדריכלות מרהיבה, אמנות מופתית וקולינריה מעודנת.',
                'מסע היסטורי מעמיק בין ערים עתיקות ואתרי מורשת עולמית.',
            ],
            Continent.SOUTH_AMERICA: [
                'הרפתקה של פעם בחיים ביבשת הססגונית – טבע פראי, תרבויות מרתקות וערים תוססות.',
                'מסע אל לב יער הגשם האמזוני, בין עצים עתיקים וחיות בר נדירות.',
                'טרק מרגש בין פסגות האנדים המושלגות ושרידי תרבות האינקה העתיקה.',
            ],
            Continent.NORTH_AND_CENTRAL_AMERICA: [
                'גלו את יופי המערב הפראי: קניונים אדומים, נופים אינסופיים ופארקים לאומיים מרהיבים.',
                'מסע אל הטבע הצפון-אמריקאי: בין יערות ירוקים, אגמים צלולים והרים מושלגים.',
                'טרופי קריבי: חופים לבנים, מים טורקיז ושונית אלמוגים צבעונית.',
            ],
            Continent.OCEANIA: [
                'מסע חד פעמי בין איים וחלומות – שייט מרהיב לגן העדן הטרופי.',
                'מסע אל קצה העולם – טבע בראשיתי, נופים דרמטיים ועולם חי נדיר.',
                'גלו את ניו זילנד הקסומה: פיורדים כחולים, הרים מושלגים וגייזרים מפעפעים.',
            ],
            Continent.ANTARCTICA: [
                'מסע אל הקוטב הנצחי – קרחונים כחולים מרהיבים, פינגווינים באלפים וטבע קפוא בראשיתי.',
                'חוויה קוטבית אמיתית ביבשת הלבנה: שדות קרח אינסופיים והרי קרח מרהיבים.',
                'שייט קוטבי מרגש בין קרחונים צפים ומושבות פינגווינים ענקיות.',
            ],
        }
        
        # Track trips per country
        trips_per_country = {country.id: 0 for country in all_countries}
        all_generated_trips = []
        
        # PHASE 1: Generate trips by TripType (at least 10 per type)
        print("PHASE 1: Generating trips by TripType (min 10 per type)...\n")
        
        for trip_type in all_trip_types:
            type_name = trip_type.name
            country_restriction = TYPE_TO_COUNTRY_LOGIC.get(type_name, "ALL")
            
            # Get valid countries for this type
            if country_restriction == "ALL":
                valid_countries = all_countries
            else:
                valid_countries = [country_by_name[name] for name in country_restriction if name in country_by_name]
            
            if not valid_countries:
                print(f"WARNING: No valid countries for {type_name}, skipping...")
                continue
            
            # Generate 30-40 trips for this type (to reach ~400 total)
            num_trips = random.randint(30, 40)
            print(f"  [{type_name}] Generating {num_trips} trips...")
            
            for _ in range(num_trips):
                country = random.choice(valid_countries)
                trips_per_country[country.id] += 1
                
                # Generate trip data
                trip_data = generate_trip_data(
                    country=country,
                    trip_type=trip_type,
                    guide=random.choice(all_guides),
                    theme_tags=theme_tags,
                    continent_theme_mapping=CONTINENT_THEME_MAPPING,
                    hebrew_title_templates=HEBREW_TITLE_TEMPLATES,
                    hebrew_descriptions=HEBREW_DESCRIPTIONS
                )
                
                all_generated_trips.append(trip_data)
        
        print(f"\nSUCCESS: Phase 1 Complete - {len(all_generated_trips)} trips generated\n")
        
        # PHASE 2: Ensure every country has at least 1 trip
        print("PHASE 2: Ensuring every country has at least 1 trip...\n")
        
        countries_needing_trips = [c for c in all_countries if trips_per_country[c.id] == 0]
        
        for country in countries_needing_trips:
            # Find compatible trip types for this country
            compatible_types = []
            for trip_type in all_trip_types:
                restriction = TYPE_TO_COUNTRY_LOGIC.get(trip_type.name, "ALL")
                if restriction == "ALL" or country.name in restriction:
                    compatible_types.append(trip_type)
            
            if not compatible_types:
                # Default to "Geographic Depth" (works everywhere)
                compatible_types = [t for t in all_trip_types if t.name == "Geographic Depth"]
            
            trip_type = random.choice(compatible_types)
            trips_per_country[country.id] += 1
            
            trip_data = generate_trip_data(
                country=country,
                trip_type=trip_type,
                guide=random.choice(all_guides),
                theme_tags=theme_tags,
                continent_theme_mapping=CONTINENT_THEME_MAPPING,
                hebrew_title_templates=HEBREW_TITLE_TEMPLATES,
                hebrew_descriptions=HEBREW_DESCRIPTIONS
            )
            
            all_generated_trips.append(trip_data)
            print(f"  [ADDED] Trip for {country.name} ({trip_type.name})")
        
        print(f"\nSUCCESS: Phase 2 Complete - {len(countries_needing_trips)} countries filled\n")
        
        # PHASE 3: Save all trips to database
        print("PHASE 3: Saving trips to database...\n")
        
        for idx, trip_data in enumerate(all_generated_trips, 1):
            trip = Trip(
                title=trip_data['title'],
                title_he=trip_data['title_he'],
                description=trip_data['description'],
                description_he=trip_data['description_he'],
                start_date=trip_data['start_date'],
                end_date=trip_data['end_date'],
                price=trip_data['price'],
                single_supplement_price=trip_data['single_supplement'],
                max_capacity=trip_data['max_capacity'],
                spots_left=trip_data['spots_left'],
                status=trip_data['status'],
                difficulty_level=trip_data['difficulty'],
                country_id=trip_data['country_id'],
                guide_id=trip_data['guide_id'],
                trip_type_id=trip_data['trip_type_id']  # Foreign Key to TripType
            )
            session.add(trip)
            session.flush()
            
            # Add theme tags (many-to-many)
            for theme_tag_id in trip_data['theme_tag_ids']:
                trip_tag = TripTag(trip_id=trip.id, tag_id=theme_tag_id)
                session.add(trip_tag)
            
            if idx % 50 == 0:
                print(f"  ... {idx} trips saved")
        
        session.commit()
        trip_count = session.query(Trip).count()
        print(f"\nSUCCESS: Saved {trip_count} trips to database\n")
        
        # ============================================
        # FINAL SUMMARY
        # ============================================
        print("="*70)
        print("DATABASE SEED COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"\nFinal Statistics:")
        print(f"   - Countries: {country_count}")
        print(f"   - Trip Types: {type_count}")
        print(f"   - Theme Tags: {theme_count}")
        print(f"   - Guides: {guide_count}")
        print(f"   - Trips: {trip_count}")
        
        # Show trips per type
        print(f"\nTrips per Type:")
        for trip_type in all_trip_types:
            count = session.query(Trip).filter(Trip.trip_type_id == trip_type.id).count()
            print(f"   - {trip_type.name}: {count} trips")
        
        print(f"\nSUCCESS: All countries have at least 1 trip!")
        print(f"SUCCESS: Database ready for production!\n")
        
    except Exception as e:
        print(f"\nERROR seeding database: {e}")
        session.rollback()
        raise
    
    finally:
        session.close()


def generate_trip_data(country, trip_type, guide, theme_tags, continent_theme_mapping, 
                       hebrew_title_templates, hebrew_descriptions):
    """Generate trip data with premium content"""
    
    continent = country.continent
    is_private_group = trip_type.name == 'Private Groups'
    
    # Generate dates (special handling for Private Groups)
    if is_private_group:
        # Private Groups: no fixed date (set to far future)
        start_date = datetime(2099, 12, 31).date()
        end_date = datetime(2099, 12, 31).date()
    else:
        # Regular trips: 1-18 months from now, 5-30 days duration
        days_from_now = random.randint(30, 540)
        start_date = datetime.now().date() + timedelta(days=days_from_now)
        duration = random.randint(5, 30)
        end_date = start_date + timedelta(days=duration)
    
    # Generate price ($2,000-$15,000, ends in 0)
    base_price = random.randint(200, 1500) * 10
    single_supplement = base_price * random.uniform(0.15, 0.25)
    
    # Generate capacity (special handling for Private Groups)
    if is_private_group:
        # Private Groups: 0 participants (entire group booking)
        max_capacity = 0
        spots_left = 0
        status = TripStatus.OPEN  # Always open for group bookings
    else:
        # Regular trips: normal capacity
        max_capacity = random.choice([12, 15, 18, 20, 24, 25, 30])
        spots_left = random.randint(0, max_capacity)
        
        # Determine status
        if spots_left == 0:
            status = TripStatus.FULL
        elif spots_left <= 4:
            status = TripStatus.LAST_PLACES
        elif spots_left >= max_capacity * 0.8:
            status = TripStatus.OPEN
        else:
            status = random.choice([TripStatus.GUARANTEED, TripStatus.LAST_PLACES, TripStatus.OPEN])
    
    # Difficulty
    difficulty = random.randint(1, 3)
    
    # Generate titles
    template = random.choice(hebrew_title_templates)
    title_he = template.format(country.name_he)
    title = f"Discover {country.name}"
    
    # Generate descriptions
    continent_descriptions_he = hebrew_descriptions.get(continent, hebrew_descriptions[Continent.ASIA])
    description_he = random.choice(continent_descriptions_he)
    description = f"Explore the wonders of {country.name}. An unforgettable journey awaits."
    
    # Select theme tags (continent-appropriate)
    continent_themes = continent_theme_mapping.get(continent, [])
    available_theme_tags = [t for t in theme_tags if t.name in continent_themes]
    
    theme_tag_ids = []
    if available_theme_tags:
        num_themes = random.randint(1, min(3, len(available_theme_tags)))
        selected_themes = random.sample(available_theme_tags, num_themes)
        theme_tag_ids = [t.id for t in selected_themes]
    
    return {
        'title': title,
        'title_he': title_he,
        'description': description,
        'description_he': description_he,
        'start_date': start_date,
        'end_date': end_date,
        'price': base_price,
        'single_supplement': single_supplement,
        'max_capacity': max_capacity,
        'spots_left': spots_left,
        'status': status,
        'difficulty': difficulty,
        'country_id': country.id,
        'guide_id': guide.id,
        'trip_type_id': trip_type.id,  # Foreign Key
        'theme_tag_ids': theme_tag_ids
    }


if __name__ == '__main__':
    seed_database()
