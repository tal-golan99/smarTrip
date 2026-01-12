"""
System API Endpoints
====================

Health check and database seeding.
"""

import os
import sys
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


@system_bp.route('/api/seed', methods=['POST'])
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
        # Add scripts to path for import
        # __file__ is backend/app/api/system/routes.py, so go up to backend/
        backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        scripts_path = os.path.join(backend_path, 'scripts')
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        from scripts.db.seed import seed_database  # type: ignore[import-untyped]
        
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


