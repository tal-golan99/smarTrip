"""
Database configuration and session management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
# Default to SQLite for local development if no DATABASE_URL is set
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./smarttrip.db')

# Some providers use postgres:// but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Ensure SSL mode for cloud databases (Supabase, etc.)
if 'supabase' in DATABASE_URL and 'sslmode' not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL + ('&' if '?' in DATABASE_URL else '?') + 'sslmode=require'

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True if os.getenv('FLASK_ENV') == 'development' else False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Verify connections before using them
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create scoped session for thread-safe operations
db_session = scoped_session(SessionLocal)


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def drop_db():
    """Drop all database tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    print("WARNING: All database tables dropped!")
