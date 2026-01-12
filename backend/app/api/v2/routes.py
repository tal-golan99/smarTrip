"""
SmartTrip API V2 - Using New Schema
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

from app.core.database import db_session, is_database_error
from app.models.trip import (
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
    from app.services.recommendation import get_recommendations, SCORE_THRESHOLDS
    from app.main import LOGGING_ENABLED
    
    # Import logging and classification (same as V1)
    rec_logger = None
    request_id = None
    classify_search = None
    
    if LOGGING_ENABLED:
        try:
            from recommender.logging import get_logger
            rec_logger = get_logger()
            request_id = rec_logger.generate_request_id()
            rec_logger.start_request_timer(request_id)
        except Exception as log_err:
            print(f"[V2] Logger initialization failed: {log_err}", flush=True)
    
    try:
        from app.services.events import classify_search as _classify_search
        classify_search = _classify_search
    except ImportError:
        pass
    
    try:
        prefs = request.get_json(silent=True) or {}
        
        # Call recommendation service
        result = get_recommendations(prefs, format_occurrence_as_trip)
        
        primary_trips = result['primary_trips']
        relaxed_trips = result['relaxed_trips']
        total_candidates = result['total_candidates']
        total_trips_in_db = result['total_trips_in_db']
        
        # Combine primary and relaxed results
        all_trips = primary_trips + relaxed_trips
        has_relaxed = len(relaxed_trips) > 0
        
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
        
        print(f"[V2] Returning {len(primary_trips)} primary + {len(relaxed_trips)} relaxed = {len(all_trips)} total. Top score: {top_score}", flush=True)
        
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
                    total_candidates=total_candidates,
                    primary_count=len(primary_trips),
                    relaxed_count=len(relaxed_trips),
                    session_id=request.headers.get('X-Session-ID'),
                    algorithm_version='v2.0',
                    search_type=search_type,
                )
            except Exception as log_err:
                print(f"[V2] Failed to log request: {log_err}", flush=True)
        
        # Build message with relaxed count (V1 parity)
        message = f'Found {len(primary_trips)} recommended trips'
        if has_relaxed:
            message += f' + {len(relaxed_trips)} expanded results'
        
        return jsonify({
            'success': True,
            'count': len(all_trips),
            'primary_count': len(primary_trips),
            'relaxed_count': len(relaxed_trips),
            'total_candidates': total_candidates,
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
        is_db_error, is_conn_error = is_database_error(e)
        
        if is_conn_error:
            return jsonify({
                'success': False,
                'error': 'Database connection unavailable. Please check your configuration or try again later.',
                'api_version': 'v2'
            }), 503
        elif is_db_error:
            return jsonify({
                'success': False,
                'error': 'Database error occurred. Please try again later.',
                'api_version': 'v2'
            }), 503
        else:
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
