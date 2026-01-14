"""
System API Endpoints
====================

Health check endpoint.
"""

from flask import Blueprint, jsonify
from app.core.database import db_session, is_database_error
from app.models.trip import TripOccurrence, TripTemplate, Country, Guide, Tag, TripType

system_bp = Blueprint('system', __name__)


@system_bp.route('/api/health', methods=['GET'])
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
        is_db_error, is_conn_error = is_database_error(e)
        
        if is_conn_error:
            return jsonify({
                'status': 'unhealthy',
                'error': 'Database connection unavailable. Please check your configuration or try again later.'
            }), 503
        elif is_db_error:
            return jsonify({
                'status': 'unhealthy',
                'error': 'Database error occurred. Please try again later.'
            }), 503
        else:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500

