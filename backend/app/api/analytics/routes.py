"""
Analytics API Endpoints
=======================

Metrics and evaluation endpoints for recommendation analytics and testing.
"""

import traceback
from datetime import datetime, timedelta, date
from flask import Blueprint, jsonify, request
from app.core.database import is_database_error

# Check if logging/metrics modules are available
try:
    from recommender.metrics import get_aggregator
    from recommender.evaluation import get_evaluator
    LOGGING_ENABLED = True
except ImportError:
    LOGGING_ENABLED = False

analytics_bp = Blueprint('analytics', __name__)


# ============================================
# METRICS ENDPOINTS
# ============================================

@analytics_bp.route('/api/metrics', methods=['GET'])
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


@analytics_bp.route('/api/metrics/daily', methods=['GET'])
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


@analytics_bp.route('/api/metrics/top-searches', methods=['GET'])
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


# ============================================
# EVALUATION ENDPOINTS
# ============================================

@analytics_bp.route('/api/evaluation/run', methods=['POST'])
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
        print(f"[EVALUATION] Error: {traceback.format_exc()}", flush=True)
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


@analytics_bp.route('/api/evaluation/scenarios', methods=['GET'])
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
