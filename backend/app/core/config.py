"""
Centralized Configuration Module
================================
Centralized entry point for all environment variables and settings.
Avoids env-var sprawl by consolidating all configuration access.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Centralized configuration class for the application"""
    
    # Flask Configuration
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_APP: str = os.getenv('FLASK_APP', 'app.main:app')
    FLASK_ENV: str = os.getenv('FLASK_ENV', 'development')
    
    # Database Configuration
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./smarttrip.db')
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000')
    
    # Supabase Configuration
    SUPABASE_JWT_SECRET: Optional[str] = os.getenv('SUPABASE_JWT_SECRET')
    
    @classmethod
    def get_allowed_origins_list(cls) -> list[str]:
        """Parse ALLOWED_ORIGINS into a list"""
        return [origin.strip() for origin in cls.ALLOWED_ORIGINS.split(',')]
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL with proper protocol handling"""
        db_url = cls.DATABASE_URL
        
        # Some providers use postgres:// but SQLAlchemy requires postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        
        # Ensure SSL mode for cloud databases (Supabase, etc.)
        if 'supabase' in db_url and 'sslmode' not in db_url:
            db_url = db_url + ('&' if '?' in db_url else '?') + 'sslmode=require'
        
        return db_url


# Export configuration instance
config = Config()
