"""
SmartTrip Flask API - Main Application
Smart Recommendation Engine for Niche Travel
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from database import init_db, db_session
from models import Trip, Country, Guide, Tag, TripTag, TripType, TripStatus
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload, selectinload
from datetime import datetime, timedelta, date

# Import recommendation logging (Phase 0)
try:
    from recommender.logging import get_logger, RecommendationLogger
    from recommender.metrics import get_aggregator, MetricsAggregator
    from recommender.evaluation import get_evaluator, ScenarioEvaluator
    LOGGING_ENABLED = True
except ImportError as e:
    print(f"[WARNING] Recommender module not available: {e}")
    LOGGING_ENABLED = False

# Import event tracking (Phase 1)
try:
    from events.api import events_bp
    from events.service import classify_search
    EVENTS_ENABLED = True
except ImportError as e:
    print(f"[WARNING] Events module not available: {e}")
    EVENTS_ENABLED = False

# Import V2 API (Phase 2 - New Schema)
try:
    from api_v2 import api_v2_bp
    API_V2_ENABLED = True
except ImportError as e:
    print(f"[WARNING] API V2 module not available: {e}")
    API_V2_ENABLED = False

# Import Background Scheduler (Phase 1 - Background Jobs)
try:
    from scheduler import start_scheduler, get_scheduler_status
    SCHEDULER_ENABLED = True
except ImportError as e:
    print(f"[WARNING] Scheduler module not available: {e}")
    SCHEDULER_ENABLED = False

# Load environment variables
load_dotenv()

# ============================================
# RECOMMENDATION ALGORITHM CONFIGURATION
# ============================================
# High-precision floating-point scoring weights
# Trip Type is a HARD FILTER (not scored)
# Score is normalized to 0-100 based on ACTIVE criteria only

# Scoring weights dictionary (all float values)
# Raw point accumulation - max possible = 100
SCORING_WEIGHTS = {
    # Base score for passing hard filters
    'BASE_SCORE': 25.0,           # All trips that pass filters start here
    'RELAXED_PENALTY': -20.0,     # Penalty for relaxed/expanded results
    
    # Theme matching (user selected theme interests)
    'THEME_FULL': 25.0,           # Multiple theme matches (2+ themes)
    'THEME_PARTIAL': 12.0,        # Single theme match
    'THEME_PENALTY': -15.0,       # PENALTY: Trip has NONE of user's selected themes
    
    # Difficulty matching (user selected difficulty preference)
    'DIFFICULTY_PERFECT': 15.0,   # Exact difficulty match
    
    # Duration matching (user specified duration range)
    'DURATION_IDEAL': 12.0,       # Within specified range
    'DURATION_GOOD': 8.0,         # Within 4 days of range
    
    # Budget matching (user specified budget)
    'BUDGET_PERFECT': 12.0,       # Within budget
    'BUDGET_GOOD': 8.0,           # Within 110% of budget
    'BUDGET_ACCEPTABLE': 5.0,     # Within 120% of budget
    
    # Urgency/Status bonuses (always active - business priority)
    'STATUS_GUARANTEED': 7.0,     # Guaranteed departure bonus
    'STATUS_LAST_PLACES': 15.0,   # Last places urgency bonus
    'DEPARTING_SOON': 7.0,        # Departing within 30 days
    
    # Geography bonuses (always active when locations selected)
    'GEO_DIRECT_COUNTRY': 15.0,   # Direct country match bonus
    'GEO_CONTINENT': 5.0,         # Continent match bonus
}

# Score thresholds for color coding (used by frontend)
SCORE_THRESHOLDS = {
    'HIGH': 70,    # >= 70 = Turquoise (excellent match)
    'MID': 50,     # >= 50 = Orange (medium match)
    # < 50 = Red (low match)
}

class RecommendationConfig:
    """Configuration for the recommendation scoring algorithm
    
    Note: Trip Type is now a HARD FILTER (not scored).
    Only Theme tags are used for soft scoring.
    """
    
    # Filtering thresholds (not scoring - these are for hard filters)
    DIFFICULTY_TOLERANCE = 1        # Allow +/-1 difficulty level
    BUDGET_MAX_MULTIPLIER = 1.3     # Allow up to 30% over budget
    DURATION_GOOD_DAYS = 4          # "Good" duration within +/-4 days
    DURATION_HARD_FILTER_DAYS = 7   # HARD FILTER: Skip trips outside +/-7 days
    DEPARTING_SOON_DAYS = 30        # Bonus for trips in next 30 days
    
    # Relaxed filtering thresholds (for expanded results)
    RELAXED_DIFFICULTY_TOLERANCE = 2    # Allow +/-2 difficulty levels
    RELAXED_BUDGET_MULTIPLIER = 1.5     # Allow up to 50% over budget
    RELAXED_DURATION_DAYS = 10          # Allow +/-10 days from range
    
    # Result limits
    MAX_RESULTS = 10                # Return top 10 recommendations
    MIN_RESULTS_THRESHOLD = 6       # If results < this, add relaxed results
    THEME_MATCH_THRESHOLD = 2       # Need 2+ themes for full points

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure CORS - Secure by default, configurable via environment
# Set ALLOWED_ORIGINS in .env as comma-separated list: "https://example.com,https://app.example.com"
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
allowed_origins = [origin.strip() for origin in allowed_origins]  # Clean whitespace

CORS(app, resources={
    r"/api/*": {
        "origins": allowed_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Register Phase 1 Events Blueprint
if EVENTS_ENABLED:
    app.register_blueprint(events_bp)
    print("[INIT] Events module registered (Phase 1)")
else:
    print("[INIT] Events module not available")

# Register Phase 2 API V2 Blueprint (New Schema)
if API_V2_ENABLED:
    app.register_blueprint(api_v2_bp, url_prefix='/api/v2')
    print("[INIT] API V2 module registered (Phase 2 - Templates/Occurrences)")
else:
    print("[INIT] API V2 module not available")


# ============================================
# DATABASE LIFECYCLE
# ============================================

@app.before_request
def before_request():
    """Attach database session to request context"""
    pass


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Remove database session at the end of request"""
    db_session.remove()


# ============================================
# HEALTH CHECK
# ============================================

