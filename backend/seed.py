"""
Database Seed Script with Smart Logic
Populates the database with realistic data from Ayala Geographic
"""

from database import SessionLocal, init_db
from models import Country, Guide, Tag, Trip, TripTag, Continent, Gender, TripStatus, TagCategory
from faker import Faker
from datetime import datetime, timedelta
import random

# Initialize Faker for Hebrew and English
fake_he = Faker('he_IL')
fake_en = Faker('en_US')

def seed_database():
    """Seed the database with realistic data"""
    
    print("Starting database seed...")
    
    # Initialize database (create tables)
    init_db()
    
    # Create session
    session = SessionLocal()
    
    try:
        # ============================================
        # CLEAR TRIPS DATA (Keep Countries/Tags/Guides)
        # ============================================
        print("Clearing existing trips and trip tags...")
        session.query(TripTag).delete()
        session.query(Trip).delete()
        session.commit()
        print("Cleared all trips and trip_tags")
        
        # ============================================
        # SEED COUNTRIES (Updated Geography)
        # ============================================
        print("Seeding countries...")
        
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
        ]
        
        for name, name_he, continent in countries_data:
            existing = session.query(Country).filter(Country.name == name).first()
            if not existing:
                country = Country(name=name, name_he=name_he, continent=continent)
                session.add(country)
        
        session.commit()
        print(f"Seeded {len(countries_data)} countries")
        
        # ============================================
        # SEED TAGS (Strict TYPE vs THEME)
        # ============================================
        print("Seeding tags...")
        
        tags_data = [
            # TYPE Category - The style of the trip
            ('Geographic Depth', 'טיולי עומק גיאוגרפיים', 'In-depth geographical exploration tours', TagCategory.TYPE),
            ('Carnivals & Festivals', 'טיולי קרנבלים ופסטיבלים', 'Cultural carnivals and festivals', TagCategory.TYPE),
            ('African Safari', 'ספארי באפריקה', 'Wildlife safari adventures in Africa', TagCategory.TYPE),
            ('Train Tours', 'טיולי רכבות', 'Scenic railway journeys', TagCategory.TYPE),
            ('Geographic Cruises', 'טיולי שייט גיאוגרפיים', 'Maritime exploration cruises', TagCategory.TYPE),
            ('Nature Hiking', 'טיולי הליכות בטבע', 'Nature walks and hiking', TagCategory.TYPE),
            ('Boutique Tours', 'טיולי בוטיק בתפירה אישית', 'Custom-tailored boutique experiences', TagCategory.TYPE),
            ('Jeep Tours', 'טיולי ג\'יפים', '4x4 off-road adventures', TagCategory.TYPE),
            ('Snowmobile Tours', 'טיולי אופנועי שלג', 'Arctic snowmobile expeditions', TagCategory.TYPE),
            ('Private Groups', 'קבוצות סגורות', 'Exclusive private group tours', TagCategory.TYPE),
            ('Photography', 'צילום', 'Photography-focused tours', TagCategory.TYPE),
            
            # THEME Category - The content of the trip
            ('Extreme', 'אקסטרים', 'Extreme adventure and challenge', TagCategory.THEME),
            ('Wildlife', 'חיות בר', 'Wildlife observation tours', TagCategory.THEME),
            ('Cultural', 'תרבות', 'Cultural immersion experiences', TagCategory.THEME),
            ('Historical', 'היסטוריה', 'Historical sites and heritage', TagCategory.THEME),
            ('Food & Wine', 'אוכל ויין', 'Culinary and wine tours', TagCategory.THEME),
            ('Beach & Island', 'חופים ואיים', 'Beach and island getaways', TagCategory.THEME),
            ('Mountain', 'הרים', 'Mountain expeditions', TagCategory.THEME),
            ('Desert', 'מדבר', 'Desert exploration', TagCategory.THEME),
            ('Arctic & Snow', 'קרח ושלג', 'Arctic and winter expeditions', TagCategory.THEME),
            ('Tropical', 'טרופי', 'Tropical destinations', TagCategory.THEME),
            ('Hanukkah & Christmas Lights', 'טיולי אורות חנוכה וכריסמס', 'Holiday lights and festive tours', TagCategory.THEME),
        ]
        
        for name, name_he, description, category in tags_data:
            existing = session.query(Tag).filter(Tag.name == name).first()
            if not existing:
                tag = Tag(name=name, name_he=name_he, description=description, category=category)
                session.add(tag)
        
        session.commit()
        print(f"Seeded {len(tags_data)} tags (TYPE + THEME categories)")
        
        # ============================================
        # SEED GUIDES (5 Specific + 20 Generated)
        # ============================================
        print("Seeding guides...")
        
        # 5 Specific hardcoded guides
        specific_guides = [
            ('Ayala Cohen', 'ayala@ayalageo.co.il', '+972-3-9436030', Gender.FEMALE, 45,
             'Founder of Ayala Geographic, specializing in geographic depth tours worldwide',
             'מייסדת איילה גיאוגרפית, מתמחה בטיולי עומק גיאוגרפיים ברחבי העולם'),
            ('David Levi', 'david@ayalageo.co.il', '+972-50-1234567', Gender.MALE, 38,
             'Expert in African safaris and wildlife tours',
             'מומחה לספארי אפריקאי וטיולי חיות בר'),
            ('Sarah Mizrahi', 'sarah@ayalageo.co.il', '+972-52-9876543', Gender.FEMALE, 42,
             'Specialist in Asian cultural tours and trekking',
             'מומחית לטיולי תרבות אסייתיים וטרקים'),
            ('Moshe Amir', 'moshe@ayalageo.co.il', '+972-54-5556666', Gender.MALE, 50,
             'Expert in European historical and cultural tours',
             'מומחה לטיולי היסטוריה ותרבות באירופה'),
            ('Rachel Green', 'rachel@ayalageo.co.il', '+972-53-7778888', Gender.FEMALE, 35,
             'Specialist in South American adventures and nature tours',
             'מומחית להרפתקאות וטיולי טבע בדרום אמריקה'),
        ]
        
        for name, email, phone, gender, age, bio, bio_he in specific_guides:
            existing = session.query(Guide).filter(Guide.email == email).first()
            if not existing:
                guide = Guide(
                    name=name,
                    email=email,
                    phone=phone,
                    gender=gender,
                    age=age,
                    bio=bio,
                    bio_he=bio_he,
                    is_active=True
                )
                session.add(guide)
        
        # Generate 20 additional realistic guides with Faker
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
            # Generate realistic Hebrew names ONLY
            first_name_he = fake_he.first_name()
            last_name_he = fake_he.last_name()
            name_he = f"{first_name_he} {last_name_he}"
            
            # Use Hebrew name for email (transliterated)
            email_name = f"guide{i+6}@ayalageo.co.il"
            phone = f"+972-{random.choice(['50', '52', '53', '54'])}-{random.randint(1000000, 9999999)}"
            gender = random.choice([Gender.MALE, Gender.FEMALE])
            age = random.randint(28, 60)
            
            spec_index = i % len(specializations_en)
            bio = specializations_en[spec_index]
            bio_he = specializations_he[spec_index]
            
            existing = session.query(Guide).filter(Guide.email == email_name).first()
            if not existing:
                guide = Guide(
                    name=name_he,  # Use Hebrew name
                    email=email_name,
                    phone=phone,
                    gender=gender,
                    age=age,
                    bio=bio,
                    bio_he=bio_he,
                    is_active=True
                )
                session.add(guide)
        
        session.commit()
        guide_count = session.query(Guide).count()
        print(f"Seeded {guide_count} guides (5 specific + 20 generated)")
        
        # ============================================
        # SEED TRIPS (200+ with High-Quality Hebrew Content)
        # ============================================
        print("Generating 200+ trips with premium Hebrew content...")
        
        # Get all data for trip generation
        all_countries = session.query(Country).all()
        all_guides = session.query(Guide).filter(Guide.is_active == True).all()
        type_tags = session.query(Tag).filter(Tag.category == TagCategory.TYPE).all()
        theme_tags = session.query(Tag).filter(Tag.category == TagCategory.THEME).all()
        
        # Smart tag mapping by continent
        CONTINENT_THEME_MAPPING = {
            Continent.AFRICA: ['Wildlife', 'Cultural', 'Desert', 'Photography', 'Extreme'],
            Continent.ASIA: ['Cultural', 'Historical', 'Food & Wine', 'Mountain', 'Tropical', 'Beach & Island'],
            Continent.EUROPE: ['Historical', 'Cultural', 'Food & Wine', 'Mountain', 'Arctic & Snow', 'Hanukkah & Christmas Lights'],
            Continent.NORTH_AND_CENTRAL_AMERICA: ['Mountain', 'Desert', 'Beach & Island', 'Wildlife', 'Cultural', 'Hanukkah & Christmas Lights'],
            Continent.SOUTH_AMERICA: ['Mountain', 'Tropical', 'Wildlife', 'Cultural', 'Extreme'],
            Continent.OCEANIA: ['Beach & Island', 'Tropical', 'Wildlife', 'Mountain', 'Extreme'],
            Continent.ANTARCTICA: ['Arctic & Snow', 'Wildlife', 'Extreme', 'Photography'],
        }
        
        # Price ranges by continent (in USD)
        CONTINENT_PRICE_RANGES = {
            Continent.AFRICA: (3000, 8000),
            Continent.ASIA: (2500, 6000),
            Continent.EUROPE: (2000, 5000),
            Continent.NORTH_AND_CENTRAL_AMERICA: (3000, 7000),
            Continent.SOUTH_AMERICA: (3500, 8000),
            Continent.OCEANIA: (5000, 12000),
            Continent.ANTARCTICA: (10000, 20000),
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
            'עקבות {} הקסומה',
            'נופי {} הדרמטיים',
            '{} בעונה המושלמת',
        ]
        
        # Premium Hebrew Description Templates by Continent
        HEBREW_DESCRIPTIONS = {
            Continent.ASIA: [
                'מסע צבעוני בלב המזרח הקסום, בין טרסות אורז, כפרים מסורתיים ונופים עוצרי נשימה. חוויה אותנטית המשלבת תרבות עתיקה עם טבע פראי.',
                'מסע מעמיק אל הלב, הרוח, הטעמים והצבעים של תת-היבשת המרתקת. חוויה של פעם בחיים שמשלבת מקדשים, שווקים ססגוניים ונופים מרהיבים.',
                'גלו את קסמה של תרבות עתיקה ששרדה אלפי שנים. בין מקדשים מפוארים, כפרים מסורתיים וטבע בראשיתי.',
                'הרפתקה אסייתית אמיתית: טבע פראי, מסורות עתיקות, טעמים אקזוטיים ואנשים חמים. מסע שישנה את השקפת עולמכם.',
                'חוויה רוחנית ותרבותית עמוקה בין הרים מושלגים, עמקים ירוקים ועיירות קסומות. מסע אל נוף הנשמה.',
            ],
            Continent.AFRICA: [
                'מסע אל הלב הפועם של היבשת הפראית. ספארי מרהיב, שקיעות אדומות, עולם חי עשיר וטבע בראשיתי שלא נגע בו אדם.',
                'חוויה אפריקאית אמיתית: בין סוואנות אינסופיות, חיות בר מרהיבות ותרבויות שבטיות עתיקות. טבע פראי שאין כמוהו.',
                'גלו את קסם המדבר האפריקאי, דיונות זהב אינסופיות, שבטים נומדיים ושקיעות עוצרות נשימה. מסע אל עבר רחוק.',
                'ספארי פוטוגרפי מרהיב ביבשת הקסומה. בין חמשת הגדולים, נופים דרמטיים ושמורות טבע בראשיתיות.',
                'מסע אל מעמקי אפריקה המסתורית: תרבות עשירה, טבע פראי, מסורות עתיקות וחוויות שאי אפשר לשכוח.',
            ],
            Continent.EUROPE: [
                'מסע תרבותי מרתק בין ארמונות מפוארים, כנסיות גותיות, מוזיאונים עשירים וקפאים אינטימיים. אירופה במיטבה.',
                'גלו את קסמה של היבשת העתיקה: אדריכלות מרהיבה, אמנות מופתית, קולינריה מעודנת וטבע מגוון.',
                'צפון איטליה בחג המולד – שלג, אורות וריחות מאגדה חורפית. חוויה קסומה בלב אירופה הרומנטית.',
                'מסע היסטורי מעמיק בין ערים עתיקות, אתרי מורשת עולמית וסיפורים שעיצבו את העולם המודרני.',
                'חוויה אירופאית משולבת: בין נופי הרים מרהיבים, כרמים ירוקים, עיירות קסומות ותרבות עשירה בת אלפי שנים.',
            ],
            Continent.SOUTH_AMERICA: [
                'הרפתקה של פעם בחיים ביבשת הססגונית בעולם – טבע פראי, תרבויות מרתקות, ערים תוססות ומסע רב-רבדים אל נופים, טעמים וסיפורים שאין דומים להם.',
                'מסע אל לב יער הגשם האמזוני, בין עצים עתיקים, חיות בר נדירות ושבטים ילידים. חוויה בראשיתית שלא תשכחו לעולם.',
                'טרק מרגש בין פסגות האנדים המושלגות, אגמים בצבעי כחול-טורקיז ושרידי תרבות האינקה העתיקה.',
                'קרנבל, סמבה ושמחת חיים: גלו את הצד הססגוני והמרגש של דרום אמריקה בין חופים זהובים, מפלים מרהיבים ותרבות תוססת.',
                'חוויה אקסטרימית בקצה העולם: קרחונים כחולים, פסגות מושלגות, נופים דרמטיים וטבע בראשיתי שעוצר נשימה.',
            ],
            Continent.NORTH_AND_CENTRAL_AMERICA: [
                'גלו את יופי המערב הפראי: קניונים אדומים, נופים אינסופיים, פארקים לאומיים מרהיבים וטבע מגוון ועשיר.',
                'מסע אל הטבע הצפון-אמריקאי: בין יערות ירוקים עתיקים, אגמים צלולים, הרים מושלגים וחיות בר מרהיבות.',
                'חוויה קנדית אמיתית: טבע בראשיתי, אגמים פיורדים, דובי גריזלי וצפון רחוק שמציע נופים שאי אפשר למצוא בשום מקום אחר.',
                'טרופי קריבי: חופים לבנים, מים טורקיז, שונית אלמוגים צבעונית וג\'ונגלים ירוקים. גן עדן עלי אדמות.',
                'הרי הרוקי במלוא הדרם: פסגות מושלגות, עמקים ירוקים, אגמים צלולים וחיות בר בסביבה הטבעית שלהם.',
            ],
            Continent.OCEANIA: [
                'מסע חד פעמי בין איים וחלומות – שייט מרהיב לגן העדן הטרופי, בין הרי געש ליערות גשם, בין חופים זהובים לתרבות פולינזית חמה.',
                'מסע אל קצה העולם – טבע בראשיתי, נופים דרמטיים, עולם חי נדיר ותרבות מאורית עתיקה. הרפתקה אוסטרלית אמיתית.',
                'גלו את ניו זילנד הקסומה: פיורדים כחולים, הרים מושלגים, גייזרים מפעפעים ונופים שנראים כאילו יצאו מסרט פנטזיה.',
                'שונית המחסום הגדולה: צלילה בין אלמוגים צבעוניים, צבי ים, דולפינים ודגים טרופיים. חוויה תת-ימית בלתי נשכחת.',
                'הרפתקה באוסטרליה הפראית: אאוטבק אדום, חופים לבנים, יערות גשם טרופיים וחיות בר ייחודיות שלא קיימות בשום מקום אחר.',
            ],
            Continent.ANTARCTICA: [
                'מסע אל הקוטב הנצחי – קרחונים כחולים מרהיבים, פינגווינים באלפים, כלבי ים וטבע קפוא בראשיתי. הרפתקה בקצה העולם.',
                'חוויה קוטבית אמיתית ביבשת הלבנה: שדות קרח אינסופיים, הרי קרח מרהיבים ושקט מוחלט. מסע שיגדיר את המושג הרפתקה.',
                'שייט קוטבי מרגש בין קרחונים צפים, מפרצונים קפואים ומושבות פינגווינים ענקיות. חוויה של פעם בחיים.',
                'אנטארקטיקה – היבשת האחרונה: טבע בראשיתי קפוא, חיות בר ייחודיות ונופים מהעולם הבא. מסע אקסטרימי שרק אמיצים מעזים.',
                'מסע פוטוגרפי לקצה הדרומי: קרחונים בצבעי כחול-לבן, עולם חי קוטבי וזריחות שקיעות מאגיות באור הקוטב.',
            ],
        }
        
        # Premium Hebrew Title Prefix Templates
        TITLE_PREFIXES = [
            'הקסם של',
            'מסע אל',
            'גלה את',
            'חוויה ב',
            'הרפתקה ב',
            'פלאי',
            'אוצרות',
            'סיור מעמיק ב',
            'טיול מקיף ב',
            'מסע תרבותי ב',
        ]
        
        # Price ranges by continent (in USD)
        CONTINENT_PRICE_RANGES = {
            Continent.AFRICA: (3000, 8000),
            Continent.ASIA: (2500, 6000),
            Continent.EUROPE: (2000, 5000),
            Continent.NORTH_AND_CENTRAL_AMERICA: (3000, 7000),
            Continent.SOUTH_AMERICA: (3500, 8000),
            Continent.OCEANIA: (5000, 12000),
            Continent.ANTARCTICA: (10000, 20000),
        }
        
        trips_to_generate = []
        
        # STEP 1: Ensure EVERY country gets at least ONE trip
        print(f"Creating base trips for {len(all_countries)} countries...")
        for country in all_countries:
            trips_to_generate.append(country)
        
        # STEP 2: Fill remaining slots randomly to reach 300
        target_count = 300
        remaining = target_count - len(trips_to_generate)
        print(f"Adding {remaining} additional random trips...")
        for _ in range(remaining):
            trips_to_generate.append(random.choice(all_countries))
        
        # STEP 3: Generate trips with premium content
        print(f"Generating {len(trips_to_generate)} trips with premium Hebrew content...")
        
        for idx, country in enumerate(trips_to_generate, 1):
            continent = country.continent
            
            # Generate realistic dates (1-18 months from now, 5-30 days duration)
            days_from_now = random.randint(30, 540)
            start_date = datetime.now().date() + timedelta(days=days_from_now)
            duration = random.randint(5, 30)  # Updated to 5-30 days
            end_date = start_date + timedelta(days=duration)
            
            # Generate price ($2,000-$15,000, must end in 0)
            base_price = random.randint(200, 1500) * 10  # Always ends in 0
            single_supplement = base_price * random.uniform(0.15, 0.25)
            
            # Generate capacity
            max_capacity = random.choice([12, 15, 18, 20, 24, 25, 30])
            spots_left = random.randint(0, max_capacity)
            
            # Determine status based on spots left (25% LAST_PLACES frequency)
            if spots_left == 0:
                status = TripStatus.FULL
            elif spots_left <= 3:
                status = TripStatus.LAST_PLACES
            elif spots_left >= max_capacity * 0.8:
                status = TripStatus.OPEN
            else:
                # 25% chance for LAST_PLACES, 50% GUARANTEED, 25% OPEN
                rand = random.random()
                if rand < 0.25:
                    status = TripStatus.LAST_PLACES
                elif rand < 0.75:
                    status = TripStatus.GUARANTEED
                else:
                    status = TripStatus.OPEN
            
            # Difficulty level
            difficulty = random.randint(1, 3)
            
            # Select guide
            guide = random.choice(all_guides)
            
            # Generate premium Hebrew title
            template = random.choice(HEBREW_TITLE_TEMPLATES)
            title_he = template.format(country.name_he)
            title = f"Discover {country.name}"
            
            # Generate context-aware descriptions (both English and Hebrew)
            continent_descriptions_he = HEBREW_DESCRIPTIONS.get(continent, HEBREW_DESCRIPTIONS[Continent.ASIA])
            description_he = random.choice(continent_descriptions_he)
            
            # English descriptions mapped by continent
            english_desc_templates = {
                Continent.AFRICA: [
                    f"Explore the wild heart of {country.name}. Experience breathtaking safaris, vibrant cultures, and pristine natural landscapes.",
                    f"An unforgettable African adventure in {country.name}. Witness incredible wildlife, ancient traditions, and dramatic scenery.",
                    f"Discover the magic of {country.name} with expert guides. Safari, culture, and natural wonders await.",
                ],
                Continent.ASIA: [
                    f"Journey through the enchanting landscapes of {country.name}. Experience ancient temples, vibrant markets, and stunning scenery.",
                    f"Immerse yourself in the culture and beauty of {country.name}. A transformative Asian adventure.",
                    f"Explore {country.name}'s hidden treasures. From spiritual sites to natural wonders, every moment is unforgettable.",
                ],
                Continent.EUROPE: [
                    f"Discover the historic charm of {country.name}. Explore magnificent architecture, world-class cuisine, and rich cultural heritage.",
                    f"Experience the best of {country.name}. From medieval towns to modern cities, history comes alive.",
                    f"Journey through {country.name}'s stunning landscapes. Mountains, coastlines, and timeless villages await.",
                ],
                Continent.SOUTH_AMERICA: [
                    f"Adventure awaits in {country.name}. Trek through mountain ranges, explore rainforests, and experience vibrant cultures.",
                    f"Discover the wild beauty of {country.name}. From ancient ruins to natural wonders, every day is extraordinary.",
                    f"Explore {country.name}'s diverse landscapes. Glaciers, jungles, and coastlines offer endless adventure.",
                ],
                Continent.NORTH_AND_CENTRAL_AMERICA: [
                    f"Experience the natural splendor of {country.name}. National parks, stunning coastlines, and rich biodiversity await.",
                    f"Discover {country.name}'s incredible landscapes. From mountains to beaches, adventure is everywhere.",
                    f"Explore the diverse beauty of {country.name}. Wildlife, culture, and breathtaking scenery combine for an unforgettable journey.",
                ],
                Continent.OCEANIA: [
                    f"Journey to the paradise of {country.name}. Pristine beaches, coral reefs, and unique wildlife await.",
                    f"Discover the natural wonders of {country.name}. From tropical islands to dramatic landscapes.",
                    f"Experience {country.name}'s breathtaking beauty. Dive into crystal waters and explore untouched nature.",
                ],
                Continent.ANTARCTICA: [
                    f"Venture to the frozen continent. Witness massive glaciers, penguin colonies, and pristine polar wilderness.",
                    f"Experience Antarctica's otherworldly beauty. Ice formations, wildlife, and endless white landscapes.",
                    f"Journey to the ends of the Earth. Antarctica offers the ultimate polar expedition.",
                ],
            }
            
            english_templates = english_desc_templates.get(continent, english_desc_templates[Continent.ASIA])
            description = random.choice(english_templates)
            
            # Create trip
            trip = Trip(
                title=title,
                title_he=title_he,
                description=description,
                description_he=description_he,
                start_date=start_date,
                end_date=end_date,
                price=base_price,
                single_supplement_price=single_supplement,
                max_capacity=max_capacity,
                spots_left=spots_left,
                status=status,
                difficulty_level=difficulty,
                country_id=country.id,
                guide_id=guide.id
            )
            session.add(trip)
            session.flush()  # Get trip ID
            
            # Assign tags with smart logic
            # 1. Mandatory: ONE TYPE tag
            type_tag = random.choice(type_tags)
            trip_tag_type = TripTag(trip_id=trip.id, tag_id=type_tag.id)
            session.add(trip_tag_type)
            
            # 2. Optional: 1-3 THEME tags (continent-appropriate)
            continent_themes = CONTINENT_THEME_MAPPING.get(continent, [])
            available_theme_tags = [t for t in theme_tags if t.name in continent_themes]
            
            if available_theme_tags:
                num_themes = random.randint(1, min(3, len(available_theme_tags)))
                selected_themes = random.sample(available_theme_tags, num_themes)
                
                for theme_tag in selected_themes:
                    trip_tag_theme = TripTag(trip_id=trip.id, tag_id=theme_tag.id)
                    session.add(trip_tag_theme)
            
            if (idx % 50 == 0):
                print(f"  ... {idx} trips created")
        
        session.commit()
        trip_count = session.query(Trip).count()
        print(f"Generated {trip_count} trips with premium Hebrew content")
        
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        session.rollback()
        raise
    
    finally:
        session.close()


if __name__ == '__main__':
    seed_database()
