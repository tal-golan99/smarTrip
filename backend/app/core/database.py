"""
Database configuration and session management
V2 Schema: Uses models_v2.Base for table creation
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError, DatabaseError
# V2 Migration: Use V2 Base for table creation
from app.models.trip import Base
from dotenv import load_dotenv

# Load environment variables (if not already loaded by main.py)
# This ensures database.py can be imported independently if needed
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./smarttrip.db')

# Some providers use postgres:// but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

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