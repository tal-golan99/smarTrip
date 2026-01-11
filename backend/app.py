"""
SmartTrip Flask API - Main Application
Smart Recommendation Engine for Niche Travel
"""

import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from database import init_db, db_session
# V2 Migration: Use V2 models for shared entities (Country, Guide, Tag, TripType)
# V1 Trip model is deprecated - frontend uses V2 TripTemplate/TripOccurrence
from models_v2 import Country, Guide, Tag, TripType, TripOccurrence, TripTemplate, TripStatus
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
allowed_origins_str = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000')
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',')]  # Clean whitespace

# Log CORS configuration for debugging (only in production to help troubleshoot)
if os.getenv('FLASK_ENV') == 'production':
    print(f"[CORS] Production mode - Allowing origins: {allowed_origins}", flush=True)
    print(f"[CORS] ALLOWED_ORIGINS env var: {allowed_origins_str}", flush=True)

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
    """Health check endpoint - V2 Schema"""
    try:
        # V2 Migration: Use V2 models (TripOccurrence instead of Trip)
        occurrence_count = db_session.query(TripOccurrence).count()
        template_count = db_session.query(TripTemplate).count()
        country_count = db_session.query(Country).count()
        guide_count = db_session.query(Guide).count()
        tag_count = db_session.query(Tag).count()
        trip_type_count = db_session.query(TripType).count()
        return jsonify({
            'status': 'healthy',
            'service': 'SmartTrip API',
            'version': '2.0.0',
            'schema': 'V2 (Templates + Occurrences)',
            'database': {
                'trip_occurrences': occurrence_count,
                'trip_templates': template_count,
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
    """
    Seed database with programmatically generated data (DEVELOPMENT ONLY).
    
    This endpoint is restricted to development environments only.
    Production should use Supabase data directly.
    
    Use this for local development/testing with empty database.
    """
    # Restrict to development only
    is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('ENV') == 'production'
    
    if is_production:
        return jsonify({
            'success': False,
            'error': 'This endpoint is disabled in production. Use Supabase data directly.'
        }), 403
    
    try:
        import sys
        import os
        # Add scripts to path for import
        scripts_path = os.path.join(os.path.dirname(__file__), 'scripts')
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        from seed import seed_database  # type: ignore[import-untyped]
        
        print("[SEED] Seeding database with programmatically generated data (DEV ONLY)", flush=True)
        seed_database()
        
        # V2 Migration: Count V2 models instead of V1 Trip
        occurrence_count = db_session.query(TripOccurrence).count()
        template_count = db_session.query(TripTemplate).count()
        
        return jsonify({
            'success': True,
            'message': 'Database seeded successfully with generated data (DEV ONLY)',
            'trip_templates': template_count,
            'trip_occurrences': occurrence_count,
            'note': 'This endpoint is for local development only. Production uses Supabase data.'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
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
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response
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
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response
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
# PIXABAY IMAGE API ENDPOINT
# ============================================

# In-memory cache for country images (simple dict)
# Key: country name (normalized), Value: {url: str, expires_at: datetime}
_country_image_cache = {}

def _get_pixabay_image_url(country_name: str, width: int = 1200, height: int = 600) -> str:
    """
    Fetch landscape image URL from Pixabay API for a country.
    
    Each country gets a different image by using country-specific search query.
    Same country always gets the same image (deterministic, cache-friendly).
    
    Returns placeholder URL if API fails or key is missing.
    """
    pixabay_key = os.getenv('PIXABAY_API_KEY')
    
    if not pixabay_key:
        print(f"[PIXABAY] No API key, using placeholder for {country_name}", flush=True)
        return f"https://placehold.co/{width}x{height}/4A90E2/FFFFFF?text={requests.utils.quote(country_name)}"
    
    # Country-specific query: country name + landscape
    # Different countries = different queries = different images automatically
    query = f"{country_name} landscape"
    pixabay_url = "https://pixabay.com/api/"
    
    params = {
        'key': pixabay_key,
        'q': query,
        'image_type': 'photo',
        'category': 'places',
        'safesearch': 'true',
        'orientation': 'horizontal',
        'min_width': width,
        'per_page': 1,  # Only need first result
        'order': 'popular'
    }
    
    try:
        response = requests.get(pixabay_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        hits = data.get('hits', [])
        if hits:
            # Use first result (best/most popular match for this country)
            selected = hits[0]
            image_url = selected.get('webformatURL') or selected.get('largeImageURL')
            if image_url:
                print(f"[PIXABAY] '{country_name}': found image (ID: {selected.get('id')})", flush=True)
                return image_url
        
        # No results - try fallback query
        fallback_query = f"{country_name} nature"
        params['q'] = fallback_query
        response = requests.get(pixabay_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        hits = data.get('hits', [])
        if hits:
            selected = hits[0]
            image_url = selected.get('webformatURL') or selected.get('largeImageURL')
            if image_url:
                print(f"[PIXABAY] '{country_name}': found image with fallback query '{fallback_query}' (ID: {selected.get('id')})", flush=True)
                return image_url
        
        # All queries failed - use placeholder
        print(f"[PIXABAY] No images found for '{country_name}'", flush=True)
        return f"https://placehold.co/{width}x{height}/4A90E2/FFFFFF?text={requests.utils.quote(country_name)}"
    
    except Exception as e:
        print(f"[PIXABAY] Error fetching image for '{country_name}': {e}", flush=True)
        return f"https://placehold.co/{width}x{height}/4A90E2/FFFFFF?text={requests.utils.quote(country_name)}"


@app.route('/api/images/country/<country_name>', methods=['GET'])
def get_country_image(country_name: str):
    """
    Get landscape image URL for a country using Pixabay API.
    
    Uses in-memory caching with 7-day TTL to reduce API calls.
    Falls back to placeholder if Pixabay API fails or key is missing.
    
    Query params:
    - width: Image width (default: 1200)
    - height: Image height (default: 600)
    - redirect: If 'true', redirects directly to image URL (for <img> src)
    - format: 'json' (default) or 'redirect'
    """
    from datetime import datetime, timedelta
    from flask import redirect
    
    # Get optional width/height params
    width = request.args.get('width', default=1200, type=int)
    height = request.args.get('height', default=600, type=int)
    redirect_param = request.args.get('redirect', 'false').lower() == 'true'
    format_param = request.args.get('format', 'json').lower()
    
    # Normalize country name (lowercase for cache key)
    country_normalized = country_name.strip().lower()
    cache_key = f"{country_normalized}:{width}x{height}"
    
    # Check cache first
    if cache_key in _country_image_cache:
        cached_entry = _country_image_cache[cache_key]
        if cached_entry['expires_at'] > datetime.now():
            print(f"[PIXABAY] Cache hit for {country_name}", flush=True)
            image_url = cached_entry['url']
            
            # If redirect requested, return redirect response
            if redirect_param or format_param == 'redirect':
                return redirect(image_url, code=302)
            
            # Otherwise return JSON
            return jsonify({
                'success': True,
                'url': image_url,
                'country': country_name,
                'cached': True
            }), 200
        else:
            # Cache expired, remove it
            del _country_image_cache[cache_key]
    
    # Cache miss or expired - fetch from Pixabay
    print(f"[PIXABAY] Cache miss for {country_name}, fetching from API", flush=True)
    image_url = _get_pixabay_image_url(country_name, width, height)
    
    # Cache the result (7 days TTL)
    _country_image_cache[cache_key] = {
        'url': image_url,
        'expires_at': datetime.now() + timedelta(days=7)
    }
    
    # Clean up expired cache entries (simple cleanup - remove old entries)
    # This prevents memory leak if many countries are requested
    if len(_country_image_cache) > 100:  # Only clean if cache is large
        now = datetime.now()
        expired_keys = [k for k, v in _country_image_cache.items() if v['expires_at'] <= now]
        for key in expired_keys:
            del _country_image_cache[key]
    
    # If redirect requested, return redirect response
    if redirect_param or format_param == 'redirect':
        return redirect(image_url, code=302)
    
    # Otherwise return JSON
    return jsonify({
        'success': True,
        'url': image_url,
        'country': country_name,
        'cached': False
    }), 200


# ============================================
# DEBUG ENDPOINT (Remove after testing)
# ============================================

@app.route('/api/debug/pixabay-key', methods=['GET'])
def debug_pixabay_key():
    """
    Debug endpoint to check if PIXABAY_API_KEY is loaded.
    Remove this endpoint after confirming everything works.
    """
    key = os.getenv('PIXABAY_API_KEY')
    return jsonify({
        'key_exists': bool(key),
        'key_length': len(key) if key else 0,
        'key_preview': (key[:10] + '...') if key and len(key) > 10 else ('N/A' if not key else key),
        'message': 'Key loaded successfully' if key else 'Key not found - check Render environment variables'
    }), 200


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

# Initialize database on module load
# Wrap in try-except to allow app to start even if DB is temporarily unavailable
with app.app_context():
    try:
        init_db()
        print("[INIT] Database initialized. Data comes from Supabase (DATABASE_URL).")
    except Exception as e:
        print(f"[WARNING] Database initialization failed: {e}")
        print("[WARNING] App will start but database operations may fail until connection is restored.")
        print("[WARNING] This is normal if DATABASE_URL is not set or database is temporarily unavailable.")

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
