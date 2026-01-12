"""
Resources API Endpoints
=======================

Read-only endpoints for countries, guides, trip types, tags, and locations.
"""

from flask import Blueprint, jsonify, request
from app.core.database import db_session, is_database_error
from app.models.trip import Country, Guide, TripType, Tag

resources_bp = Blueprint('resources', __name__)


@resources_bp.route('/api/locations', methods=['GET'])
def get_locations():
    """Get ALL countries and continents for the search dropdown - NO FILTERING"""
    try:
        # CRITICAL: Fetch ALL countries from the database
        # Do NOT filter by trips - show every country available
        # Ensure db_session is bound to the current request context
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
        is_db_error, is_conn_error = is_database_error(e)
        
        if is_conn_error:
            return jsonify({
                'success': False,
                'error': 'Database connection unavailable. Please check your configuration or try again later.'
            }), 503
        elif is_db_error:
            return jsonify({
                'success': False,
                'error': 'Database error occurred. Please try again later.'
            }), 503
        else:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@resources_bp.route('/api/countries', methods=['GET'])
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


@resources_bp.route('/api/countries/<int:country_id>', methods=['GET'])
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
        is_db_error, is_conn_error = is_database_error(e)
        
        if is_conn_error:
            return jsonify({
                'success': False,
                'error': 'Database connection unavailable. Please check your configuration or try again later.'
            }), 503
        elif is_db_error:
            return jsonify({
                'success': False,
                'error': 'Database error occurred. Please try again later.'
            }), 503
        else:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@resources_bp.route('/api/guides', methods=['GET'])
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
        is_db_error, is_conn_error = is_database_error(e)
        
        if is_conn_error:
            return jsonify({
                'success': False,
                'error': 'Database connection unavailable. Please check your configuration or try again later.'
            }), 503
        elif is_db_error:
            return jsonify({
                'success': False,
                'error': 'Database error occurred. Please try again later.'
            }), 503
        else:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@resources_bp.route('/api/guides/<int:guide_id>', methods=['GET'])
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
        is_db_error, is_conn_error = is_database_error(e)
        
        if is_conn_error:
            return jsonify({
                'success': False,
                'error': 'Database connection unavailable. Please check your configuration or try again later.'
            }), 503
        elif is_db_error:
            return jsonify({
                'success': False,
                'error': 'Database error occurred. Please try again later.'
            }), 503
        else:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@resources_bp.route('/api/trip-types', methods=['GET'])
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
        is_db_error, is_conn_error = is_database_error(e)
        
        if is_conn_error:
            return jsonify({
                'success': False,
                'error': 'Database connection unavailable. Please check your configuration or try again later.'
            }), 503
        elif is_db_error:
            return jsonify({
                'success': False,
                'error': 'Database error occurred. Please try again later.'
            }), 503
        else:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@resources_bp.route('/api/tags', methods=['GET'])
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
        is_db_error, is_conn_error = is_database_error(e)
        
        if is_conn_error:
            return jsonify({
                'success': False,
                'error': 'Database connection unavailable. Please check your configuration or try again later.'
            }), 503
        elif is_db_error:
            return jsonify({
                'success': False,
                'error': 'Database error occurred. Please try again later.'
            }), 503
        else:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
