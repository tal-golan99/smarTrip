"""
Supabase JWT Authentication Helper
==================================

Verifies Supabase JWT tokens and extracts user information for Flask routes.

Usage:
    from auth_supabase import get_current_user, require_auth
    
    @app.route('/api/protected')
    @require_auth  # Optional decorator
    def protected_route():
        user = get_current_user()  # Returns None if not authenticated
        if user:
            # User is authenticated
            return jsonify({'user_id': user['id'], 'email': user['email']})
        else:
            # Guest user
            return jsonify({'message': 'Guest access'})
"""


import os
import jwt
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, g, jsonify

# Get JWT secret from environment
SUPABASE_JWT_SECRET = os.environ.get('SUPABASE_JWT_SECRET')

if not SUPABASE_JWT_SECRET:
    print("[WARNING] SUPABASE_JWT_SECRET not set. JWT verification will be disabled.")


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Extract and verify Supabase JWT token from request headers.
    
    Returns:
        Dict with user info if authenticated, None if guest:
        {
            'id': 'uuid',           # Supabase user ID (from 'sub' claim)
            'email': 'user@...',    # User email
            'supabase_user_id': 'uuid'  # Same as 'id' (for clarity)
        }
        None if no valid token or not authenticated
    """
    if not SUPABASE_JWT_SECRET:
        return None
    
    # Get Authorization header
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return None
    
    # Extract token
    token = auth_header.split(' ', 1)[1]
    
    try:
        # Verify and decode JWT
        # Supabase uses HS256 algorithm
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=['HS256'],
            audience='authenticated',  # Supabase JWT audience
            options={
                'verify_signature': True,
                'verify_exp': True,
                'verify_aud': True,
            }
        )
        
        # Extract user info from payload
        # Supabase JWT contains 'sub' (user ID) and 'email'
        user_id = payload.get('sub')
        email = payload.get('email')
        
        if not user_id:
            return None
        
        return {
            'id': user_id,
            'email': email,
            'supabase_user_id': user_id,  # Alias for clarity
        }
        
    except jwt.ExpiredSignatureError:
        print("[AUTH] JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"[AUTH] Invalid JWT token: {e}")
        return None
    except Exception as e:
        print(f"[AUTH] Error verifying JWT: {e}")
        return None


def require_auth(f):
    """
    Decorator to require authentication for a route.
    
    If user is not authenticated, returns 401 Unauthorized.
    If authenticated, stores user info in Flask's g object.
    
    Usage:
        @app.route('/api/protected')
        @require_auth
        def protected_route():
            user = g.current_user  # Available in route
            return jsonify({'user_id': user['id']})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Store user in Flask's g object for route access
        g.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function


def optional_auth(f):
    """
    Decorator that makes authentication optional.
    
    If user is authenticated, stores user info in Flask's g object.
    If not authenticated, g.current_user is None (route can still proceed).
    
    Usage:
        @app.route('/api/recommendations')
        @optional_auth
        def recommendations():
            user = g.current_user  # None if guest, dict if authenticated
            # ... proceed with or without user
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        g.current_user = user  # Can be None for guests
        return f(*args, **kwargs)
    
    return decorated_function



