"""
SmartTrip Flask API - Main Application
Smart Recommendation Engine for Niche Travel
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables FIRST, before any imports that depend on them
load_dotenv()

# Now import database and other modules that depend on environment variables
from app.core.database import init_db, db_session, engine

# Note: LOGGING_ENABLED is now checked in analytics blueprint
# Keeping this import for backward compatibility if needed elsewhere
try:
    from recommender.logging import get_logger, RecommendationLogger
    LOGGING_ENABLED = True
except ImportError as e:
    print(f"[WARNING] Recommender module not available: {e}")
    LOGGING_ENABLED = False

# Import event tracking (Phase 1)
try:
    from app.api.events.routes import events_bp
    EVENTS_ENABLED = True
except ImportError as e:
    print(f"[WARNING] Events module not available: {e}")
    EVENTS_ENABLED = False

# Import V2 API (Phase 2 - New Schema)
try:
    from app.api.v2.routes import api_v2_bp
    API_V2_ENABLED = True
except ImportError as e:
    print(f"[WARNING] API V2 module not available: {e}")
    API_V2_ENABLED = False

# Import new blueprints
from app.api.system.routes import system_bp
from app.api.resources.routes import resources_bp
from app.api.analytics.routes import analytics_bp


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

# Register new blueprints (no url_prefix - routes define full paths)
app.register_blueprint(system_bp)
app.register_blueprint(resources_bp)
app.register_blueprint(analytics_bp)
print("[INIT] System, Resources, and Analytics blueprints registered")


# ============================================
# DATABASE LIFECYCLE
# ============================================

@app.before_request
def before_request():
    """Attach database session to request context"""
    # Scoped session automatically handles Flask application context
    # No explicit binding needed - scoped_session uses thread-local storage
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


if __name__ == '__main__':
    # Run Flask development server
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"SmartTrip API running on http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/api/health")
    
    # Disable reloader to prevent double connection attempts to database
    # This prevents circuit breaker issues and connection pool exhaustion
    app.run(host=host, port=port, debug=True, use_reloader=False)
