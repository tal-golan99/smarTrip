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
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Enable CORS for Next.js frontend
CORS(app, origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000')])


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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'SmartTrip API',
        'version': '1.0.0'
    }), 200


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
    
    Input JSON:
    {
      "selected_countries": [12, 15],     // Optional
      "selected_continents": ["Asia"],    // Optional
      "preferred_type_id": 5,             // Single TYPE tag ID
      "preferred_theme_ids": [10, 12],    // Up to 3 THEME tag IDs
      "min_duration": 7,
      "max_duration": 14,
      "budget": 5000,
      "difficulty": 2,                    // 1-3
      "start_date": "2025-01-01"
    }
    
    Returns: Top 10 trips with match_score (0-100) and match_details
    """
    try:
        from models import TagCategory
        import json
        
        # Get user preferences
        prefs = request.get_json() or {}
        
        # #region agent log
        with open(r'c:\Users\talgo\Documents\פרויקט מערכת המלצות טיולים\trip-recommendations\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({'location': 'app.py:291', 'message': 'Request received', 'data': {'prefs': prefs}, 'timestamp': datetime.now().timestamp() * 1000, 'sessionId': 'debug-session', 'hypothesisId': 'A'}) + '\n')
        # #endregion
        
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
        
        # #region agent log
        with open(r'c:\Users\talgo\Documents\פרויקט מערכת המלצות טיולים\trip-recommendations\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({'location': 'app.py:314', 'message': 'Continents mapped', 'data': {'input': selected_continents_input, 'mapped': selected_continents}, 'timestamp': datetime.now().timestamp() * 1000, 'sessionId': 'debug-session', 'hypothesisId': 'A'}) + '\n')
        # #endregion
        
        # Parse start date
        user_start_date = None
        if start_date_str:
            user_start_date = datetime.fromisoformat(start_date_str).date()
        
        # ========================================
        # STEP A: HARD FILTERING
        # ========================================
        query = db_session.query(Trip)
        
        # Filter by geography (countries OR continents)
        if selected_countries or selected_continents:
            geo_filters = []
            if selected_countries:
                geo_filters.append(Trip.country_id.in_(selected_countries))
            if selected_continents:
                # Join with Country to filter by continent
                query = query.join(Country)
                continent_filter = Country.continent.in_(selected_continents)
                if geo_filters:
                    query = query.filter(or_(*geo_filters, continent_filter))
                else:
                    query = query.filter(continent_filter)
            else:
                query = query.filter(or_(*geo_filters))
        
        # Filter by date
        if user_start_date:
            query = query.filter(Trip.start_date >= user_start_date)
        
        # Filter by status (exclude cancelled and full)
        query = query.filter(
            and_(
                Trip.status != TripStatus.CANCELLED,
                Trip.spots_left > 0
            )
        )
        
        # Get candidate trips
        candidates = query.all()
        
        # #region agent log
        with open(r'c:\Users\talgo\Documents\פרויקט מערכת המלצות טיולים\trip-recommendations\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({'location': 'app.py:367', 'message': 'Query executed', 'data': {'candidate_count': len(candidates), 'sample_trip_id': candidates[0].id if candidates else None}, 'timestamp': datetime.now().timestamp() * 1000, 'sessionId': 'debug-session', 'hypothesisId': 'C'}) + '\n')
        # #endregion
        
        if not candidates:
            return jsonify({
                'success': True,
                'count': 0,
                'data': [],
                'message': 'No trips match your criteria'
            }), 200
        
        # ========================================
        # STEP B: WEIGHTED SCORING (100 points)
        # ========================================
        scored_trips = []
        
        for trip in candidates:
            score = 0
            match_details = []
            
            # Get trip's tags by category
            trip_type_tags = [tt.tag_id for tt in trip.trip_tags if tt.tag.category == TagCategory.TYPE]
            trip_theme_tags = [tt.tag_id for tt in trip.trip_tags if tt.tag.category == TagCategory.THEME]
            
            # 1. TYPE Match (25 pts) - The "Style"
            if preferred_type_id and preferred_type_id in trip_type_tags:
                score += 25
                match_details.append("Perfect Style Match")
            
            # 2. THEME Match (15 pts) - The "Content"
            if preferred_theme_ids:
                theme_matches = len(set(trip_theme_tags) & set(preferred_theme_ids))
                if theme_matches >= 2:
                    score += 15
                    match_details.append(f"Excellent Theme Match ({theme_matches} interests)")
                elif theme_matches == 1:
                    score += 7
                    match_details.append("Good Theme Match")
            
            # 3. Difficulty Match (20 pts)
            if difficulty:
                diff_deviation = abs(trip.difficulty_level - difficulty)
                if diff_deviation == 0:
                    score += 20
                    match_details.append("Perfect Difficulty Level")
                elif diff_deviation == 1:
                    score += 10
                    match_details.append("Close Difficulty Level")
            
            # 4. Duration Match (15 pts)
            trip_duration = (trip.end_date - trip.start_date).days
            if min_duration <= trip_duration <= max_duration:
                score += 15
                match_details.append("Ideal Duration")
            elif abs(trip_duration - min_duration) <= 2 or abs(trip_duration - max_duration) <= 2:
                score += 10
                match_details.append("Good Duration")
            elif abs(trip_duration - min_duration) <= 5 or abs(trip_duration - max_duration) <= 5:
                score += 5
            
            # 5. Budget Match (15 pts)
            if budget:
                trip_price = float(trip.price)
                if trip_price <= budget:
                    score += 15
                    match_details.append("Within Budget")
                elif trip_price <= budget * 1.1:
                    score += 10
                    match_details.append("Slightly Over Budget")
                elif trip_price <= budget * 1.2:
                    score += 5
            
            # 6. Business Logic (10 pts)
            if trip.status in [TripStatus.GUARANTEED, TripStatus.LAST_PLACES]:
                score += 10
                if trip.status == TripStatus.GUARANTEED:
                    match_details.append("Guaranteed Departure")
                else:
                    match_details.append("Last Places Available")
            elif user_start_date and (trip.start_date - user_start_date).days <= 45:
                score += 5
                match_details.append("Departing Soon")
            
            # Add to results
            try:
                trip_dict = trip.to_dict(include_relations=True)
                trip_dict['match_score'] = score
                trip_dict['match_details'] = match_details
                scored_trips.append(trip_dict)
            except Exception as serialize_err:
                # #region agent log
                with open(r'c:\Users\talgo\Documents\פרויקט מערכת המלצות טיולים\trip-recommendations\.cursor\debug.log', 'a', encoding='utf-8') as f:
                    f.write(json.dumps({'location': 'app.py:456', 'message': 'Serialization error', 'data': {'trip_id': trip.id, 'error': str(serialize_err), 'has_guide': trip.guide is not None, 'guide_id': trip.guide_id}, 'timestamp': datetime.now().timestamp() * 1000, 'sessionId': 'debug-session', 'hypothesisId': 'E'}) + '\n')
                # #endregion
                raise
        
        # ========================================
        # STEP C: SORT AND RETURN TOP 10
        # ========================================
        scored_trips.sort(key=lambda x: x['match_score'], reverse=True)
        top_trips = scored_trips[:10]
        
        # #region agent log
        with open(r'c:\Users\talgo\Documents\פרויקט מערכת המלצות טיולים\trip-recommendations\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({'location': 'app.py:473', 'message': 'Returning response', 'data': {'top_trips_count': len(top_trips), 'sample_trip_keys': list(top_trips[0].keys()) if top_trips else []}, 'timestamp': datetime.now().timestamp() * 1000, 'sessionId': 'debug-session', 'hypothesisId': 'D'}) + '\n')
        # #endregion
        
        return jsonify({
            'success': True,
            'count': len(top_trips),
            'total_candidates': len(candidates),
            'data': top_trips,
            'message': f'Found {len(top_trips)} recommended trips'
        }), 200
    
    except Exception as e:
        # #region agent log
        import traceback
        with open(r'c:\Users\talgo\Documents\פרויקט מערכת המלצות טיולים\trip-recommendations\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({'location': 'app.py:487', 'message': 'Backend exception caught', 'data': {'error': str(e), 'error_type': type(e).__name__, 'traceback': traceback.format_exc()}, 'timestamp': datetime.now().timestamp() * 1000, 'sessionId': 'debug-session', 'hypothesisId': 'C'}) + '\n')
        # #endregion
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
# MAIN
# ============================================

if __name__ == '__main__':
    # Initialize database on startup
    with app.app_context():
        init_db()
    
    # Run Flask development server
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"SmartTrip API running on http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/api/health")
    
    app.run(host=host, port=port, debug=True)


