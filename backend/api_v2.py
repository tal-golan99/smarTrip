"""
SmartTrip API V2 - Using New Schema (Templates + Occurrences)
=============================================================

This module provides API endpoints that use the refactored database schema:
- TripTemplate: The "what" of a trip (description, pricing, difficulty)
- TripOccurrence: The "when" of a trip (dates, guide, availability)

Register this blueprint in app.py:
    from api_v2 import api_v2_bp
    app.register_blueprint(api_v2_bp, url_prefix='/api/v2')
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import and_, or_, extract, func
from sqlalchemy.orm import joinedload, selectinload
from datetime import datetime, timedelta

from database import db_session
from models_v2 import (
    Company, TripTemplate, TripOccurrence, TripTemplateTag, TripTemplateCountry,
    Country, Guide, TripType, Tag, TripStatus, Continent
)

api_v2_bp = Blueprint('api_v2', __name__)


# ============================================
# COMPANIES API
# ============================================

@api_v2_bp.route('/companies', methods=['GET'])
def get_companies():
    """Get all active companies"""
    try:
        companies = db_session.query(Company).filter(
            Company.is_active == True
        ).order_by(Company.name).all()
        
        return jsonify({
            'success': True,
            'count': len(companies),
            'data': [c.to_dict() for c in companies]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v2_bp.route('/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """Get a specific company with its trip templates"""
    try:
        company = db_session.query(Company).filter(
            Company.id == company_id
        ).first()
        
        if not company:
            return jsonify({'success': False, 'error': 'Company not found'}), 404
        
        data = company.to_dict()
        
        # Include template count
        template_count = db_session.query(TripTemplate).filter(
            TripTemplate.company_id == company_id,
            TripTemplate.is_active == True
        ).count()
        data['templateCount'] = template_count
        
        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# TRIP TEMPLATES API
# ============================================

@api_v2_bp.route('/templates', methods=['GET'])
def get_templates():
    """
    Get trip templates with optional filters.
    
    Query params:
    - company_id: Filter by company
    - trip_type_id: Filter by trip type
    - country_id: Filter by country (via multi-country support)
    - difficulty: Filter by difficulty level
    - include_occurrences: Include upcoming occurrences (default: false)
    - limit: Max results (default: 50)
    - offset: Pagination offset
    """
    try:
        query = db_session.query(TripTemplate).options(
            joinedload(TripTemplate.company),
            joinedload(TripTemplate.trip_type),
            joinedload(TripTemplate.primary_country),
        ).filter(TripTemplate.is_active == True)
        
        # Filters
        if request.args.get('company_id'):
            query = query.filter(TripTemplate.company_id == int(request.args.get('company_id')))
        
        if request.args.get('trip_type_id'):
            query = query.filter(TripTemplate.trip_type_id == int(request.args.get('trip_type_id')))
        
        if request.args.get('difficulty'):
            query = query.filter(TripTemplate.difficulty_level == int(request.args.get('difficulty')))
        
        if request.args.get('country_id'):
            country_id = int(request.args.get('country_id'))
            query = query.join(TripTemplateCountry).filter(
                TripTemplateCountry.country_id == country_id
            )
        
        # Pagination
        total = query.count()
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))
        
        templates = query.order_by(TripTemplate.title).offset(offset).limit(limit).all()
        
        # Include occurrences if requested
        include_occurrences = request.args.get('include_occurrences', 'false').lower() == 'true'
        
        results = []
        for template in templates:
            data = template.to_dict(include_relations=True)
            
            if include_occurrences:
                # Get upcoming occurrences
                occurrences = db_session.query(TripOccurrence).filter(
                    TripOccurrence.trip_template_id == template.id,
                    TripOccurrence.start_date >= datetime.now().date(),
                    TripOccurrence.status != 'Cancelled'
                ).order_by(TripOccurrence.start_date).limit(5).all()
                
                data['upcomingOccurrences'] = [o.to_dict() for o in occurrences]
            
            results.append(data)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'total': total,
            'offset': offset,
            'limit': limit,
            'data': results
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v2_bp.route('/templates/<int:template_id>', methods=['GET'])
def get_template(template_id):
    """Get a specific trip template with all details"""
    try:
        template = db_session.query(TripTemplate).options(
            joinedload(TripTemplate.company),
            joinedload(TripTemplate.trip_type),
            joinedload(TripTemplate.primary_country),
            selectinload(TripTemplate.template_tags).joinedload(TripTemplateTag.tag),
            selectinload(TripTemplate.template_countries).joinedload(TripTemplateCountry.country),
        ).filter(TripTemplate.id == template_id).first()
        
        if not template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        data = template.to_dict(include_relations=True)
        
        # Get all occurrences
        occurrences = db_session.query(TripOccurrence).options(
            joinedload(TripOccurrence.guide)
        ).filter(
            TripOccurrence.trip_template_id == template_id,
            TripOccurrence.start_date >= datetime.now().date(),
            TripOccurrence.status != 'Cancelled'
        ).order_by(TripOccurrence.start_date).all()
        
        data['occurrences'] = [o.to_dict() for o in occurrences]
        
        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# TRIP OCCURRENCES API
# ============================================

@api_v2_bp.route('/occurrences', methods=['GET'])
def get_occurrences():
    """
    Get trip occurrences (scheduled trips) with filters.
    
    Query params:
    - template_id: Filter by template
    - guide_id: Filter by guide
    - status: Filter by status (OPEN, GUARANTEED, LAST_PLACES, FULL)
    - start_date: Filter by minimum start date
    - end_date: Filter by maximum end date
    - year: Filter by year
    - month: Filter by month (1-12)
    - min_price: Minimum price
    - max_price: Maximum price
    - include_template: Include template details (default: true)
    - limit: Max results
    - offset: Pagination
    """
    try:
        query = db_session.query(TripOccurrence).options(
            joinedload(TripOccurrence.template).joinedload(TripTemplate.company),
            joinedload(TripOccurrence.template).joinedload(TripTemplate.trip_type),
            joinedload(TripOccurrence.template).joinedload(TripTemplate.primary_country),
            joinedload(TripOccurrence.guide),
        )
        
        # Default: exclude cancelled and past trips
        # Note: status is VARCHAR in DB, not enum
        # Exclude Cancelled AND Full trips from listings
        today = datetime.now().date()
        query = query.filter(
            TripOccurrence.status.notin_(['Cancelled', 'Full']),
            TripOccurrence.start_date >= today
        )
        
        # Filters
        if request.args.get('template_id'):
            query = query.filter(TripOccurrence.trip_template_id == int(request.args.get('template_id')))
        
        if request.args.get('guide_id'):
            query = query.filter(TripOccurrence.guide_id == int(request.args.get('guide_id')))
        
        if request.args.get('status'):
            # Map status to DB format (Title Case)
            status_map = {'OPEN': 'Open', 'GUARANTEED': 'Guaranteed', 'LAST_PLACES': 'Last Places', 'FULL': 'Full', 'CANCELLED': 'Cancelled'}
            status_str = request.args.get('status').upper().replace(' ', '_')
            if status_str in status_map:
                query = query.filter(TripOccurrence.status == status_map[status_str])
        
        if request.args.get('year'):
            query = query.filter(extract('year', TripOccurrence.start_date) == int(request.args.get('year')))
        
        if request.args.get('month'):
            query = query.filter(extract('month', TripOccurrence.start_date) == int(request.args.get('month')))
        
        if request.args.get('start_date'):
            try:
                min_date = datetime.fromisoformat(request.args.get('start_date')).date()
                query = query.filter(TripOccurrence.start_date >= min_date)
            except ValueError:
                pass
        
        if request.args.get('end_date'):
            try:
                max_date = datetime.fromisoformat(request.args.get('end_date')).date()
                query = query.filter(TripOccurrence.start_date <= max_date)
            except ValueError:
                pass
        
        # Price filtering using effective_price
        if request.args.get('max_price'):
            max_price = float(request.args.get('max_price'))
            query = query.filter(TripOccurrence.effective_price <= max_price)
        
        # Pagination
        total = query.count()
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))
        
        occurrences = query.order_by(TripOccurrence.start_date).offset(offset).limit(limit).all()
        
        # Format response
        include_template = request.args.get('include_template', 'true').lower() == 'true'
        results = [o.to_dict(include_template=include_template) for o in occurrences]
        
        return jsonify({
            'success': True,
            'count': len(results),
            'total': total,
            'offset': offset,
            'limit': limit,
            'data': results
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v2_bp.route('/occurrences/<int:occurrence_id>', methods=['GET'])
def get_occurrence(occurrence_id):
    """Get a specific trip occurrence with full details"""
    try:
        occurrence = db_session.query(TripOccurrence).options(
            joinedload(TripOccurrence.template).joinedload(TripTemplate.company),
            joinedload(TripOccurrence.template).joinedload(TripTemplate.trip_type),
            joinedload(TripOccurrence.template).selectinload(TripTemplate.template_tags).joinedload(TripTemplateTag.tag),
            joinedload(TripOccurrence.template).selectinload(TripTemplate.template_countries).joinedload(TripTemplateCountry.country),
            joinedload(TripOccurrence.guide),
        ).filter(TripOccurrence.id == occurrence_id).first()
        
        if not occurrence:
            return jsonify({'success': False, 'error': 'Occurrence not found'}), 404
        
        return jsonify({
            'success': True,
            'data': occurrence.to_dict(include_template=True)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# TRIPS API (Backward Compatible - Returns Occurrences as "Trips")
# ============================================

@api_v2_bp.route('/trips', methods=['GET'])
def get_trips_v2():
    """
    Backward-compatible trips endpoint.
    Returns occurrences formatted like the old trips table.
    
    This allows frontend to migrate gradually without breaking changes.
    """
    try:
        query = db_session.query(TripOccurrence).options(
            joinedload(TripOccurrence.template).joinedload(TripTemplate.company),
            joinedload(TripOccurrence.template).joinedload(TripTemplate.trip_type),
            joinedload(TripOccurrence.template).joinedload(TripTemplate.primary_country),
            joinedload(TripOccurrence.template).selectinload(TripTemplate.template_tags).joinedload(TripTemplateTag.tag),
            joinedload(TripOccurrence.guide),
        )
        
        today = datetime.now().date()
        
        # Check if this is Private Groups query (exclude date filter)
        trip_type_id = request.args.get('trip_type_id', type=int)
        private_groups_type = db_session.query(TripType).filter(TripType.name == 'Private Groups').first()
        is_private_groups = trip_type_id == (private_groups_type.id if private_groups_type else None)
        
        # Exclude Cancelled AND Full trips
        query = query.filter(TripOccurrence.status.notin_(['Cancelled', 'Full']))
        if not is_private_groups:
            query = query.filter(
                TripOccurrence.start_date >= today,
                TripOccurrence.spots_left > 0
            )
        
        # Join template for filtering
        query = query.join(TripTemplate).filter(TripTemplate.is_active == True)
        
        # Filters (compatible with old API)
        if request.args.get('country_id'):
            query = query.filter(TripTemplate.primary_country_id == int(request.args.get('country_id')))
        
        if trip_type_id:
            query = query.filter(TripTemplate.trip_type_id == trip_type_id)
        
        if request.args.get('guide_id'):
            query = query.filter(TripOccurrence.guide_id == int(request.args.get('guide_id')))
        
        if request.args.get('status'):
            # Map status to DB format (Title Case)
            status_map = {'OPEN': 'Open', 'GUARANTEED': 'Guaranteed', 'LAST_PLACES': 'Last Places', 'FULL': 'Full', 'CANCELLED': 'Cancelled'}
            status_str = request.args.get('status').upper().replace(' ', '_')
            if status_str in status_map:
                query = query.filter(TripOccurrence.status == status_map[status_str])
        
        if request.args.get('difficulty'):
            query = query.filter(TripTemplate.difficulty_level == int(request.args.get('difficulty')))
        
        # Pagination
        total = query.count()
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        if limit:
            limit = max(1, min(limit, 1000))
            query = query.offset(offset).limit(limit)
        
        occurrences = query.order_by(TripOccurrence.start_date).all()
        
        # Format as old-style trip objects
        trips = []
        for occ in occurrences:
            trip_data = format_occurrence_as_trip(occ)
            trips.append(trip_data)
        
        return jsonify({
            'success': True,
            'count': len(trips),
            'total': total,
            'offset': offset,
            'limit': limit,
            'data': trips
        }), 200
    except Exception as e:
        import traceback
        print(f"[API_V2] Error: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_v2_bp.route('/trips/<int:trip_id>', methods=['GET'])
def get_trip_v2(trip_id):
    """
    Get a specific trip by occurrence ID (backward compatible).
    """
    try:
        occurrence = db_session.query(TripOccurrence).options(
            joinedload(TripOccurrence.template).joinedload(TripTemplate.company),
            joinedload(TripOccurrence.template).joinedload(TripTemplate.trip_type),
            joinedload(TripOccurrence.template).joinedload(TripTemplate.primary_country),
            joinedload(TripOccurrence.template).selectinload(TripTemplate.template_tags).joinedload(TripTemplateTag.tag),
            joinedload(TripOccurrence.guide),
        ).filter(TripOccurrence.id == trip_id).first()
        
        if not occurrence:
            return jsonify({'success': False, 'error': 'Trip not found'}), 404
        
        trip_data = format_occurrence_as_trip(occurrence, include_relations=True)
        
        return jsonify({
            'success': True,
            'data': trip_data
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def format_occurrence_as_trip(occurrence, include_relations=False):
    """
    Format a TripOccurrence as a legacy Trip object.
    
    This provides backward compatibility with frontend code
    that expects the old Trip structure.
    """
    template = occurrence.template
    
    trip_data = {
        # IDs
        'id': occurrence.id,
        'templateId': template.id,  # NEW: Link to template
        
        # From template
        'title': template.title,
        'titleHe': template.title_he,
        'title_he': template.title_he,
        'description': template.description,
        'descriptionHe': template.description_he,
        'description_he': template.description_he,
        'imageUrl': occurrence.effective_image_url,
        'image_url': occurrence.effective_image_url,
        'difficultyLevel': template.difficulty_level,
        'difficulty_level': template.difficulty_level,
        
        # From occurrence
        'startDate': occurrence.start_date.isoformat() if occurrence.start_date else None,
        'start_date': occurrence.start_date.isoformat() if occurrence.start_date else None,
        'endDate': occurrence.end_date.isoformat() if occurrence.end_date else None,
        'end_date': occurrence.end_date.isoformat() if occurrence.end_date else None,
        'price': float(occurrence.effective_price) if occurrence.effective_price else None,
        'singleSupplementPrice': float(template.single_supplement_price) if template.single_supplement_price else None,
        'single_supplement_price': float(template.single_supplement_price) if template.single_supplement_price else None,
        'maxCapacity': occurrence.effective_max_capacity,
        'max_capacity': occurrence.effective_max_capacity,
        'spotsLeft': occurrence.spots_left,
        'spots_left': occurrence.spots_left,
        'status': occurrence.status,
        
        # Foreign keys
        'countryId': template.primary_country_id,
        'country_id': template.primary_country_id,
        'guideId': occurrence.guide_id,
        'guide_id': occurrence.guide_id,
        'tripTypeId': template.trip_type_id,
        'trip_type_id': template.trip_type_id,
        'companyId': template.company_id,  # NEW
        'company_id': template.company_id,
        
        # Timestamps
        'createdAt': occurrence.created_at.isoformat() if occurrence.created_at else None,
        'updatedAt': occurrence.updated_at.isoformat() if occurrence.updated_at else None,
    }
    
    if include_relations or True:  # Always include relations for compatibility
        # Country
        if template.primary_country:
            trip_data['country'] = template.primary_country.to_dict()
        
        # Guide
        if occurrence.guide:
            trip_data['guide'] = occurrence.guide.to_dict()
        
        # Trip type
        if template.trip_type:
            trip_data['tripType'] = template.trip_type.to_dict()
            trip_data['trip_type'] = template.trip_type.to_dict()
        
        # Company (NEW)
        if template.company:
            trip_data['company'] = template.company.to_dict()
        
        # Tags
        tags = [tt.tag.to_dict() for tt in template.template_tags if tt.tag]
        trip_data['tags'] = tags
    
    return trip_data


# ============================================
# RECOMMENDATIONS API V2 (Full Feature Parity with V1)
# ============================================

@api_v2_bp.route('/recommendations', methods=['POST'])
def get_recommendations_v2():
    """
    V2 Recommendation engine using TripOccurrence + TripTemplate.
    
    Full feature parity with V1:
    - Request logging for analytics
    - Search type classification
    - Relaxed search with date expansion, difficulty tolerance, full scoring
    - Antarctica special case handling
    - Legacy start_date support
    """
    from app import (
        SCORING_WEIGHTS, SCORE_THRESHOLDS, RecommendationConfig,
        LOGGING_ENABLED
    )
    from dateutil.relativedelta import relativedelta
    
    # Import logging and classification (same as V1)
    rec_logger = None
    request_id = None
    classify_search = None
    
    if LOGGING_ENABLED:
        try:
            from recommender.logger import get_logger
            rec_logger = get_logger()
            request_id = rec_logger.generate_request_id()
            rec_logger.start_request_timer(request_id)
        except Exception as log_err:
            print(f"[V2] Logger initialization failed: {log_err}", flush=True)
    
    try:
        from events.service import classify_search as _classify_search
        classify_search = _classify_search
    except ImportError:
        pass
    
    try:
        prefs = request.get_json(silent=True) or {}
        config = RecommendationConfig
        weights = SCORING_WEIGHTS
        today = datetime.now().date()
        
        # Parse preferences (full V1 parity)
        selected_countries = prefs.get('selected_countries', []) or []
        selected_continents_input = prefs.get('selected_continents', []) or []
        preferred_type_id = prefs.get('preferred_type_id')
        preferred_theme_ids = prefs.get('preferred_theme_ids', []) or []
        min_duration = prefs.get('min_duration', 1) or 1
        max_duration = prefs.get('max_duration', 365) or 365
        budget = prefs.get('budget')
        difficulty = prefs.get('difficulty')
        selected_year = prefs.get('year')
        selected_month = prefs.get('month')
        start_date_str = prefs.get('start_date')  # Legacy support
        
        # Parse start date safely (legacy support from V1)
        user_start_date = None
        if start_date_str:
            try:
                user_start_date = datetime.fromisoformat(start_date_str).date()
            except (ValueError, TypeError):
                user_start_date = None
        
        # Map continents to database enum values
        # Database uses NORTH_AND_CENTRAL_AMERICA (not NORTH_AMERICA)
        continent_mapping = {
            # Title Case inputs (from frontend)
            'Africa': 'AFRICA', 'Asia': 'ASIA', 'Europe': 'EUROPE',
            'North America': 'NORTH_AND_CENTRAL_AMERICA', 
            'North & Central America': 'NORTH_AND_CENTRAL_AMERICA',
            'South America': 'SOUTH_AMERICA', 'Oceania': 'OCEANIA', 'Antarctica': 'ANTARCTICA',
            # UPPERCASE inputs (from tests/direct API calls)
            'AFRICA': 'AFRICA', 'ASIA': 'ASIA', 'EUROPE': 'EUROPE',
            'NORTH_AMERICA': 'NORTH_AND_CENTRAL_AMERICA',
            'NORTH_AND_CENTRAL_AMERICA': 'NORTH_AND_CENTRAL_AMERICA',
            'SOUTH_AMERICA': 'SOUTH_AMERICA', 'OCEANIA': 'OCEANIA', 'ANTARCTICA': 'ANTARCTICA'
        }
        selected_continents_enum = [
            continent_mapping.get(c, c.upper().replace(' ', '_').replace('&', 'AND')) 
            for c in selected_continents_input
        ]
        
        # Check for Private Groups
        private_groups_type = db_session.query(TripType).filter(TripType.name == 'Private Groups').first()
        private_groups_id = private_groups_type.id if private_groups_type else 10
        is_private_groups = (preferred_type_id == private_groups_id)
        
        # Total trips count (exclude Cancelled and Full)
        total_trips_in_db = db_session.query(TripOccurrence).join(TripTemplate).filter(
            TripTemplate.is_active == True,
            TripOccurrence.status.notin_(['Cancelled', 'Full']),
            TripOccurrence.spots_left > 0,
            TripOccurrence.start_date >= today
        ).count()
        
        # Build query
        query = db_session.query(TripOccurrence).options(
            joinedload(TripOccurrence.template).joinedload(TripTemplate.company),
            joinedload(TripOccurrence.template).joinedload(TripTemplate.trip_type),
            joinedload(TripOccurrence.template).joinedload(TripTemplate.primary_country),
            joinedload(TripOccurrence.template).selectinload(TripTemplate.template_tags).joinedload(TripTemplateTag.tag),
            joinedload(TripOccurrence.guide),
        ).join(TripTemplate)
        
        # Active templates only
        query = query.filter(TripTemplate.is_active == True)
        
        # Geographic filter (via template's primary country)
        if selected_countries or selected_continents_enum:
            geo_filters = []
            if selected_countries:
                geo_filters.append(TripTemplate.primary_country_id.in_(selected_countries))
            if selected_continents_enum:
                query = query.join(Country, TripTemplate.primary_country_id == Country.id)
                geo_filters.append(Country.continent.in_(selected_continents_enum))
            
            if len(geo_filters) > 1:
                query = query.filter(or_(*geo_filters))
            else:
                query = query.filter(geo_filters[0])
        
        # Trip type filter
        if preferred_type_id:
            query = query.filter(TripTemplate.trip_type_id == preferred_type_id)
        
        # Date filter (full V1 parity including legacy start_date)
        if not is_private_groups:
            query = query.filter(TripOccurrence.start_date >= today)
            
            if selected_year and selected_year != 'all':
                query = query.filter(extract('year', TripOccurrence.start_date) == int(selected_year))
                if selected_month and selected_month != 'all':
                    query = query.filter(extract('month', TripOccurrence.start_date) == int(selected_month))
            
            # Legacy: If user specified a start date preference (old format)
            if user_start_date and user_start_date > today and not selected_year:
                query = query.filter(TripOccurrence.start_date >= user_start_date)
                print(f"[V2] Applied user start date filter: >= {user_start_date}", flush=True)
        
        # Status filter - exclude Cancelled AND Full trips
        query = query.filter(
            TripOccurrence.status.notin_(['Cancelled', 'Full'])
        )
        if not is_private_groups:
            query = query.filter(TripOccurrence.spots_left > 0)
        
        # Difficulty filter
        if difficulty is not None:
            tolerance = config.DIFFICULTY_TOLERANCE
            query = query.filter(
                TripTemplate.difficulty_level.between(difficulty - tolerance, difficulty + tolerance)
            )
        
        # Budget filter
        if budget:
            max_price = budget * config.BUDGET_MAX_MULTIPLIER
            query = query.filter(TripOccurrence.effective_price <= max_price)
        
        # Get candidates
        candidates = query.all()
        
        # Score candidates
        scored_trips = []
        for occ in candidates:
            template = occ.template
            current_score = weights['BASE_SCORE']
            match_details = []
            
            trip_is_private = (template.trip_type_id == private_groups_id)
            
            # Get theme tags (all tags are theme tags after V2 migration)
            trip_theme_tags = [
                tt.tag_id for tt in template.template_tags 
                if tt.tag
            ]
            
            # Theme scoring
            if preferred_theme_ids:
                theme_matches = len(set(trip_theme_tags) & set(preferred_theme_ids))
                if theme_matches >= config.THEME_MATCH_THRESHOLD:
                    current_score += weights['THEME_FULL']
                    match_details.append(f"Excellent Theme Match [+{weights['THEME_FULL']:.0f}]")
                elif theme_matches == 1:
                    current_score += weights['THEME_PARTIAL']
                    match_details.append(f"Good Theme Match [+{weights['THEME_PARTIAL']:.0f}]")
                else:
                    current_score += weights['THEME_PENALTY']
                    match_details.append(f"No Theme Match [{weights['THEME_PENALTY']:.0f}]")
            
            # Difficulty scoring
            if difficulty is not None and template.difficulty_level == difficulty:
                current_score += weights['DIFFICULTY_PERFECT']
                match_details.append(f"Perfect Difficulty [+{weights['DIFFICULTY_PERFECT']:.0f}]")
            
            # Duration scoring
            if trip_is_private:
                current_score += weights['DURATION_IDEAL']
                match_details.append(f"Flexible Duration [+{weights['DURATION_IDEAL']:.0f}]")
            else:
                trip_duration = occ.duration_days or 0
                if min_duration <= trip_duration <= max_duration:
                    current_score += weights['DURATION_IDEAL']
                    match_details.append(f"Ideal Duration ({trip_duration}d) [+{weights['DURATION_IDEAL']:.0f}]")
                elif abs(trip_duration - min_duration) <= config.DURATION_GOOD_DAYS or \
                     abs(trip_duration - max_duration) <= config.DURATION_GOOD_DAYS:
                    current_score += weights['DURATION_GOOD']
                    match_details.append(f"Good Duration ({trip_duration}d) [+{weights['DURATION_GOOD']:.0f}]")
                elif abs(trip_duration - min_duration) > config.DURATION_HARD_FILTER_DAYS and \
                     abs(trip_duration - max_duration) > config.DURATION_HARD_FILTER_DAYS:
                    continue  # Skip - outside hard filter
            
            # Budget scoring
            if budget:
                trip_price = float(occ.effective_price or 0)
                if trip_price <= budget:
                    current_score += weights['BUDGET_PERFECT']
                    match_details.append(f"Within Budget [+{weights['BUDGET_PERFECT']:.0f}]")
                elif trip_price <= budget * 1.1:
                    current_score += weights['BUDGET_GOOD']
                    match_details.append(f"Slightly Over (+10%) [+{weights['BUDGET_GOOD']:.0f}]")
                elif trip_price <= budget * 1.2:
                    current_score += weights['BUDGET_ACCEPTABLE']
                    match_details.append(f"Over Budget (+20%) [+{weights['BUDGET_ACCEPTABLE']:.0f}]")
            
            # Status scoring (status is VARCHAR in DB)
            if occ.status == 'Guaranteed':
                current_score += weights['STATUS_GUARANTEED']
                match_details.append(f"Guaranteed [+{weights['STATUS_GUARANTEED']:.0f}]")
            elif occ.status == 'Last Places':
                current_score += weights['STATUS_LAST_PLACES']
                match_details.append(f"Last Places [+{weights['STATUS_LAST_PLACES']:.0f}]")
            
            # Departing soon
            if not trip_is_private and occ.start_date:
                days_until = (occ.start_date - today).days
                if days_until <= config.DEPARTING_SOON_DAYS:
                    current_score += weights['DEPARTING_SOON']
                    match_details.append(f"Soon ({days_until}d) [+{weights['DEPARTING_SOON']:.0f}]")
            
            # Geography scoring (with Antarctica special case from V1)
            if selected_countries or selected_continents_enum:
                is_direct = selected_countries and template.primary_country_id in selected_countries
                is_continent = (
                    selected_continents_enum and 
                    template.primary_country and 
                    template.primary_country.continent.name in selected_continents_enum
                )
                
                # Special case: Antarctica continent selection = direct country match (V1 parity)
                is_antarctica_match = (
                    selected_continents_enum and 'ANTARCTICA' in selected_continents_enum and
                    template.primary_country and template.primary_country.name == 'Antarctica'
                )
                
                if is_direct or is_antarctica_match:
                    current_score += weights['GEO_DIRECT_COUNTRY']
                    match_details.append(f"Country Match [+{weights['GEO_DIRECT_COUNTRY']:.0f}]")
                elif is_continent:
                    current_score += weights['GEO_CONTINENT']
                    match_details.append(f"Continent Match [+{weights['GEO_CONTINENT']:.0f}]")
            
            # Final score
            final_score = max(0.0, min(100.0, current_score))
            
            trip_dict = format_occurrence_as_trip(occ, include_relations=True)
            trip_dict['_float_score'] = final_score
            trip_dict['match_score'] = int(round(final_score))
            trip_dict['match_details'] = match_details
            trip_dict['_sort_date'] = occ.start_date.isoformat() if occ.start_date else '2099-12-31'
            trip_dict['is_relaxed'] = False
            
            scored_trips.append(trip_dict)
        
        # Sort
        scored_trips.sort(key=lambda x: (-x['_float_score'], x['_sort_date']))
        
        # Get top results
        top_trips = []
        for trip in scored_trips[:config.MAX_RESULTS]:
            top_trips.append(trip)
        
        # Track IDs already included
        included_ids = {t['id'] for t in top_trips}
        
        # ========================================
        # RELAXED SEARCH (Full V1 Parity)
        # ========================================
        relaxed_trips = []
        if len(top_trips) < config.MIN_RESULTS_THRESHOLD:
            needed = config.MAX_RESULTS - len(top_trips)
            print(f"[V2 RELAXED] Only {len(top_trips)} primary results. Need {needed} more relaxed results.", flush=True)
            
            # Build relaxed query - same base but WITH EXPANDED filters
            relaxed_query = db_session.query(TripOccurrence).options(
                joinedload(TripOccurrence.template).joinedload(TripTemplate.company),
                joinedload(TripOccurrence.template).joinedload(TripTemplate.trip_type),
                joinedload(TripOccurrence.template).joinedload(TripTemplate.primary_country),
                joinedload(TripOccurrence.template).selectinload(TripTemplate.template_tags).joinedload(TripTemplateTag.tag),
                joinedload(TripOccurrence.guide),
            ).join(TripTemplate)
            
            # Active templates only
            relaxed_query = relaxed_query.filter(TripTemplate.is_active == True)
            
            # Status filter (same - no Full or Cancelled)
            if is_private_groups:
                relaxed_query = relaxed_query.filter(TripOccurrence.status.notin_(['Cancelled', 'Full']))
            else:
                relaxed_query = relaxed_query.filter(
                    TripOccurrence.status.notin_(['Cancelled', 'Full']),
                    TripOccurrence.spots_left > 0
                )
            
            # RELAXED GEOGRAPHY: Expand to same continent if user selected specific countries
            if selected_countries or selected_continents_enum:
                geo_filters = []
                
                if selected_countries:
                    # Get continents of selected countries for expansion
                    selected_country_objs = db_session.query(Country).filter(Country.id.in_(selected_countries)).all()
                    expanded_continents = set()
                    for c in selected_country_objs:
                        if c.continent:
                            continent_name = c.continent.name if hasattr(c.continent, 'name') else str(c.continent)
                            expanded_continents.add(continent_name)
                    
                    # Include all countries from same continents
                    relaxed_query = relaxed_query.join(Country, TripTemplate.primary_country_id == Country.id)
                    if expanded_continents:
                        geo_filters.append(Country.continent.in_(list(expanded_continents)))
                        print(f"[V2 RELAXED] Expanded geography to continents: {expanded_continents}", flush=True)
                    else:
                        geo_filters.append(TripTemplate.primary_country_id.in_(selected_countries))
                
                if selected_continents_enum:
                    if not selected_countries:  # Only join if not already joined
                        relaxed_query = relaxed_query.join(Country, TripTemplate.primary_country_id == Country.id)
                    geo_filters.append(Country.continent.in_(selected_continents_enum))
                
                if len(geo_filters) > 1:
                    relaxed_query = relaxed_query.filter(or_(*geo_filters))
                elif geo_filters:
                    relaxed_query = relaxed_query.filter(geo_filters[0])
            
            # RELAXED: Do NOT filter by trip type (allow all types with penalty)
            print(f"[V2 RELAXED] Not filtering by trip type (will apply penalty for different types)", flush=True)
            
            # RELAXED DATE FILTER: Expand by 2 months before and after (V1 parity)
            if not is_private_groups:
                relaxed_query = relaxed_query.filter(TripOccurrence.start_date >= today)
                
                if selected_year and selected_year != 'all':
                    try:
                        year_int = int(selected_year)
                        
                        if selected_month and selected_month != 'all':
                            # User selected specific month: expand by 2 months before and after
                            month_int = int(selected_month)
                            center_date = datetime(year_int, month_int, 1).date()
                            
                            # 2 months before
                            start_range = max(center_date - relativedelta(months=2), today)
                            # 2 months after (end of that month)
                            end_range = center_date + relativedelta(months=3) - timedelta(days=1)
                            
                            relaxed_query = relaxed_query.filter(
                                TripOccurrence.start_date.between(start_range, end_range)
                            )
                            print(f"[V2 RELAXED] Expanded date range: {start_range} to {end_range}", flush=True)
                        else:
                            # User selected only year: expand by 2 months before and after the year
                            year_start = datetime(year_int, 1, 1).date()
                            year_end = datetime(year_int, 12, 31).date()
                            
                            start_range = max(year_start - relativedelta(months=2), today)
                            end_range = year_end + relativedelta(months=2)
                            
                            relaxed_query = relaxed_query.filter(
                                TripOccurrence.start_date.between(start_range, end_range)
                            )
                            print(f"[V2 RELAXED] Expanded year {year_int} to: {start_range} to {end_range}", flush=True)
                    except (ValueError, TypeError):
                        pass  # Fall back to just >= today
            
            # RELAXED: Difficulty (+/-2 levels instead of +/-1)
            if difficulty is not None:
                RELAXED_DIFFICULTY_TOLERANCE = 2
                relaxed_query = relaxed_query.filter(
                    TripTemplate.difficulty_level.between(
                        difficulty - RELAXED_DIFFICULTY_TOLERANCE,
                        difficulty + RELAXED_DIFFICULTY_TOLERANCE
                    )
                )
                print(f"[V2 RELAXED] Difficulty filter: {difficulty} +/-{RELAXED_DIFFICULTY_TOLERANCE}", flush=True)
            
            # RELAXED: Budget (50% over budget instead of 30%)
            if budget:
                RELAXED_BUDGET_MULTIPLIER = 1.5
                relaxed_max_price = budget * RELAXED_BUDGET_MULTIPLIER
                relaxed_query = relaxed_query.filter(TripOccurrence.effective_price <= relaxed_max_price)
                print(f"[V2 RELAXED] Budget filter: max ${relaxed_max_price}", flush=True)
            
            # Exclude already included trips
            relaxed_query = relaxed_query.filter(~TripOccurrence.id.in_(included_ids))
            
            # Get relaxed candidates
            relaxed_candidates = relaxed_query.all()
            print(f"[V2 RELAXED] Found {len(relaxed_candidates)} relaxed candidates", flush=True)
            
            # ========================================
            # SCORE RELAXED TRIPS (Full V1 Parity)
            # ========================================
            RELAXED_DURATION_DAYS = 10  # Allow +/-10 days from range
            relaxed_scored = []
            
            for occ in relaxed_candidates:
                template = occ.template
                current_score = weights['BASE_SCORE'] + weights.get('RELAXED_PENALTY', -20.0)
                match_details = ["Expanded Result [-20]"]
                
                trip_is_private = (template.trip_type_id == private_groups_id)
                
                # Get theme tags
                trip_theme_tags = []
                try:
                    trip_theme_tags = [tt.tag_id for tt in template.template_tags if tt.tag]
                except:
                    pass
                
                # 1. Theme scoring
                if preferred_theme_ids:
                    theme_matches = len(set(trip_theme_tags) & set(preferred_theme_ids))
                    if theme_matches >= config.THEME_MATCH_THRESHOLD:
                        current_score += weights['THEME_FULL']
                        match_details.append(f"Theme Match [+{weights['THEME_FULL']:.0f}]")
                    elif theme_matches == 1:
                        current_score += weights['THEME_PARTIAL']
                        match_details.append(f"Theme Match [+{weights['THEME_PARTIAL']:.0f}]")
                    else:
                        current_score += weights['THEME_PENALTY']
                
                # 2. Trip type penalty (V1 parity)
                if preferred_type_id and template.trip_type_id != preferred_type_id:
                    current_score -= 10.0
                    match_details.append("Different Type [-10]")
                
                # 3. Difficulty scoring
                if difficulty is not None and template.difficulty_level == difficulty:
                    current_score += weights['DIFFICULTY_PERFECT']
                    match_details.append(f"Perfect Difficulty [+{weights['DIFFICULTY_PERFECT']:.0f}]")
                
                # 4. Duration scoring (relaxed tolerance)
                if trip_is_private:
                    current_score += weights['DURATION_IDEAL']
                else:
                    trip_duration = occ.duration_days or 0
                    if min_duration <= trip_duration <= max_duration:
                        current_score += weights['DURATION_IDEAL']
                        match_details.append(f"Ideal Duration [+{weights['DURATION_IDEAL']:.0f}]")
                    elif abs(trip_duration - min_duration) <= RELAXED_DURATION_DAYS or \
                         abs(trip_duration - max_duration) <= RELAXED_DURATION_DAYS:
                        current_score += weights['DURATION_GOOD']
                        match_details.append(f"Good Duration [+{weights['DURATION_GOOD']:.0f}]")
                
                # 5. Budget scoring
                if budget:
                    trip_price = float(occ.effective_price or 0)
                    if trip_price <= budget:
                        current_score += weights['BUDGET_PERFECT']
                        match_details.append(f"Within Budget [+{weights['BUDGET_PERFECT']:.0f}]")
                    elif trip_price <= budget * 1.1:
                        current_score += weights['BUDGET_GOOD']
                    elif trip_price <= budget * 1.2:
                        current_score += weights['BUDGET_ACCEPTABLE']
                
                # 6. Status bonuses
                if occ.status == 'Guaranteed':
                    current_score += weights['STATUS_GUARANTEED']
                    match_details.append(f"Guaranteed [+{weights['STATUS_GUARANTEED']:.0f}]")
                elif occ.status == 'Last Places':
                    current_score += weights['STATUS_LAST_PLACES']
                    match_details.append(f"Last Places [+{weights['STATUS_LAST_PLACES']:.0f}]")
                
                # 7. Departing soon bonus
                if not trip_is_private and occ.start_date:
                    days_until_departure = (occ.start_date - today).days
                    if days_until_departure <= config.DEPARTING_SOON_DAYS:
                        current_score += weights['DEPARTING_SOON']
                        match_details.append(f"Soon ({days_until_departure}d) [+{weights['DEPARTING_SOON']:.0f}]")
                
                # 8. Geography scoring (with Antarctica special case)
                if selected_countries or selected_continents_enum:
                    is_direct_match = selected_countries and template.primary_country_id in selected_countries
                    is_continent_match = (
                        selected_continents_enum and template.primary_country and 
                        template.primary_country.continent.name in selected_continents_enum
                    )
                    
                    # Special case: Antarctica continent selection = direct country match
                    is_antarctica_match = (
                        selected_continents_enum and 'ANTARCTICA' in selected_continents_enum and
                        template.primary_country and template.primary_country.name == 'Antarctica'
                    )
                    
                    if is_direct_match or is_antarctica_match:
                        current_score += weights['GEO_DIRECT_COUNTRY']
                        match_details.append(f"Country Match [+{weights['GEO_DIRECT_COUNTRY']:.0f}]")
                    elif is_continent_match:
                        current_score += weights['GEO_CONTINENT']
                        match_details.append(f"Continent Match [+{weights['GEO_CONTINENT']:.0f}]")
                
                # Final score (clamped 0-100)
                final_score = max(0.0, min(100.0, current_score))
                
                try:
                    trip_dict = format_occurrence_as_trip(occ, include_relations=True)
                    trip_dict['_float_score'] = final_score
                    trip_dict['match_score'] = int(round(final_score))
                    trip_dict['match_details'] = match_details
                    trip_dict['is_relaxed'] = True
                    if occ.start_date:
                        trip_dict['_sort_date'] = occ.start_date.isoformat()
                    else:
                        trip_dict['_sort_date'] = '2099-12-31'
                    relaxed_scored.append(trip_dict)
                except Exception as e:
                    print(f"[V2 RELAXED] Serialization error for trip {occ.id}: {e}", flush=True)
                    continue
            
            # Sort relaxed trips by score descending, then date ascending
            relaxed_scored.sort(key=lambda x: (-x['_float_score'], x['_sort_date']))
            
            # Add needed relaxed trips
            for trip in relaxed_scored[:needed]:
                trip.pop('_sort_date', None)
                trip.pop('_float_score', None)
                relaxed_trips.append(trip)
            
            print(f"[V2 RELAXED] Added {len(relaxed_trips)} relaxed results", flush=True)
        
        # Combine primary and relaxed results
        all_trips = top_trips + relaxed_trips
        has_relaxed = len(relaxed_trips) > 0
        
        # Clean up internal fields from top_trips
        for trip in top_trips:
            trip.pop('_sort_date', None)
            trip.pop('_float_score', None)
        
        # Handle empty results case
        if not all_trips:
            print(f"[V2] No results found from either primary or relaxed search", flush=True)
            return jsonify({
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
                'request_id': request_id,
                'api_version': 'v2',
                'message': 'No trips match your criteria. Try adjusting your preferences.'
            }), 200
        
        # Response metrics
        top_score = all_trips[0]['match_score'] if all_trips else 0
        show_refinement_message = top_score < SCORE_THRESHOLDS['HIGH']
        
        print(f"[V2] Returning {len(top_trips)} primary + {len(relaxed_trips)} relaxed = {len(all_trips)} total. Top score: {top_score}", flush=True)
        
        # Classify search type (V1 parity)
        search_type = 'exploration'
        if classify_search:
            try:
                search_type = classify_search(prefs)
            except Exception:
                pass
        
        # Log the request for metrics (V1 parity)
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
                    algorithm_version='v2.0',
                    search_type=search_type,
                )
            except Exception as log_err:
                print(f"[V2] Failed to log request: {log_err}", flush=True)
        
        # Build message with relaxed count (V1 parity)
        message = f'Found {len(top_trips)} recommended trips'
        if has_relaxed:
            message += f' + {len(relaxed_trips)} expanded results'
        
        return jsonify({
            'success': True,
            'count': len(all_trips),
            'primary_count': len(top_trips),
            'relaxed_count': len(relaxed_trips),
            'total_candidates': len(candidates),
            'total_trips': total_trips_in_db,
            'data': all_trips,
            'has_relaxed_results': has_relaxed,
            'score_thresholds': SCORE_THRESHOLDS,
            'show_refinement_message': show_refinement_message,
            'request_id': request_id,
            'search_type': search_type,
            'api_version': 'v2',
            'message': message
        }), 200
        
    except Exception as e:
        import traceback
        print(f"[V2 RECOMMENDATIONS] Error: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e), 'api_version': 'v2'}), 500


# ============================================
# SCHEMA INFO ENDPOINT
# ============================================

@api_v2_bp.route('/schema-info', methods=['GET'])
def get_schema_info():
    """Get information about the V2 schema"""
    try:
        stats = {
            'companies': db_session.query(Company).count(),
            'templates': db_session.query(TripTemplate).filter(TripTemplate.is_active == True).count(),
            'occurrences': db_session.query(TripOccurrence).filter(
                TripOccurrence.status != 'Cancelled'
            ).count(),
            'active_occurrences': db_session.query(TripOccurrence).filter(
                TripOccurrence.status != 'Cancelled',
                TripOccurrence.start_date >= datetime.now().date()
            ).count(),
        }
        
        return jsonify({
            'success': True,
            'schema_version': '2.3',
            'statistics': stats,
            'endpoints': {
                'companies': '/api/v2/companies',
                'templates': '/api/v2/templates',
                'occurrences': '/api/v2/occurrences',
                'trips': '/api/v2/trips (backward compatible)',
                'recommendations': '/api/v2/recommendations',
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
