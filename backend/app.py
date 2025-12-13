"""
SmartTrip Flask API - Main Application
Smart Recommendation Engine for Niche Travel
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from database import init_db, db_session
from models import Trip, Country, Guide, Tag, TripTag, TripStatus, TagCategory
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload, selectinload
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# ============================================
# RECOMMENDATION ALGORITHM CONFIGURATION
# ============================================
# Centralized scoring weights (out of 100 total points)
# Modify these values to tune the recommendation algorithm

class RecommendationConfig:
    """Configuration for the recommendation scoring algorithm"""
    
    # Maximum points per category (total = 100)
    TYPE_MATCH_POINTS = 18          # Trip style match (Safari, Cruise, etc.)
    THEME_MATCH_FULL_POINTS = 12    # Multiple theme matches
    THEME_MATCH_PARTIAL_POINTS = 6  # Single theme match
    DIFFICULTY_PERFECT_POINTS = 13  # Exact difficulty match
    DIFFICULTY_CLOSE_POINTS = 7     # Within 1 level
    DIFFICULTY_DEFAULT_POINTS = 7   # No preference specified
    DURATION_IDEAL_POINTS = 11      # Within specified range
    DURATION_GOOD_POINTS = 7        # Within 2 days of range
    DURATION_ACCEPTABLE_POINTS = 4  # Within 5 days of range
    BUDGET_PERFECT_POINTS = 11      # Within budget
    BUDGET_GOOD_POINTS = 7          # Within 110% of budget
    BUDGET_ACCEPTABLE_POINTS = 4    # Within 120% of budget
    
    # Business logic bonuses (can stack, max 22 total)
    STATUS_GUARANTEED_POINTS = 7
    STATUS_LAST_PLACES_POINTS = 15
    DEPARTING_SOON_POINTS = 7       # Leaves within 30 days
    
    # Geography priority boost
    DIRECT_COUNTRY_MATCH_POINTS = 13
    CONTINENT_MATCH_POINTS = 3
    
    # Filtering thresholds
    DIFFICULTY_TOLERANCE = 1        # Allow ±1 difficulty level
    BUDGET_MAX_MULTIPLIER = 1.3     # Allow up to 30% over budget
    DURATION_CLOSE_DAYS = 2         # "Good" duration within ±2 days
    DURATION_ACCEPTABLE_DAYS = 5    # "Acceptable" within ±5 days
    DEPARTING_SOON_DAYS = 30        # Bonus for trips in next 30 days
    
    # Result limits
    MAX_RESULTS = 10                # Return top 10 recommendations
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
    trip_count = db_session.query(Trip).count()
    country_count = db_session.query(Country).count()
    return jsonify({
        'status': 'healthy',
        'service': 'SmartTrip API',
        'version': '1.0.0',
        'database': {
            'trips': trip_count,
            'countries': country_count
        }
    }), 200


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
# TAGS API
# ============================================

@app.route('/api/tags', methods=['GET'])
def get_tags():
    """Get all trip tags/types"""
    try:
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
# TRIPS API
# ============================================

@app.route('/api/trips', methods=['GET'])
def get_trips():
    """Get all trips with optional filters"""
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
            query = query.filter(Trip.start_date >= datetime.fromisoformat(start_date).date())
        
        if end_date:
            query = query.filter(Trip.end_date <= datetime.fromisoformat(end_date).date())
        
        if tag_id:
            query = query.join(TripTag).filter(TripTag.tag_id == tag_id)
        
        # Execute query
        trips = query.order_by(Trip.start_date).all()
        
        return jsonify({
            'success': True,
            'count': len(trips),
            'data': [trip.to_dict(include_relations=include_relations) for trip in trips]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    """Get a specific trip by ID with full details"""
    try:
        trip = db_session.query(Trip).filter(Trip.id == trip_id).first()
        
        if not trip:
            return jsonify({
                'success': False,
                'error': 'Trip not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': trip.to_dict(include_relations=True)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# RECOMMENDATION ENGINE (Weighted Scoring Algorithm)
# ============================================

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """
    Smart recommendation engine with weighted scoring (0-100 points)
    
    STRICT FILTERING: If countries are selected, ONLY trips from those countries are returned.
    
    Input JSON:
    {
      "selected_countries": [12, 15],     // HARD FILTER - only these countries
      "selected_continents": ["Asia"],    // HARD FILTER - only these continents (if no countries)
      "preferred_type_id": 5,             // Single TYPE tag ID
      "preferred_theme_ids": [10, 12],    // Up to 3 THEME tag IDs
      "min_duration": 7,
      "max_duration": 14,
      "budget": 5000,
      "difficulty": 2,                    // 1-3
      "start_date": "2025-01-01"
    }
    
    Returns: Top 10 trips with match_score (0-100) and match_details
    Sorting: Primary by score (desc), Secondary by start_date (soonest first)
    """
    # Log incoming request for debugging (visible in Render logs)
    print(f"[RECOMMENDATIONS] Incoming request from: {request.remote_addr}", flush=True)
    print(f"[RECOMMENDATIONS] Request JSON: {request.get_json(silent=True)}", flush=True)
    
    try:
        import json
        
        # Get user preferences
        prefs = request.get_json() or {}
        
        # Extract preferences with defaults
        selected_countries = prefs.get('selected_countries', [])
        selected_continents_input = prefs.get('selected_continents', [])
        preferred_type_id = prefs.get('preferred_type_id')
        preferred_theme_ids = prefs.get('preferred_theme_ids', [])
        min_duration = prefs.get('min_duration', 1)
        max_duration = prefs.get('max_duration', 365)
        budget = prefs.get('budget')
        difficulty = prefs.get('difficulty')
        start_date_str = prefs.get('start_date')
        
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
        
        print(f"[RECOMMENDATIONS] Parsed - Countries: {selected_countries}, Continents: {selected_continents}", flush=True)
        
        # Parse start date
        user_start_date = None
        if start_date_str:
            user_start_date = datetime.fromisoformat(start_date_str).date()
        
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
        
        # Filter by date (only show future trips)
        today = datetime.now().date()
        query = query.filter(Trip.start_date >= today)
        
        # If user specified a start date preference, use that instead
        if user_start_date and user_start_date > today:
            query = query.filter(Trip.start_date >= user_start_date)
        
        # Filter by status (exclude cancelled and full)
        query = query.filter(
            and_(
                Trip.status != TripStatus.CANCELLED,
                Trip.spots_left > 0
            )
        )
        
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
        
        if not candidates:
            return jsonify({
                'success': True,
                'count': 0,
                'data': [],
                'total_candidates': 0,
                'total_trips': total_trips_in_db,
                'message': 'No trips match your criteria'
            }), 200
        
        # ========================================
        # STEP B: WEIGHTED SCORING (100 points MAX - NORMALIZED)
        # ========================================
        config = RecommendationConfig  # Alias for cleaner code
        scored_trips = []
        
        for trip in candidates:
            score = 0
            match_details = []
            
            # Get trip's tags by category (relationships already loaded via joinedload - no N+1 queries)
            trip_type_tags = [tt.tag_id for tt in trip.trip_tags if tt.tag.category == TagCategory.TYPE]
            trip_theme_tags = [tt.tag_id for tt in trip.trip_tags if tt.tag.category == TagCategory.THEME]
            
            # 1. TYPE Match - The "Style"
            if preferred_type_id and preferred_type_id in trip_type_tags:
                score += config.TYPE_MATCH_POINTS
                match_details.append("Perfect Style Match")
            
            # 2. THEME Match - The "Content"
            if preferred_theme_ids:
                theme_matches = len(set(trip_theme_tags) & set(preferred_theme_ids))
                if theme_matches >= config.THEME_MATCH_THRESHOLD:
                    score += config.THEME_MATCH_FULL_POINTS
                    match_details.append(f"Excellent Theme Match ({theme_matches} interests)")
                elif theme_matches == 1:
                    score += config.THEME_MATCH_PARTIAL_POINTS
                    match_details.append("Good Theme Match")
            
            # 3. Difficulty Match - HARD FILTERED (only within tolerance remains)
            if difficulty is not None:
                diff_deviation = abs(trip.difficulty_level - difficulty)
                if diff_deviation == 0:
                    score += config.DIFFICULTY_PERFECT_POINTS
                    match_details.append("Perfect Difficulty Level")
                elif diff_deviation <= config.DIFFICULTY_TOLERANCE:
                    score += config.DIFFICULTY_CLOSE_POINTS
                    match_details.append("Close Difficulty Level")
            else:
                # No difficulty preference - give baseline points to all trips
                score += config.DIFFICULTY_DEFAULT_POINTS
            
            # 4. Duration Match
            trip_duration = (trip.end_date - trip.start_date).days
            if min_duration <= trip_duration <= max_duration:
                score += config.DURATION_IDEAL_POINTS
                match_details.append("Ideal Duration")
            elif abs(trip_duration - min_duration) <= config.DURATION_CLOSE_DAYS or \
                 abs(trip_duration - max_duration) <= config.DURATION_CLOSE_DAYS:
                score += config.DURATION_GOOD_POINTS
                match_details.append("Good Duration")
            elif abs(trip_duration - min_duration) <= config.DURATION_ACCEPTABLE_DAYS or \
                 abs(trip_duration - max_duration) <= config.DURATION_ACCEPTABLE_DAYS:
                score += config.DURATION_ACCEPTABLE_POINTS
            else:
                # Outside acceptable range - SKIP this trip
                continue
            
            # 5. Budget Match - HARD FILTERED (max over budget already applied)
            if budget:
                trip_price = float(trip.price)
                if trip_price <= budget:
                    score += config.BUDGET_PERFECT_POINTS
                    match_details.append("Within Budget")
                elif trip_price <= budget * 1.1:
                    score += config.BUDGET_GOOD_POINTS
                    match_details.append("Slightly Over Budget")
                elif trip_price <= budget * 1.2:
                    score += config.BUDGET_ACCEPTABLE_POINTS
                    match_details.append("Close to Budget")
                # Trips over max multiplier are already filtered out
            
            # 6. Business Logic - Status-based scoring
            if trip.status == TripStatus.GUARANTEED:
                score += config.STATUS_GUARANTEED_POINTS
                match_details.append(f"Guaranteed Departure (+{config.STATUS_GUARANTEED_POINTS})")
            elif trip.status == TripStatus.LAST_PLACES:
                score += config.STATUS_LAST_PLACES_POINTS
                match_details.append(f"Last Places Available (+{config.STATUS_LAST_PLACES_POINTS})")
            
            # Departing soon bonus (can stack with status)
            days_until_departure = (trip.start_date - today).days
            if days_until_departure <= config.DEPARTING_SOON_DAYS:
                score += config.DEPARTING_SOON_POINTS
                match_details.append(f"Departing Soon (+{config.DEPARTING_SOON_POINTS})")
            
            # 7. Geography Priority Boost
            # This ensures directly selected countries appear FIRST in results
            is_direct_country_match = selected_countries and trip.country_id in selected_countries
            is_continent_match = selected_continents and trip.country and trip.country.continent.name in selected_continents
            
            if is_direct_country_match:
                score += config.DIRECT_COUNTRY_MATCH_POINTS
                match_details.append(f"Direct Country Match (+{config.DIRECT_COUNTRY_MATCH_POINTS})")
            elif is_continent_match:
                score += config.CONTINENT_MATCH_POINTS
                match_details.append(f"Continent Match (+{config.CONTINENT_MATCH_POINTS})")
            
            # Add to results with start_date for secondary sorting
            try:
                trip_dict = trip.to_dict(include_relations=True)
                trip_dict['match_score'] = score
                trip_dict['match_details'] = match_details
                trip_dict['_sort_date'] = trip.start_date.isoformat()  # For sorting
                scored_trips.append(trip_dict)
            except Exception as serialize_err:
                print(f"[RECOMMENDATIONS] Serialization error for trip {trip.id}: {serialize_err}", flush=True)
                raise
        
        # ========================================
        # STEP C: SORT WITH TIE-BREAKING AND RETURN TOP RESULTS
        # ========================================
        # Primary: match_score (descending - highest first)
        # Secondary: start_date (ascending - soonest first)
        scored_trips.sort(key=lambda x: (-x['match_score'], x['_sort_date']))
        
        # Remove internal sort field and get top N results
        top_trips = []
        for trip in scored_trips[:config.MAX_RESULTS]:
            trip.pop('_sort_date', None)
            top_trips.append(trip)
        
        print(f"[RECOMMENDATIONS] Returning {len(top_trips)} trips", flush=True)
        
        return jsonify({
            'success': True,
            'count': len(top_trips),
            'total_candidates': len(candidates),
            'total_trips': total_trips_in_db,
            'data': top_trips,
            'message': f'Found {len(top_trips)} recommended trips'
        }), 200
    
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
# MAIN
# ============================================

# Initialize database and auto-seed on module load (for production)
with app.app_context():
    init_db()
    auto_seed_if_empty()

if __name__ == '__main__':
    # Run Flask development server
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"SmartTrip API running on http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/api/health")
    
    app.run(host=host, port=port, debug=True)
