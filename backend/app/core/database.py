"""
Database configuration and session management
V2 Schema: Uses models_v2.Base for table creation
"""

import os
from urllib.parse import quote_plus, unquote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError, DatabaseError
# V2 Migration: Use V2 Base for table creation
from app.models.trip import Base

# Get database URL from environment
# Note: Environment variables are loaded by main.py before this module is imported
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./smarttrip.db')

# Some providers use postgres:// but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Fix: URL-encode special characters in password and remove brackets if connection string appears malformed
# This handles cases where password contains @, #, %, etc. or has brackets that break URL parsing
if DATABASE_URL.startswith('postgresql://') and '@' in DATABASE_URL:
    try:
        # Check if connection string has multiple @ symbols (indicates unencoded @ in password)
        at_count = DATABASE_URL.count('@')
        if at_count > 1:
            # Multiple @ symbols - password likely contains unencoded @
            # Find the last @ which should be the separator
            last_at_index = DATABASE_URL.rfind('@')
            scheme_user_pass = DATABASE_URL[:last_at_index]
            host_part = DATABASE_URL[last_at_index + 1:]
            
            if '://' in scheme_user_pass:
                scheme, user_pass = scheme_user_pass.split('://', 1)
                if ':' in user_pass:
                    user, password = user_pass.split(':', 1)
                    # Remove brackets if present
                    if password.startswith('[') and password.endswith(']'):
                        password = password[1:-1]
                        print(f"[DB] Removed brackets from password")
                    # URL-encode the password (handles @, #, %, etc.)
                    encoded_password = quote_plus(password)
                    # Reconstruct the connection string
                    DATABASE_URL = f"{scheme}://{user}:{encoded_password}@{host_part}"
                    print(f"[DB] Fixed connection string - URL-encoded password with special characters")
        else:
            # Single @ - check if host part is malformed (starts with ] or other invalid chars)
            parts = DATABASE_URL.split('@', 1)
            if len(parts) == 2:
                host_part = parts[1]
                if host_part.startswith(']') or (not host_part.startswith(('aws-', 'localhost', '127.0.0.1', 'postgres')) and ':' in host_part):
                    # Host part is malformed - likely password has brackets or unencoded special chars
                    scheme_user_pass = parts[0]
                    if '://' in scheme_user_pass:
                        scheme, user_pass = scheme_user_pass.split('://', 1)
                        if ':' in user_pass:
                            user, password = user_pass.split(':', 1)
                            # Remove brackets if present
                            if password.startswith('[') and password.endswith(']'):
                                password = password[1:-1]
                                print(f"[DB] Removed brackets from password")
                            # URL-encode the password
                            encoded_password = quote_plus(password)
                            # Reconstruct - need to find the actual host part
                            # If host_part starts with ], the actual host is after the next @
                            if host_part.startswith(']'):
                                # Find the actual host (after the ] and @)
                                actual_host = host_part[1:] if not host_part.startswith(']@') else host_part[2:]
                            else:
                                actual_host = host_part
                            DATABASE_URL = f"{scheme}://{user}:{encoded_password}@{actual_host}"
                            print(f"[DB] Fixed connection string - removed brackets and URL-encoded password")
    except Exception as e:
        # If parsing fails, continue with original URL (will fail with clearer error)
        print(f"[WARNING] Could not parse DATABASE_URL for password encoding: {e}")

# Ensure SSL mode for cloud databases (Supabase, etc.)
if 'supabase' in DATABASE_URL and 'sslmode' not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL + ('&' if '?' in DATABASE_URL else '?') + 'sslmode=require'

# Create engine with connection pooling
# For Supabase pooler, use smaller pool size
# For direct connections, can use larger pool
pool_size = 5 if 'pooler' in DATABASE_URL else 10
max_overflow = 10 if 'pooler' in DATABASE_URL else 20

engine = create_engine(
    DATABASE_URL,
    echo=True if os.getenv('FLASK_ENV') == 'development' else False,
    pool_size=pool_size,
    max_overflow=max_overflow,
    pool_pre_ping=True,  # Verify connections before using them
    connect_args={
        'connect_timeout': 10,  # 10 second timeout
    } if 'postgresql' in DATABASE_URL else {}
)

# Clear any stale connections on module import
try:
    engine.dispose()
except Exception:
    pass  # Ignore errors during disposal

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create scoped session for thread-safe operations
db_session = scoped_session(SessionLocal)


def init_db():
    """Initialize database - create all tables"""
    try:
        # Test connection first
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        Base.metadata.create_all(bind=engine)
        print("[DB] Database tables created successfully!")
    except Exception as e:
        print(f"[WARNING] Failed to connect to database: {e}")
        # Show partial DATABASE_URL for debugging (hide password)
        db_url_display = DATABASE_URL
        if '@' in db_url_display:
            # Hide password in display
            parts = db_url_display.split('@')
            if len(parts) == 2:
                user_pass = parts[0].split('://')[-1]
                if ':' in user_pass:
                    user = user_pass.split(':')[0]
                    db_url_display = db_url_display.replace(user_pass, f"{user}:***")
        
        print(f"[INFO] DATABASE_URL: {db_url_display[:80]}..." if len(db_url_display) > 80 else f"[INFO] DATABASE_URL: {db_url_display}")
        print("[INFO] App will continue but database operations may fail.")
        print("[INFO] See backend/README_DATABASE.md for troubleshooting.")
        # Don't raise - allow app to start without DB


def is_database_error(exception):
    """
    Check if an exception is a database connection/authentication error.
    
    Returns:
        tuple: (is_db_error: bool, is_connection_error: bool)
        - is_db_error: True if it's any database-related error
        - is_connection_error: True if it's specifically a connection/auth error
    """
    # Check for SQLAlchemy database errors
    if isinstance(exception, (OperationalError, DatabaseError)):
        error_str = str(exception).lower()
        # Check for connection/auth errors
        connection_indicators = [
            'connection',
            'authentication',
            'password',
            'circuit breaker',
            'too many authentication errors',
            'could not connect',
            'connection refused',
            'connection timeout'
        ]
        is_conn_error = any(indicator in error_str for indicator in connection_indicators)
        return (True, is_conn_error)
    
    # Check for psycopg2 errors (wrapped in SQLAlchemy)
    error_str = str(exception).lower()
    if 'psycopg2' in error_str or 'operationalerror' in error_str:
        connection_indicators = [
            'connection',
            'authentication',
            'password',
            'circuit breaker',
            'too many authentication errors',
            'could not connect',
            'connection refused',
            'connection timeout'
        ]
        is_conn_error = any(indicator in error_str for indicator in connection_indicators)
        return (True, is_conn_error)
    
    return (False, False)