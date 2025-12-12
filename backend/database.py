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
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/smarttrip')

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


def get_db():
    """
    Dependency function to get database session
    Use this in Flask routes to get a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


