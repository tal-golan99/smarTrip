"""
Database Seed Script - Import from CSV
=======================================
Imports consistent data from CSV files for identical seeding across environments.
"""

import csv
from datetime import datetime
from database import SessionLocal, init_db, drop_db
from models import Country, Guide, Tag, Trip, TripTag, TripType, Continent, Gender, TripStatus, TagCategory

def seed_from_csv():
    """Seed database by importing from CSV files"""
    
    print("\n" + "="*70)
    print("SMARTRIP DATABASE SEED - FROM CSV FILES")
    print("="*70 + "\n")
    
    # Drop and recreate tables
    drop_db()
    init_db()
    
    session = SessionLocal()
    
    try:
        # ============================================
        # SEED COUNTRIES (Static Data)
        # ============================================
        print("[SEEDING] Countries...")
        
        countries_data = [
            # ASIA
            ('India', 'הודו', Continent.ASIA),
            ('Japan', 'יפן', Continent.ASIA),
            ('Thailand', 'תאילנד', Continent.ASIA),
            ('Vietnam', 'וייטנם', Continent.ASIA),
            ('China', 'סין', Continent.ASIA),
            ('South Korea', 'דרום קוריאה', Continent.ASIA),
            ('Indonesia', 'אינדונזיה', Continent.ASIA),
            ('Malaysia', 'מלזיה', Continent.ASIA),
            ('Nepal', 'נפאל', Continent.ASIA),
            ('Sri Lanka', 'סרי לנקה', Continent.ASIA),
            ('Cambodia', 'קמבודיה', Continent.ASIA),
            ('Laos', 'לאוס', Continent.ASIA),
            ('Myanmar', 'מיאנמר', Continent.ASIA),
            ('Philippines', 'פיליפינים', Continent.ASIA),
            ('Mongolia', 'מונגוליה', Continent.ASIA),
            ('Bhutan', 'בהוטן', Continent.ASIA),
            
            # AFRICA
            ('South Africa', 'דרום אפריקה', Continent.AFRICA),
            ('Kenya', 'קניה', Continent.AFRICA),
            ('Tanzania', 'טנזניה', Continent.AFRICA),
            ('Morocco', 'מרוקו', Continent.AFRICA),
            ('Egypt', 'מצרים', Continent.AFRICA),
            ('Uganda', 'אוגנדה', Continent.AFRICA),
            ('Rwanda', 'רואנדה', Continent.AFRICA),
            ('Zimbabwe', 'זימבבואה', Continent.AFRICA),
            ('Namibia', 'נמיביה', Continent.AFRICA),
            ('Botswana', 'בוטסואנה', Continent.AFRICA),
            ('Zambia', 'זמביה', Continent.AFRICA),
            ('Senegal', 'סנגל', Continent.AFRICA),
            ('Ghana', 'גאנה', Continent.AFRICA),
            ('Ethiopia', 'אתיופיה', Continent.AFRICA),
            ('Madagascar', 'מדגסקר', Continent.AFRICA),
            ('Tunisia', 'תוניסיה', Continent.AFRICA),
            
            # OCEANIA
            ('Australia', 'אוסטרליה', Continent.OCEANIA),
            ('New Zealand', 'ניו זילנד', Continent.OCEANIA),
            ('Fiji', 'פיג\'י', Continent.OCEANIA),
            ('Papua New Guinea', 'פפואה גינאה החדשה', Continent.OCEANIA),
            ('Tahiti', 'טהיטי', Continent.OCEANIA),
            ('Samoa', 'סמואה', Continent.OCEANIA),
            ('Vanuatu', 'ונואטו', Continent.OCEANIA),
            ('New Caledonia', 'קלדוניה החדשה', Continent.OCEANIA),
            ('Cook Islands', 'איי קוק', Continent.OCEANIA),
            
            # EUROPE
            ('Italy', 'איטליה', Continent.EUROPE),
            ('Greece', 'יוון', Continent.EUROPE),
            ('Iceland', 'איסלנד', Continent.EUROPE),
            ('Ireland', 'אירלנד', Continent.EUROPE),
            ('England', 'אנגליה', Continent.EUROPE),
            ('Scotland', 'סקוטלנד', Continent.EUROPE),
            ('Estonia', 'אסטוניה', Continent.EUROPE),
            ('Austria', 'אוסטריה', Continent.EUROPE),
            ('Albania', 'אלבניה', Continent.EUROPE),
            ('Germany', 'גרמניה', Continent.EUROPE),
            ('Holland', 'הולנד', Continent.EUROPE),
            ('Hungary', 'הונגריה', Continent.EUROPE),
            ('Wales', 'וויילס', Continent.EUROPE),
            ('Georgia', 'גיאורגיה', Continent.EUROPE),
            ('Denmark', 'דנמרק', Continent.EUROPE),
            ('Turkey', 'טורקיה', Continent.EUROPE),
            ('Latvia', 'לטביה', Continent.EUROPE),
            ('Lithuania', 'ליטא', Continent.EUROPE),
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
            country = Country(name=name, name_he=name_he, continent=continent)
            session.add(country)
        
        session.commit()
        print(f"[OK] Seeded {len(countries_data)} countries\n")
        
        # ============================================
        # SEED TRIP TYPES (Static Data with Fixed IDs)
        # ============================================
        print("[SEEDING] Trip Types...")
        
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
            trip_type = TripType(id=type_id, name=name, name_he=name_he, description=description)
            session.add(trip_type)
        
        session.commit()
        print(f"[OK] Seeded {len(trip_types_data)} trip types\n")
        
        # ============================================
        # SEED TAGS (Static Data with Fixed IDs)
        # ============================================
        print("[SEEDING] Theme Tags...")
        
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
            tag = Tag(id=tag_id, name=name, name_he=name_he, description=description, category=TagCategory.THEME)
            session.add(tag)
        
        session.commit()
        print(f"[OK] Seeded {len(theme_tags_data)} theme tags\n")
        
        # ============================================
        # IMPORT GUIDES FROM CSV
        # ============================================
        print("[IMPORTING] Guides from CSV...")
        
        with open('data/guides.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            guides_imported = 0
            for row in reader:
                guide = Guide(
                    id=int(row['id']),
                    name=row['name'],
                    name_he=row['name_he'],
                    email=row['email'] if row['email'] else None,
                    phone=row['phone'] if row['phone'] else None,
                    gender=Gender(row['gender']) if row['gender'] else None,
                    age=int(row['age']) if row['age'] else None,
                    bio=row['bio'] if row['bio'] else None,
                    bio_he=row['bio_he'] if row['bio_he'] else None,
                    image_url=row['image_url'] if row['image_url'] else None
                )
                session.add(guide)
                guides_imported += 1
        
        session.commit()
        print(f"[OK] Imported {guides_imported} guides\n")
        
        # ============================================
        # IMPORT TRIPS FROM CSV
        # ============================================
        print("[IMPORTING] Trips from CSV...")
        
        with open('data/trips.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            trips_imported = 0
            for row in reader:
                trip = Trip(
                    id=int(row['id']),
                    title=row['title'],
                    title_he=row['title_he'],
                    description=row['description'] if row['description'] else None,
                    description_he=row['description_he'] if row['description_he'] else None,
                    image_url=row['image_url'] if row['image_url'] else None,
                    start_date=datetime.strptime(row['start_date'], '%Y-%m-%d').date(),
                    end_date=datetime.strptime(row['end_date'], '%Y-%m-%d').date(),
                    price=float(row['price']),
                    single_supplement_price=float(row['single_supplement_price']),
                    max_capacity=int(row['max_capacity']),
                    spots_left=int(row['spots_left']),
                    status=TripStatus(row['status']),
                    difficulty_level=int(row['difficulty_level']),
                    country_id=int(row['country_id']),
                    guide_id=int(row['guide_id']),
                    trip_type_id=int(row['trip_type_id'])
                )
                session.add(trip)
                trips_imported += 1
                
                if trips_imported % 50 == 0:
                    print(f"  ... {trips_imported} trips imported")
        
        session.commit()
        print(f"[OK] Imported {trips_imported} trips\n")
        
        # ============================================
        # IMPORT TRIP-TAG RELATIONSHIPS FROM CSV
        # ============================================
        print("[IMPORTING] Trip-Tag relationships from CSV...")
        
        with open('data/trip_tags.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            relationships_imported = 0
            for row in reader:
                trip_tag = TripTag(
                    trip_id=int(row['trip_id']),
                    tag_id=int(row['tag_id'])
                )
                session.add(trip_tag)
                relationships_imported += 1
        
        session.commit()
        print(f"[OK] Imported {relationships_imported} trip-tag relationships\n")
        
        # ============================================
        # FINAL SUMMARY
        # ============================================
        country_count = session.query(Country).count()
        type_count = session.query(TripType).count()
        theme_count = session.query(Tag).count()
        guide_count = session.query(Guide).count()
        trip_count = session.query(Trip).count()
        
        print("="*70)
        print("DATABASE SEED FROM CSV COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"\nFinal Statistics:")
        print(f"   - Countries: {country_count}")
        print(f"   - Trip Types: {type_count}")
        print(f"   - Theme Tags: {theme_count}")
        print(f"   - Guides: {guide_count}")
        print(f"   - Trips: {trip_count}")
        
        print("\nSUCCESS: Database ready with consistent data!\n")
        
    except Exception as e:
        session.rollback()
        print(f"\nERROR: {str(e)}\n")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    seed_from_csv()