@app.route('/', methods=['GET'])
def root():
    """Root endpoint - basic ping"""
    return jsonify({
        'status': 'ok',
        'service': 'SmartTrip API',
        'message': 'Welcome to SmartTrip API. Use /api/health for detailed status.'
    }), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        trip_count = db_session.query(Trip).count()
        country_count = db_session.query(Country).count()
        guide_count = db_session.query(Guide).count()
        tag_count = db_session.query(Tag).count()
        trip_type_count = db_session.query(TripType).count()
        return jsonify({
            'status': 'healthy',
            'service': 'SmartTrip API',
            'version': '1.0.0',
            'database': {
                'trips': trip_count,
                'countries': country_count,
                'guides': guide_count,
                'tags': tag_count,
                'trip_types': trip_type_count
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/api/seed', methods=['POST'])
def manual_seed():
    """Manually trigger database seeding (use if auto-seed failed)"""
    try:
        from seed import seed_database
        seed_database()
        trip_count = db_session.query(Trip).count()
        return jsonify({
            'success': True,
            'message': 'Database seeded successfully',
            'trips_created': trip_count
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/migrate', methods=['POST'])
def migrate_database():
    """
    Migrate database schema and reseed data.
    WARNING: This drops all existing tables and recreates them.
    Use this when schema changes and you need to update production database.
    """
    try:
        from seed_from_csv import seed_from_csv
        
        print("[MIGRATE] Starting database migration...", flush=True)
        print("[MIGRATE] Importing data from CSV files...", flush=True)
        
        # Seed data from CSV
        seed_from_csv()
        
        # Verify
        trip_count = db_session.query(Trip).count()
        country_count = db_session.query(Country).count()
        
        print(f"[MIGRATE] Migration complete! Trips: {trip_count}, Countries: {country_count}", flush=True)
        
        return jsonify({
            'success': True,
            'message': 'Database migrated and seeded successfully',
            'data': {
                'trips': trip_count,
                'countries': country_count
            }
        }), 200
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[MIGRATE] Error: {error_trace}", flush=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_trace
        }), 500


# ============================================
# LOCATIONS API (Countries + Continents for Frontend)
# ============================================

@app.route('/api/locations', methods=['GET'])
def get_locations():
    """Get ALL countries and continents for the search dropdown - NO FILTERING"""
    try:
        # CRITICAL: Fetch ALL countries from the database
        # Do NOT filter by trips - show every country available
        countries = db_session.query(Country).order_by(Country.name_he).all()
        
        print(f"[LOCATIONS] Found {len(countries)} TOTAL countries in database (no filtering)", flush=True)
        
        # Debug: Log first 5 countries to verify data
        if countries:
            sample_countries = [f"{c.name} ({c.name_he})" for c in countries[:5]]
            print(f"[LOCATIONS] Sample countries: {sample_countries}", flush=True)
        
        # Build continents list from unique values
        # Convert enum to string to avoid comparison issues
        continents_set = set()
        for country in countries:
            if country.continent:
                # Convert Continent enum to its string value
                continent_str = country.continent.name if hasattr(country.continent, 'name') else str(country.continent)
                continents_set.add(continent_str)
        
        # Map continents to Hebrew names
        continent_names_he = {
            'AFRICA': 'אפריקה',
            'ASIA': 'אסיה',
            'EUROPE': 'אירופה',
            'NORTH_AND_CENTRAL_AMERICA': 'צפון ומרכז אמריקה',
            'SOUTH_AMERICA': 'דרום אמריקה',
            'OCEANIA': 'אוקיאניה',
            'ANTARCTICA': 'אנטארקטיקה'
        }
        
        continent_display_names = {
            'AFRICA': 'Africa',
            'ASIA': 'Asia',
            'EUROPE': 'Europe',
            'NORTH_AND_CENTRAL_AMERICA': 'North & Central America',
            'SOUTH_AMERICA': 'South America',
            'OCEANIA': 'Oceania',
            'ANTARCTICA': 'Antarctica'
        }
        
        # Convert enum set to list and sort by display name
        continents_list = []
        for c in sorted(continents_set):  # Sort the set first for consistency
            continents_list.append({
                'value': continent_display_names.get(c, c),
                'nameHe': continent_names_he.get(c, c)
            })
        
        # Convert countries with proper continent string conversion
        countries_list = []
        for c in countries:
            continent_str = c.continent.name if hasattr(c.continent, 'name') else str(c.continent)
            countries_list.append({
                'id': c.id,
                'name': c.name,
                'name_he': c.name_he,
                'continent': continent_display_names.get(continent_str, continent_str)
            })
        
        print(f"[LOCATIONS] Returning {len(countries_list)} countries to frontend", flush=True)
        
        return jsonify({
            'success': True,
            'count': len(countries_list),
            'countries': countries_list,
            'continents': continents_list
        }), 200
    
    except Exception as e:
        print(f"[LOCATIONS] Error: {str(e)}", flush=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# COUNTRIES API
# ============================================

@app.route('/api/countries', methods=['GET'])
def get_countries():
    """Get all countries, optionally filtered by continent"""
    continent = request.args.get('continent')
    
    try:
        query = db_session.query(Country)
        
        # Exclude Antarctica from country list (users select it via continent instead)
        query = query.filter(Country.name != 'Antarctica')
        
        if continent:
            query = query.filter(Country.continent == continent)
        
        countries = query.order_by(Country.name).all()
        
        return jsonify({
            'success': True,
            'count': len(countries),
            'data': [country.to_dict() for country in countries]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/countries/<int:country_id>', methods=['GET'])
def get_country(country_id):
    """Get a specific country by ID"""
    try:
        country = db_session.query(Country).filter(Country.id == country_id).first()
        
        if not country:
            return jsonify({
                'success': False,
                'error': 'Country not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': country.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# GUIDES API
# ============================================

@app.route('/api/guides', methods=['GET'])
def get_guides():
    """Get all active guides"""
    try:
        guides = db_session.query(Guide).filter(Guide.is_active == True).order_by(Guide.name).all()
        
        return jsonify({
            'success': True,
            'count': len(guides),
            'data': [guide.to_dict() for guide in guides]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/guides/<int:guide_id>', methods=['GET'])
def get_guide(guide_id):
    """Get a specific guide by ID"""
    try:
        guide = db_session.query(Guide).filter(Guide.id == guide_id).first()
        
        if not guide:
            return jsonify({
                'success': False,
                'error': 'Guide not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': guide.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# TRIP TYPES API
# ============================================

@app.route('/api/trip-types', methods=['GET'])
def get_trip_types():
    """Get all trip types (trip styles)"""
    try:
        trip_types = db_session.query(TripType).order_by(TripType.name).all()
        
        return jsonify({
            'success': True,
            'count': len(trip_types),
            'data': [trip_type.to_dict() for trip_type in trip_types]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# TAGS API (THEMES ONLY)
# ============================================

@app.route('/api/tags', methods=['GET'])
def get_tags():
    """Get all theme tags (trip interests/themes only)
    
    Note: After schema migration, this endpoint only returns THEME tags.
    For trip styles, use /api/trip-types endpoint.
    """
    try:
        # All tags are now theme tags (category column dropped in V2 migration)
        tags = db_session.query(Tag).order_by(Tag.name).all()
        
        return jsonify({
            'success': True,
            'count': len(tags),
            'data': [tag.to_dict() for tag in tags]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# TRIPS API (V1 - DEPRECATED)
# ============================================
# NOTE: These endpoints are deprecated. Use /api/v2/trips instead.
# V2 provides template/occurrence architecture with better filtering.

def add_deprecation_headers(response, deprecated_endpoint, new_endpoint):
    """Add deprecation headers to response"""
    response.headers['Deprecation'] = 'true'
    response.headers['Sunset'] = '2025-06-01'
    response.headers['Link'] = f'<{new_endpoint}>; rel="successor-version"'
    response.headers['X-Deprecated-Message'] = f'This endpoint is deprecated. Use {new_endpoint} instead.'
    return response


@app.route('/api/trips', methods=['GET'])
def get_trips():
    """
    [DEPRECATED] Get all trips with optional filters and pagination.
    
    Use /api/v2/trips instead for the new template/occurrence architecture.
    """
    try:
        # Get query parameters
        country_id = request.args.get('country_id', type=int)
        guide_id = request.args.get('guide_id', type=int)
        tag_id = request.args.get('tag_id', type=int)
        status = request.args.get('status')
        difficulty = request.args.get('difficulty', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        include_relations = request.args.get('include_relations', 'false').lower() == 'true'
        
        # Pagination parameters
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # Validate pagination
        if limit is not None:
            limit = max(1, min(limit, 1000))  # Clamp between 1 and 1000
        if offset < 0:
            offset = 0
        
        # Build query
        query = db_session.query(Trip)
        
        # Apply filters
        if country_id:
            query = query.filter(Trip.country_id == country_id)
        
        if guide_id:
            query = query.filter(Trip.guide_id == guide_id)
        
        if status:
            query = query.filter(Trip.status == status)
        
        if difficulty:
            query = query.filter(Trip.difficulty_level == difficulty)
        
        if start_date:
            try:
                query = query.filter(Trip.start_date >= datetime.fromisoformat(start_date).date())
            except (ValueError, TypeError):
                pass  # Ignore invalid date
        
        if end_date:
            try:
                query = query.filter(Trip.end_date <= datetime.fromisoformat(end_date).date())
            except (ValueError, TypeError):
                pass  # Ignore invalid date
        
        if tag_id:
            query = query.join(TripTag).filter(TripTag.tag_id == tag_id)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply ordering
        query = query.order_by(Trip.start_date)
        
        # Apply pagination if limit is specified
        if limit is not None:
            query = query.offset(offset).limit(limit)
        
        # Execute query
        trips = query.all()
        
        response = jsonify({
            'success': True,
            'count': len(trips),
            'total': total_count,
            'offset': offset,
            'limit': limit,
            'data': [trip.to_dict(include_relations=include_relations) for trip in trips],
            '_deprecated': True,
            '_deprecation_notice': 'This endpoint is deprecated. Use /api/v2/trips instead.',
            '_successor': '/api/v2/trips'
        })
        return add_deprecation_headers(response, '/api/trips', '/api/v2/trips'), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    """
    [DEPRECATED] Get a specific trip by ID with full details.
    
    Use /api/v2/trips/<id> instead for the new template/occurrence architecture.
    """
    try:
        trip = db_session.query(Trip).filter(Trip.id == trip_id).first()
        
        if not trip:
            return jsonify({
                'success': False,
                'error': 'Trip not found'
            }), 404
        
        response = jsonify({
            'success': True,
            'data': trip.to_dict(include_relations=True),
            '_deprecated': True,
            '_deprecation_notice': 'This endpoint is deprecated. Use /api/v2/trips/<id> instead.',
            '_successor': f'/api/v2/trips/{trip_id}'
        })
        return add_deprecation_headers(response, f'/api/trips/{trip_id}', f'/api/v2/trips/{trip_id}'), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# RECOMMENDATION ENGINE (V1 - DEPRECATED)
# ============================================
# NOTE: This endpoint is deprecated. Use /api/v2/recommendations instead.
# V2 provides full feature parity plus new features like company attribution.

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """
    [DEPRECATED] Smart recommendation engine with weighted scoring (0-100 points).
    
    Use /api/v2/recommendations instead - it provides full feature parity plus:
    - Company attribution
    - Price overrides per occurrence
    - Better relaxed search logic
    - Search classification
    
    STRICT FILTERING: If countries are selected, ONLY trips from those countries are returned.
    
    Input JSON:
    {
      "selected_countries": [12, 15],     // HARD FILTER - only these countries
      "selected_continents": ["Asia"],    // HARD FILTER - only these continents (if no countries)
      "preferred_type_id": 5,             // HARD FILTER - single TripType ID
      "preferred_theme_ids": [10, 12],    // SOFT FILTER - up to 3 THEME tag IDs (for scoring)
      "min_duration": 7,
      "max_duration": 14,
      "budget": 5000,
      "difficulty": 2,                    // 1-3
      "start_date": "2025-01-01"
    }
    
    Returns: Top 10 trips with match_score (0-100) and match_details
    Sorting: Primary by score (desc), Secondary by start_date (soonest first)
    """
    # Initialize logging (Phase 0 metrics)
    request_id = None
    rec_logger = None
    if LOGGING_ENABLED:
        try:
            rec_logger = get_logger()
            request_id = rec_logger.generate_request_id()
            rec_logger.start_request_timer(request_id)
        except Exception as log_err:
            print(f"[WARNING] Logger initialization failed: {log_err}", flush=True)
    
    # Log incoming request for debugging (visible in Render logs)
    print(f"[RECOMMENDATIONS] Incoming request from: {request.remote_addr}", flush=True)
    print(f"[RECOMMENDATIONS] Request JSON: {request.get_json(silent=True)}", flush=True)
    
    try:
        import json
        import re
        
        # ========================================
        # INPUT VALIDATION & SANITIZATION
        # ========================================
        
        def safe_int(value, default=None, min_val=None, max_val=None):
            """Safely convert to int with bounds checking"""
            if value is None:
                return default
            try:
                result = int(float(value))  # Handle "5.0" strings
                if min_val is not None and result < min_val:
                    return default
                if max_val is not None and result > max_val:
                    return default
                return result
            except (TypeError, ValueError):
                return default
        
        def safe_float(value, default=None, min_val=None):
            """Safely convert to float with bounds checking"""
            if value is None:
                return default
            try:
                result = float(value)
                if min_val is not None and result < min_val:
                    return default
                return result
            except (TypeError, ValueError):
                return default
        
        def safe_int_list(value, max_length=100):
            """Safely convert to list of integers"""
            if value is None:
                return []
            if not isinstance(value, list):
                return []
            result = []
            for item in value[:max_length]:  # Limit array size
                try:
                    int_val = int(item)
                    if int_val > 0:  # Only positive IDs
                        result.append(int_val)
                except (TypeError, ValueError):
                    continue
            return result
        
        def sanitize_string(value):
            """Remove potentially dangerous characters from strings"""
            if value is None:
                return None
            if not isinstance(value, str):
                return None
            # Remove HTML tags, script tags, SQL injection patterns
            value = re.sub(r'<[^>]*>', '', value)  # Remove HTML tags
            value = re.sub(r'[;\'"\\]', '', value)  # Remove SQL injection chars
            value = value.strip()
            if len(value) > 100:  # Limit string length
                value = value[:100]
            return value if value else None
        
        def safe_string_list(value, allowed_values=None, max_length=10):
            """Safely convert to list of sanitized strings"""
            if value is None:
                return []
            if not isinstance(value, list):
                return []
            result = []
            for item in value[:max_length]:
                sanitized = sanitize_string(item)
                if sanitized:
                    if allowed_values is None or sanitized in allowed_values:
                        result.append(sanitized)
            return result
        
        # Get user preferences
        prefs = request.get_json(silent=True) or {}
        
        # Validate and sanitize all inputs
        selected_countries = safe_int_list(prefs.get('selected_countries'))
        
        # Valid continents for validation
        valid_continents = [
            'Africa', 'Asia', 'Europe', 'North America', 
            'North & Central America', 'South America', 'Oceania', 'Antarctica'
        ]
        selected_continents_input = safe_string_list(
            prefs.get('selected_continents'), 
            allowed_values=valid_continents
        )
        
        preferred_type_id = safe_int(prefs.get('preferred_type_id'), min_val=1, max_val=100)
        preferred_theme_ids = safe_int_list(prefs.get('preferred_theme_ids'))
        min_duration = safe_int(prefs.get('min_duration'), default=1, min_val=0, max_val=365)
        max_duration = safe_int(prefs.get('max_duration'), default=365, min_val=0, max_val=365)
        budget = safe_float(prefs.get('budget'), min_val=0)
        difficulty = safe_int(prefs.get('difficulty'), min_val=1, max_val=5)
        start_date_str = sanitize_string(prefs.get('start_date'))
        
        # Validate year (must be reasonable range)
        selected_year_raw = prefs.get('year')
        if selected_year_raw == 'all' or selected_year_raw is None:
            selected_year = selected_year_raw
        else:
            year_int = safe_int(selected_year_raw, min_val=2020, max_val=2050)
            selected_year = str(year_int) if year_int else None
        
        # Validate month (1-12 only)
        selected_month_raw = prefs.get('month')
        if selected_month_raw == 'all' or selected_month_raw is None:
            selected_month = selected_month_raw
        else:
            month_int = safe_int(selected_month_raw, min_val=1, max_val=12)
            selected_month = str(month_int) if month_int else None
        
        # Ensure min_duration <= max_duration
        if min_duration > max_duration:
            min_duration, max_duration = max_duration, min_duration
        
        print(f"[RECOMMENDATIONS] Validated - Type: {preferred_type_id}, Budget: {budget}", flush=True)
        print(f"[RECOMMENDATIONS] Validated - Year: {selected_year}, Month: {selected_month}", flush=True)
        print(f"[RECOMMENDATIONS] Validated - Countries: {selected_countries}", flush=True)
        
        # Map continent names to enum values
        continent_mapping = {
            'Africa': 'AFRICA',
            'Asia': 'ASIA',
            'Europe': 'EUROPE',
            'North America': 'NORTH_AMERICA',
            'North & Central America': 'NORTH_AND_CENTRAL_AMERICA',
            'South America': 'SOUTH_AMERICA',
            'Oceania': 'OCEANIA',
            'Antarctica': 'ANTARCTICA'
        }
        selected_continents = [continent_mapping.get(c, c.upper().replace(' ', '_').replace('&', 'AND')) for c in selected_continents_input]
        
        print(f"[RECOMMENDATIONS] Parsed continents: {selected_continents}", flush=True)
        
        # Parse start date safely
        user_start_date = None
        if start_date_str:
            try:
                user_start_date = datetime.fromisoformat(start_date_str).date()
            except (ValueError, TypeError):
                user_start_date = None
        
        # Get total number of trips in database (for UI messaging)
        total_trips_in_db = db_session.query(Trip).filter(
            and_(
                Trip.status != TripStatus.CANCELLED,
                Trip.spots_left > 0,
                Trip.start_date >= datetime.now().date()
            )
        ).count()
        print(f"[RECOMMENDATIONS] Total available trips in database: {total_trips_in_db}", flush=True)
        
        # ========================================
        # STEP A: GEOGRAPHIC FILTERING (UNION LOGIC)
        # ========================================
        # PERFORMANCE FIX: Eagerly load relationships to avoid N+1 queries
        query = db_session.query(Trip).options(
            joinedload(Trip.country),           # Load country data
            joinedload(Trip.guide),             # Load guide data
            selectinload(Trip.trip_tags).joinedload(TripTag.tag)  # Load tags efficiently
        )
        
        # NEW LOGIC: If both countries AND continents are selected, include BOTH (OR/UNION)
        # Example: User selects "Argentina" + "Asia" → Show Argentina trips + All Asia trips
        if selected_countries or selected_continents:
            geo_filters = []
            
            # Add selected countries filter
            if selected_countries:
                geo_filters.append(Trip.country_id.in_(selected_countries))
                print(f"[RECOMMENDATIONS] Including specific countries: {selected_countries}", flush=True)
            
            # Add selected continents filter (all countries in those continents)
            if selected_continents:
                # Need to join with Country table to filter by continent
                query = query.join(Country)
                geo_filters.append(Country.continent.in_(selected_continents))
                print(f"[RECOMMENDATIONS] Including all countries from continents: {selected_continents}", flush=True)
            
            # Apply OR logic: (country_id IN [...]) OR (continent IN [...])
            if len(geo_filters) > 1:
                query = query.filter(or_(*geo_filters))
                print(f"[RECOMMENDATIONS] Applied UNION filter (countries OR continents)", flush=True)
            else:
                query = query.filter(geo_filters[0])
                print(f"[RECOMMENDATIONS] Applied single geographic filter", flush=True)
        
        # Check if Private Groups type is selected
        # First try to get the Private Groups ID from database
        private_groups_type = db_session.query(TripType).filter(TripType.name == 'Private Groups').first()
        private_groups_id = private_groups_type.id if private_groups_type else 10
        is_private_groups = (preferred_type_id == private_groups_id)
        print(f"[RECOMMENDATIONS] Private Groups ID: {private_groups_id}, is_private_groups: {is_private_groups}", flush=True)
        
        # HARD FILTER: Trip Type (if user specified)
        if preferred_type_id:
            query = query.filter(Trip.trip_type_id == preferred_type_id)
            print(f"[RECOMMENDATIONS] Applied trip type filter: {preferred_type_id}", flush=True)
        
        # Define today for use in filtering and scoring
        today = datetime.now().date()
        
        # Filter by date (skip for Private Groups since they have no fixed dates)
        if not is_private_groups:
            query = query.filter(Trip.start_date >= today)
            print(f"[RECOMMENDATIONS] Applied date filter: trips >= {today}", flush=True)
            
            # HARD FILTER: Year and Month (if user specified)
            # This is a strict filter - only trips in the selected timeframe
            if selected_year and selected_year != 'all':
                from sqlalchemy import extract
                year_int = int(selected_year)
                query = query.filter(extract('year', Trip.start_date) == year_int)
                print(f"[RECOMMENDATIONS] HARD FILTER: Year = {year_int}", flush=True)
                
                # If month is also specified, filter by month too
                if selected_month and selected_month != 'all':
                    month_int = int(selected_month)
                    query = query.filter(extract('month', Trip.start_date) == month_int)
                    print(f"[RECOMMENDATIONS] HARD FILTER: Month = {month_int}", flush=True)
            
            # Legacy: If user specified a start date preference (old format)
            if user_start_date and user_start_date > today and not selected_year:
                query = query.filter(Trip.start_date >= user_start_date)
                print(f"[RECOMMENDATIONS] Applied user start date filter: >= {user_start_date}", flush=True)
        else:
            print(f"[RECOMMENDATIONS] Skipped date filter for Private Groups", flush=True)
        
        # Filter by status (exclude cancelled, but include Private Groups with 0 spots)
        if is_private_groups:
            # Private Groups: only exclude cancelled
            query = query.filter(Trip.status != TripStatus.CANCELLED)
            print(f"[RECOMMENDATIONS] Private Groups filter: excluding only cancelled trips", flush=True)
        else:
            # Regular trips: exclude cancelled and full
            query = query.filter(
                and_(
                    Trip.status != TripStatus.CANCELLED,
                    Trip.spots_left > 0
                )
            )
            print(f"[RECOMMENDATIONS] Regular trips filter: excluding cancelled and full trips", flush=True)
        
        # HARD FILTER: Difficulty (if user specified)
        if difficulty is not None:
            # Exclude trips that are off by tolerance level
            tolerance = RecommendationConfig.DIFFICULTY_TOLERANCE
            query = query.filter(
                and_(
                    Trip.difficulty_level >= difficulty - tolerance,
                    Trip.difficulty_level <= difficulty + tolerance
                )
            )
            print(f"[RECOMMENDATIONS] Applied difficulty filter: {difficulty} ±{tolerance}", flush=True)
        
        # HARD FILTER: Budget (if user specified)
        if budget:
            # Exclude trips beyond budget multiplier threshold
            max_price = budget * RecommendationConfig.BUDGET_MAX_MULTIPLIER
            query = query.filter(Trip.price <= max_price)
            print(f"[RECOMMENDATIONS] Applied budget filter: max ${max_price}", flush=True)
        
        # Get candidate trips
        candidates = query.all()
        
        print(f"[RECOMMENDATIONS] Found {len(candidates)} candidate trips after filtering", flush=True)
        
        # NOTE: Don't return early if no candidates - relaxed search may find results!
        # The relaxed search logic (Step D) will handle finding expanded results.
        
        # ========================================
        # STEP B: RAW POINT SCORING (Max = 100)
        # Bonuses - Penalties = Final Score
        # ========================================
        config = RecommendationConfig  # Alias for cleaner code
        weights = SCORING_WEIGHTS      # Alias for weights dictionary
        scored_trips = []
        
        for trip in candidates:
            # Start with BASE_SCORE - trips that pass hard filters already earned points
            current_score = weights['BASE_SCORE']
            match_details = []  # Don't show base score to users - it's implicit
            
            # Get trip's theme tags (relationships already loaded via joinedload - no N+1 queries)
            # Note: All tags are now theme tags after V2 migration (category column dropped)
            trip_theme_tags = []
            try:
                trip_theme_tags = [tt.tag_id for tt in trip.trip_tags if tt.tag]
            except Exception as tag_err:
                print(f"[RECOMMENDATIONS] Tag access error for trip {trip.id}: {tag_err}", flush=True)
            
            # Determine if this is a Private Group trip
            trip_is_private = (trip.trip_type_id == private_groups_id)
            
            # ----------------------------------------
            # 1. THEME SCORING WITH PENALTIES
            # ----------------------------------------
            if preferred_theme_ids:
                theme_matches = len(set(trip_theme_tags) & set(preferred_theme_ids))
                if theme_matches >= config.THEME_MATCH_THRESHOLD:
                    current_score += weights['THEME_FULL']
                    match_details.append(f"Excellent Theme Match ({theme_matches} interests) [+{weights['THEME_FULL']:.0f}]")
                elif theme_matches == 1:
                    current_score += weights['THEME_PARTIAL']
                    match_details.append(f"Good Theme Match [+{weights['THEME_PARTIAL']:.0f}]")
                else:
                    # PENALTY: Trip has NONE of the user's selected themes
                    current_score += weights['THEME_PENALTY']
                    match_details.append(f"No Theme Match [{weights['THEME_PENALTY']:.0f}]")
            
            # ----------------------------------------
            # 2. DIFFICULTY SCORING (only perfect match)
            # ----------------------------------------
            if difficulty is not None:
                diff_deviation = abs(trip.difficulty_level - difficulty)
                if diff_deviation == 0:
                    current_score += weights['DIFFICULTY_PERFECT']
                    match_details.append(f"Perfect Difficulty [+{weights['DIFFICULTY_PERFECT']:.0f}]")
                # Note: Close difficulty (within tolerance) passes hard filter but gets no bonus
            
            # ----------------------------------------
            # 3. DURATION SCORING (skip for Private Groups)
            # Hard filter: 7 days, Good: 4 days
            # ----------------------------------------
            if trip_is_private:
                # Private Groups: flexible duration, give full points
                current_score += weights['DURATION_IDEAL']
                match_details.append(f"Flexible Duration [+{weights['DURATION_IDEAL']:.0f}]")
            else:
                trip_duration = (trip.end_date - trip.start_date).days
                if min_duration <= trip_duration <= max_duration:
                    current_score += weights['DURATION_IDEAL']
                    match_details.append(f"Ideal Duration ({trip_duration}d) [+{weights['DURATION_IDEAL']:.0f}]")
                elif abs(trip_duration - min_duration) <= config.DURATION_GOOD_DAYS or \
                     abs(trip_duration - max_duration) <= config.DURATION_GOOD_DAYS:
                    current_score += weights['DURATION_GOOD']
                    match_details.append(f"Good Duration ({trip_duration}d) [+{weights['DURATION_GOOD']:.0f}]")
                elif abs(trip_duration - min_duration) <= config.DURATION_HARD_FILTER_DAYS or \
                     abs(trip_duration - max_duration) <= config.DURATION_HARD_FILTER_DAYS:
                    # Within hard filter but outside "good" range - no points, but don't skip
                    match_details.append(f"Duration OK ({trip_duration}d)")
                else:
                    # Outside hard filter (7 days) - SKIP this trip
                    continue
            
            # ----------------------------------------
            # 4. BUDGET SCORING
            # ----------------------------------------
            if budget:
                trip_price = float(trip.price)
                if trip_price <= budget:
                    current_score += weights['BUDGET_PERFECT']
                    match_details.append(f"Within Budget [+{weights['BUDGET_PERFECT']:.0f}]")
                elif trip_price <= budget * 1.1:
                    current_score += weights['BUDGET_GOOD']
                    match_details.append(f"Slightly Over (+10%) [+{weights['BUDGET_GOOD']:.0f}]")
                elif trip_price <= budget * 1.2:
                    current_score += weights['BUDGET_ACCEPTABLE']
                    match_details.append(f"Over Budget (+20%) [+{weights['BUDGET_ACCEPTABLE']:.0f}]")
            
            # ----------------------------------------
            # 5. URGENCY/STATUS SCORING
            # ----------------------------------------
            if trip.status == TripStatus.GUARANTEED:
                current_score += weights['STATUS_GUARANTEED']
                match_details.append(f"Guaranteed [+{weights['STATUS_GUARANTEED']:.0f}]")
            elif trip.status == TripStatus.LAST_PLACES:
                current_score += weights['STATUS_LAST_PLACES']
                match_details.append(f"Last Places [+{weights['STATUS_LAST_PLACES']:.0f}]")
            
            # Departing soon bonus - skip for Private Groups
            if not trip_is_private:
                days_until_departure = (trip.start_date - today).days
                if days_until_departure <= config.DEPARTING_SOON_DAYS:
                    current_score += weights['DEPARTING_SOON']
                    match_details.append(f"Soon ({days_until_departure}d) [+{weights['DEPARTING_SOON']:.0f}]")
            
            # ----------------------------------------
            # 6. GEOGRAPHY SCORING
            # ----------------------------------------
            if selected_countries or selected_continents:
                is_direct_country_match = selected_countries and trip.country_id in selected_countries
                is_continent_match = selected_continents and trip.country and trip.country.continent.name in selected_continents
                
                # Special case: Antarctica continent selection = direct country match
                is_antarctica_continent_match = (
                    selected_continents and 'ANTARCTICA' in selected_continents and 
                    trip.country and trip.country.name == 'Antarctica'
                )
                
                if is_direct_country_match or is_antarctica_continent_match:
                    current_score += weights['GEO_DIRECT_COUNTRY']
                    match_details.append(f"Country Match [+{weights['GEO_DIRECT_COUNTRY']:.0f}]")
                elif is_continent_match:
                    current_score += weights['GEO_CONTINENT']
                    match_details.append(f"Continent Match [+{weights['GEO_CONTINENT']:.0f}]")
            
            # ----------------------------------------
            # FINAL SCORE (Raw Points, max 100)
            # Clamp between 0 and 100
            # ----------------------------------------
            final_score = max(0.0, min(100.0, current_score))
            
            # Add to results
            try:
                trip_dict = trip.to_dict(include_relations=True)
                trip_dict['_float_score'] = final_score
                trip_dict['match_score'] = int(round(final_score))  # Integer for UI
                trip_dict['match_details'] = match_details
                # Handle Private Groups with placeholder dates
                if trip.start_date:
                    trip_dict['_sort_date'] = trip.start_date.isoformat()
                else:
                    trip_dict['_sort_date'] = '2099-12-31'
                scored_trips.append(trip_dict)
            except Exception as serialize_err:
                print(f"[RECOMMENDATIONS] Serialization error for trip {trip.id}: {serialize_err}", flush=True)
                continue
        
        # ========================================
        # STEP C: SORT WITH HIGH-PRECISION TIE-BREAKING
        # ========================================
        # Primary: _float_score (descending - highest first) - FLOAT for precision
        # Secondary: start_date (ascending - soonest first)
        scored_trips.sort(key=lambda x: (-x['_float_score'], x['_sort_date']))
        
        # Remove internal fields and get top N results
        top_trips = []
        for trip in scored_trips[:config.MAX_RESULTS]:
            # Remove internal sorting/debugging fields before sending to frontend
            trip.pop('_sort_date', None)
            trip.pop('_float_score', None)
            trip.pop('_raw_points', None)
            trip.pop('_max_points', None)
            trip['is_relaxed'] = False  # Mark as primary result
            top_trips.append(trip)
        
        # ========================================
        # STEP D: RELAXED/EXPANDED RESULTS
        # If we have < MIN_RESULTS_THRESHOLD, fill with relaxed criteria
        # ========================================
        relaxed_trips = []
        if len(top_trips) < config.MIN_RESULTS_THRESHOLD:
            needed = config.MAX_RESULTS - len(top_trips)
            print(f"[RECOMMENDATIONS] Only {len(top_trips)} primary results. Need {needed} more relaxed results.", flush=True)
            
            # Get IDs of already included trips to avoid duplicates
            included_ids = {trip['id'] for trip in top_trips}
            
            # Build relaxed query - same base but looser filters
            relaxed_query = db_session.query(Trip).options(
                joinedload(Trip.country),
                joinedload(Trip.guide),
                selectinload(Trip.trip_tags).joinedload(TripTag.tag)
            )
            
            # RELAXED GEOGRAPHY: Include same continent if user selected specific countries
            if selected_countries or selected_continents:
                geo_filters = []
                
                if selected_countries:
                    # Get continents of selected countries for expansion
                    selected_country_objs = db_session.query(Country).filter(Country.id.in_(selected_countries)).all()
                    expanded_continents = set()
                    for c in selected_country_objs:
                        if c.continent:
                            continent_name = c.continent.name if hasattr(c.continent, 'name') else str(c.continent)
                            expanded_continents.add(continent_name)
                    
                    # Include original countries + all countries from same continents
                    relaxed_query = relaxed_query.join(Country)
                    if expanded_continents:
                        geo_filters.append(Country.continent.in_(list(expanded_continents)))
                        print(f"[RELAXED] Expanded geography to continents: {expanded_continents}", flush=True)
                    else:
                        geo_filters.append(Trip.country_id.in_(selected_countries))
                
                if selected_continents:
                    if not selected_countries:  # Only join if not already joined
                        relaxed_query = relaxed_query.join(Country)
                    geo_filters.append(Country.continent.in_(selected_continents))
                
                if len(geo_filters) > 1:
                    relaxed_query = relaxed_query.filter(or_(*geo_filters))
                elif geo_filters:
                    relaxed_query = relaxed_query.filter(geo_filters[0])
            
            # RELAXED: Do NOT filter by trip type - show all types with a penalty
            # This allows users to discover trips of different types when their preferred type has no matches
            print(f"[RELAXED] Not filtering by trip type (will apply penalty for different types)", flush=True)
            
            # RELAXED DATE FILTER: Expand by 2 months before and after
            if not is_private_groups:
                relaxed_query = relaxed_query.filter(Trip.start_date >= today)
                
                # Get database date boundaries to avoid runtime errors
                from sqlalchemy import func
                min_date_result = db_session.query(func.min(Trip.start_date)).filter(Trip.start_date >= today).scalar()
                max_date_result = db_session.query(func.max(Trip.start_date)).filter(Trip.start_date >= today).scalar()
                
                if selected_year and selected_year != 'all':
                    year_int = int(selected_year)
                    
                    if selected_month and selected_month != 'all':
                        # User selected specific month: expand by 2 months before and after
                        month_int = int(selected_month)
                        
                        # Calculate expanded date range with boundary checking
                        from dateutil.relativedelta import relativedelta
                        center_date = datetime(year_int, month_int, 1).date()
                        
                        # 2 months before
                        start_range = center_date - relativedelta(months=2)
                        # 2 months after (end of that month)
                        end_range = center_date + relativedelta(months=3) - timedelta(days=1)
                        
                        # Clamp to database boundaries
                        if min_date_result:
                            start_range = max(start_range, min_date_result)
                        if max_date_result:
                            end_range = min(end_range, max_date_result)
                        
                        # Ensure start is not in the past
                        start_range = max(start_range, today)
                        
                        relaxed_query = relaxed_query.filter(
                            and_(
                                Trip.start_date >= start_range,
                                Trip.start_date <= end_range
                            )
                        )
                        print(f"[RELAXED] Expanded date range: {start_range} to {end_range}", flush=True)
                    else:
                        # User selected only year: expand by 2 months before and after the year
                        # e.g., 2026 -> Oct 2025 to Feb 2027
                        from dateutil.relativedelta import relativedelta
                        
                        year_start = datetime(year_int, 1, 1).date()
                        year_end = datetime(year_int, 12, 31).date()
                        
                        # 2 months before year start
                        start_range = year_start - relativedelta(months=2)
                        # 2 months after year end
                        end_range = year_end + relativedelta(months=2)
                        
                        # Clamp to database boundaries
                        if min_date_result:
                            start_range = max(start_range, min_date_result)
                        if max_date_result:
                            end_range = min(end_range, max_date_result)
                        
                        # Ensure start is not in the past
                        start_range = max(start_range, today)
                        
                        relaxed_query = relaxed_query.filter(
                            and_(
                                Trip.start_date >= start_range,
                                Trip.start_date <= end_range
                            )
                        )
                        print(f"[RELAXED] Expanded year {year_int} to: {start_range} to {end_range}", flush=True)
            
            # Relaxed status filter
            if is_private_groups:
                relaxed_query = relaxed_query.filter(Trip.status != TripStatus.CANCELLED)
            else:
                relaxed_query = relaxed_query.filter(
                    and_(
                        Trip.status != TripStatus.CANCELLED,
                        Trip.spots_left > 0
                    )
                )
            
            # RELAXED: Difficulty (±2 levels instead of ±1)
            if difficulty is not None:
                tolerance = config.RELAXED_DIFFICULTY_TOLERANCE
                relaxed_query = relaxed_query.filter(
                    and_(
                        Trip.difficulty_level >= difficulty - tolerance,
                        Trip.difficulty_level <= difficulty + tolerance
                    )
                )
            
            # RELAXED: Budget (50% over budget instead of 30%)
            if budget:
                max_price = budget * config.RELAXED_BUDGET_MULTIPLIER
                relaxed_query = relaxed_query.filter(Trip.price <= max_price)
            
            # Exclude already included trips
            relaxed_query = relaxed_query.filter(~Trip.id.in_(included_ids))
            
            # Get relaxed candidates
            relaxed_candidates = relaxed_query.all()
            print(f"[RECOMMENDATIONS] Found {len(relaxed_candidates)} relaxed candidates", flush=True)
            
            # Score relaxed trips (same logic but with penalty)
            relaxed_scored = []
            for trip in relaxed_candidates:
                current_score = weights['BASE_SCORE'] + weights['RELAXED_PENALTY']  # Start lower
                match_details = ["Expanded Result [-20]"]
                
                trip_theme_tags = []
                try:
                    # All tags are theme tags after V2 migration
                    trip_theme_tags = [tt.tag_id for tt in trip.trip_tags if tt.tag]
                except:
                    pass
                
                trip_is_private = (trip.trip_type_id == private_groups_id)
                
                # Apply same scoring logic (abbreviated version)
                if preferred_theme_ids:
                    theme_matches = len(set(trip_theme_tags) & set(preferred_theme_ids))
                    if theme_matches >= config.THEME_MATCH_THRESHOLD:
                        current_score += weights['THEME_FULL']
                    elif theme_matches == 1:
                        current_score += weights['THEME_PARTIAL']
                    else:
                        current_score += weights['THEME_PENALTY']
                
                # RELAXED: Penalty for different trip type
                if preferred_type_id and trip.trip_type_id != preferred_type_id:
                    current_score -= 10.0  # Additional penalty for different type
                    match_details.append("Different Type [-10]")
                
                if difficulty is not None and trip.difficulty_level == difficulty:
                    current_score += weights['DIFFICULTY_PERFECT']
                
                # Duration (relaxed tolerance)
                if trip_is_private:
                    current_score += weights['DURATION_IDEAL']
                else:
                    trip_duration = (trip.end_date - trip.start_date).days
                    if min_duration <= trip_duration <= max_duration:
                        current_score += weights['DURATION_IDEAL']
                    elif abs(trip_duration - min_duration) <= config.RELAXED_DURATION_DAYS or \
                         abs(trip_duration - max_duration) <= config.RELAXED_DURATION_DAYS:
                        current_score += weights['DURATION_GOOD']
                
                # Budget
                if budget:
                    trip_price = float(trip.price)
                    if trip_price <= budget:
                        current_score += weights['BUDGET_PERFECT']
                    elif trip_price <= budget * 1.1:
                        current_score += weights['BUDGET_GOOD']
                
                # Status bonuses
                if trip.status == TripStatus.GUARANTEED:
                    current_score += weights['STATUS_GUARANTEED']
                elif trip.status == TripStatus.LAST_PLACES:
                    current_score += weights['STATUS_LAST_PLACES']
                
                if not trip_is_private:
                    days_until_departure = (trip.start_date - today).days
                    if days_until_departure <= config.DEPARTING_SOON_DAYS:
                        current_score += weights['DEPARTING_SOON']
                
                # Geography
                if selected_countries or selected_continents:
                    is_direct_country_match = selected_countries and trip.country_id in selected_countries
                    is_continent_match = selected_continents and trip.country and trip.country.continent.name in selected_continents
                    
                    # Special case: Antarctica continent selection = direct country match
                    is_antarctica_continent_match = (
                        selected_continents and 'ANTARCTICA' in selected_continents and 
                        trip.country and trip.country.name == 'Antarctica'
                    )
                    
                    if is_direct_country_match or is_antarctica_continent_match:
                        current_score += weights['GEO_DIRECT_COUNTRY']
                    elif is_continent_match:
                        current_score += weights['GEO_CONTINENT']
                
                final_score = max(0.0, min(100.0, current_score))
                
                try:
                    trip_dict = trip.to_dict(include_relations=True)
                    trip_dict['_float_score'] = final_score
                    trip_dict['match_score'] = int(round(final_score))
                    trip_dict['match_details'] = match_details
                    trip_dict['is_relaxed'] = True  # Mark as relaxed result
                    if trip.start_date:
                        trip_dict['_sort_date'] = trip.start_date.isoformat()
                    else:
                        trip_dict['_sort_date'] = '2099-12-31'
                    relaxed_scored.append(trip_dict)
                except Exception as e:
                    print(f"[RECOMMENDATIONS] Relaxed serialization error for trip {trip.id}: {e}", flush=True)
                    continue
            
            # Sort relaxed trips
            relaxed_scored.sort(key=lambda x: (-x['_float_score'], x['_sort_date']))
            
            # Add needed relaxed trips
            for trip in relaxed_scored[:needed]:
                trip.pop('_sort_date', None)
                trip.pop('_float_score', None)
                relaxed_trips.append(trip)
            
            print(f"[RECOMMENDATIONS] Added {len(relaxed_trips)} relaxed results", flush=True)
        
        # Combine primary and relaxed results
        all_trips = top_trips + relaxed_trips
        has_relaxed = len(relaxed_trips) > 0
        
        # If absolutely no results found (both primary and relaxed empty)
        if not all_trips:
            print(f"[RECOMMENDATIONS] No results found from either primary or relaxed search", flush=True)
            response = jsonify({
                'success': True,
                'count': 0,
                'primary_count': 0,
                'relaxed_count': 0,
                'data': [],
                'total_candidates': 0,
                'total_trips': total_trips_in_db,
                'has_relaxed_results': False,
                'score_thresholds': SCORE_THRESHOLDS,
                'show_refinement_message': True,
                'message': 'No trips match your criteria. Try adjusting your preferences.',
                '_deprecated': True,
                '_deprecation_notice': 'This endpoint is deprecated. Use /api/v2/recommendations instead.',
                '_successor': '/api/v2/recommendations'
            })
            return add_deprecation_headers(response, '/api/recommendations', '/api/v2/recommendations'), 200
        
        # Check if top result is NOT high-score (show message for orange AND red)
        top_score = all_trips[0]['match_score'] if all_trips else 0
        show_refinement_message = top_score < SCORE_THRESHOLDS['HIGH']  # Show for both orange and red
        
        print(f"[RECOMMENDATIONS] Returning {len(top_trips)} primary + {len(relaxed_trips)} relaxed = {len(all_trips)} total. Top score: {top_score}", flush=True)
        
        # Classify search type (Phase 1 enhancement)
        search_type = 'exploration'
        if EVENTS_ENABLED:
            try:
                search_type = classify_search(prefs)
            except Exception:
                pass
        
        # Log the request for metrics (Phase 0)
        if LOGGING_ENABLED and rec_logger and request_id:
            try:
                rec_logger.log_request(
                    request_id=request_id,
                    preferences=prefs,
                    results=all_trips,
                    total_candidates=len(candidates),
                    primary_count=len(top_trips),
                    relaxed_count=len(relaxed_trips),
                    session_id=request.headers.get('X-Session-ID'),
                    algorithm_version='v1.0',
                    search_type=search_type,  # Phase 1: exploration or focused_search
                )
            except Exception as log_err:
                print(f"[WARNING] Failed to log request: {log_err}", flush=True)
        
        response = jsonify({
            'success': True,
            'count': len(all_trips),
            'primary_count': len(top_trips),
            'relaxed_count': len(relaxed_trips),
            'total_candidates': len(candidates),
            'total_trips': total_trips_in_db,
            'data': all_trips,
            'has_relaxed_results': has_relaxed,
            'score_thresholds': SCORE_THRESHOLDS,  # Send thresholds for color coding
            'show_refinement_message': show_refinement_message,
            'request_id': request_id,  # Phase 1: For event correlation
            'search_type': search_type,  # Phase 1: exploration or focused_search
            'message': f'Found {len(top_trips)} recommended trips' + (f' + {len(relaxed_trips)} expanded results' if has_relaxed else ''),
            '_deprecated': True,
            '_deprecation_notice': 'This endpoint is deprecated. Use /api/v2/recommendations instead.',
            '_successor': '/api/v2/recommendations'
        })
        return add_deprecation_headers(response, '/api/recommendations', '/api/v2/recommendations'), 200

    except Exception as e:
        import traceback
        print(f"[RECOMMENDATIONS] ERROR: {str(e)}", flush=True)
        print(f"[RECOMMENDATIONS] Traceback: {traceback.format_exc()}", flush=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# ============================================
# METRICS & EVALUATION API (Phase 0)
# ============================================

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """
    Get current recommendation metrics (summary).
    
    Query params:
    - days: Number of days to include (default 7)
    
    Returns aggregated metrics for the time period.
    """
    if not LOGGING_ENABLED:
        return jsonify({
            'success': False,
            'error': 'Metrics module not available'
        }), 503
    
    try:
        days = request.args.get('days', default=7, type=int)
        days = max(1, min(days, 90))  # Clamp between 1 and 90
        
        aggregator = get_aggregator()
        metrics = aggregator.get_current_metrics(days=days)
        
        return jsonify({
            'success': True,
            'data': metrics
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/metrics/daily', methods=['GET'])
def get_daily_metrics():
    """
    Get daily breakdown of recommendation metrics.
    
    Query params:
    - start: Start date (YYYY-MM-DD, default 7 days ago)
    - end: End date (YYYY-MM-DD, default today)
    
    Returns list of daily metrics.
    """
    if not LOGGING_ENABLED:
        return jsonify({
            'success': False,
            'error': 'Metrics module not available'
        }), 503
    
    try:
        # Parse date parameters
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        if request.args.get('start'):
            try:
                start_date = datetime.fromisoformat(request.args.get('start')).date()
            except ValueError:
                pass
        
        if request.args.get('end'):
            try:
                end_date = datetime.fromisoformat(request.args.get('end')).date()
            except ValueError:
                pass
        
        # Limit range to 90 days
        if (end_date - start_date).days > 90:
            start_date = end_date - timedelta(days=90)
        
        aggregator = get_aggregator()
        metrics = aggregator.get_metrics_range(start=start_date, end=end_date)
        
        return jsonify({
            'success': True,
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
            'count': len(metrics),
            'data': metrics
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/metrics/top-searches', methods=['GET'])
def get_top_searches():
    """
    Get top search patterns (continents, types, etc.)
    
    Query params:
    - days: Number of days to analyze (default 7)
    - limit: Max items per category (default 10)
    """
    if not LOGGING_ENABLED:
        return jsonify({
            'success': False,
            'error': 'Metrics module not available'
        }), 503
    
    try:
        days = request.args.get('days', default=7, type=int)
        limit = request.args.get('limit', default=10, type=int)
        
        days = max(1, min(days, 90))
        limit = max(1, min(limit, 50))
        
        aggregator = get_aggregator()
        top_searches = aggregator.get_top_searches(days=days, limit=limit)
        
        return jsonify({
            'success': True,
            'data': top_searches
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/evaluation/run', methods=['POST'])
def run_evaluation():
    """
    Run evaluation scenarios and get results.
    
    Input JSON:
    {
        "category": "core_persona",  // optional filter
        "scenario_ids": [1, 2, 3],   // optional specific IDs
    }
    
    Returns evaluation report with pass/fail status for each scenario.
    """
    if not LOGGING_ENABLED:
        return jsonify({
            'success': False,
            'error': 'Evaluation module not available'
        }), 503
    
    try:
        data = request.get_json(silent=True) or {}
        category = data.get('category')
        scenario_ids = data.get('scenario_ids')
        
        # Validate scenario_ids
        if scenario_ids is not None:
            if not isinstance(scenario_ids, list):
                scenario_ids = None
            else:
                scenario_ids = [int(i) for i in scenario_ids if isinstance(i, (int, str))]
        
        # Get base URL from request
        base_url = request.url_root.rstrip('/')
        
        evaluator = get_evaluator(base_url=base_url)
        report = evaluator.run_all_scenarios(
            category=category,
            scenario_ids=scenario_ids
        )
        
        return jsonify(report), 200
    
    except Exception as e:
        import traceback
        print(f"[EVALUATION] Error: {traceback.format_exc()}", flush=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/evaluation/scenarios', methods=['GET'])
def get_evaluation_scenarios():
    """
    Get available evaluation scenarios.
    
    Query params:
    - category: Filter by category (optional)
    
    Returns list of scenarios without running them.
    """
    if not LOGGING_ENABLED:
        return jsonify({
            'success': False,
            'error': 'Evaluation module not available'
        }), 503
    
    try:
        category = request.args.get('category')
        
        evaluator = get_evaluator()
        scenarios = evaluator.load_scenarios(category=category)
        
        # Return simplified list (without preferences details)
        scenario_list = []
        for s in scenarios:
            scenario_list.append({
                'id': s.get('id'),
                'name': s.get('name'),
                'description': s.get('description'),
                'category': s.get('category'),
                'expected_min_results': s.get('expected_min_results'),
            })
        
        return jsonify({
            'success': True,
            'count': len(scenario_list),
            'data': scenario_list
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/migration/logging', methods=['POST'])
def run_logging_migration():
    """
    Run the database migration to create recommendation logging tables.
    WARNING: This creates new tables. Safe to run multiple times.
    """
    try:
        from migrations import upgrade_logging_tables
        
        print("[MIGRATION] Starting logging tables migration...", flush=True)
        success = upgrade_logging_tables()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Logging tables migration completed successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Migration failed - check logs'
            }), 500
    
    except ImportError:
        # Fallback: run migration directly
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'migrations'))
            
            from migrations import _001_add_recommendation_logging as migration
            success = migration.upgrade()
            
            return jsonify({
                'success': True,
                'message': 'Logging tables migration completed successfully'
            }), 200
        except Exception as e2:
            return jsonify({
                'success': False,
                'error': f'Migration not available: {str(e2)}'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/migration/user-tracking', methods=['POST'])
def run_user_tracking_migration():
    """
    Run the Phase 1 database migration to create user tracking tables.
    Creates: users, sessions, events, trip_interactions tables.
    WARNING: Safe to run multiple times (checks for existing tables).
    """
    try:
        from migrations import upgrade_user_tracking
        
        print("[MIGRATION] Starting user tracking tables migration (Phase 1)...", flush=True)
        success = upgrade_user_tracking()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'User tracking tables migration completed successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Migration failed - check logs'
            }), 500
    
    except ImportError:
        # Fallback: run migration directly
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'migrations'))
            
            from migrations import _002_add_user_tracking as migration
            success = migration.upgrade()
            
            return jsonify({
                'success': True,
                'message': 'User tracking tables migration completed successfully'
            }), 200
        except Exception as e2:
            return jsonify({
                'success': False,
                'error': f'Migration not available: {str(e2)}'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# AUTO-MIGRATION AND AUTO-SEED
# ============================================

def auto_seed_if_empty():
    """Automatically seed the database if no trips exist"""
    try:
        trip_count = db_session.query(Trip).count()
        if trip_count == 0:
            print("\n[AUTO-SEED] Database is empty. Auto-seeding...")
            from seed import seed_database
            seed_database()
            print("[AUTO-SEED] Auto-seeding completed successfully!")
        else:
            print(f"[AUTO-SEED] Database already has {trip_count} trips. Skipping seed.")
    except Exception as e:
        print(f"[AUTO-SEED] Auto-seed check failed: {e}")
        # Don't crash the app if seeding fails
        pass


# ============================================
# V2 SCHEMA MIGRATION ENDPOINT
# ============================================

@app.route('/api/migration/v2-schema', methods=['POST'])
def run_v2_schema_migration():
    """
    Run V2 schema migration (companies + templates/occurrences).
    Call via: POST https://your-backend.onrender.com/api/migration/v2-schema
    Safe to run multiple times.
    """
    results = {'migration_003': None, 'migration_004': None}
    
    try:
        print("[MIGRATION] Starting V2 schema migration...", flush=True)
        
        # Migration 003: Companies
        try:
            from migrations._003_add_companies import upgrade as upgrade_003
            success = upgrade_003()
            results['migration_003'] = 'success' if success else 'failed'
            print(f"[MIGRATION] 003 Companies: {results['migration_003']}", flush=True)
        except Exception as e:
            results['migration_003'] = f'error: {str(e)}'
            print(f"[MIGRATION] 003 error: {e}", flush=True)
        
        # Migration 004: Templates/Occurrences
        try:
            from migrations._004_refactor_trips_to_templates import upgrade as upgrade_004
            success = upgrade_004()
            results['migration_004'] = 'success' if success else 'failed'
            print(f"[MIGRATION] 004 Templates: {results['migration_004']}", flush=True)
        except Exception as e:
            results['migration_004'] = f'error: {str(e)}'
            print(f"[MIGRATION] 004 error: {e}", flush=True)
        
        all_success = all(v == 'success' for v in results.values())
        return jsonify({
            'success': all_success,
            'message': 'V2 migration completed' if all_success else 'Some migrations failed - check results',
            'results': results
        }), 200 if all_success else 500
        
    except Exception as e:
        import traceback
        print(f"[MIGRATION] Error: {traceback.format_exc()}", flush=True)
        return jsonify({'success': False, 'error': str(e), 'results': results}), 500


# ============================================
# SCHEDULER STATUS ENDPOINT
# ============================================

@app.route('/api/scheduler/status', methods=['GET'])
def scheduler_status():
    """Get background scheduler status and job information"""
    if not SCHEDULER_ENABLED:
        return jsonify({
            'success': False,
            'error': 'Scheduler module not available'
        }), 503
    
    try:
        status = get_scheduler_status()
        return jsonify({
            'success': True,
            'data': status
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# MAIN
# ============================================

# Initialize database and auto-seed on module load (for production)
with app.app_context():
    init_db()
    auto_seed_if_empty()

# Start background scheduler (runs in-process with Flask)
# This starts the scheduler when the module is loaded (works with gunicorn)
if SCHEDULER_ENABLED:
    try:
        start_scheduler()
        print("[INIT] Background scheduler started (Phase 1 jobs)")
    except Exception as e:
        print(f"[WARNING] Failed to start scheduler: {e}")
else:
    print("[INIT] Scheduler not available")

if __name__ == '__main__':
    # Run Flask development server
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"SmartTrip API running on http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/api/health")
    print(f"Scheduler Status: http://{host}:{port}/api/scheduler/status")
    
    app.run(host=host, port=port, debug=True)
