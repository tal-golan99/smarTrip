"""
Migration: Add User Tracking Tables (Phase 1)
==============================================

Creates tables for user feedback signal collection:
- users: User identity (anonymous and registered)
- sessions: Browsing sessions with device info
- events: All user interactions with flexible metadata
- trip_interactions: Aggregated trip metrics for popularity

Run from backend folder: python migrations/_002_add_user_tracking.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, SessionLocal
from sqlalchemy import text, inspect


def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def upgrade():
    """Create user tracking tables for Phase 1."""
    
    print("\n" + "=" * 70)
    print("MIGRATION: Add User Tracking Tables (Phase 1)")
    print("=" * 70 + "\n")
    
    session = SessionLocal()
    
    try:
        dialect = engine.dialect.name
        is_postgres = dialect == 'postgresql'
        
        # ============================================
        # TABLE 1: users
        # Manages anonymous and registered users
        # ============================================
        if check_table_exists('users'):
            print("[SKIP] users table already exists")
        else:
            print("[CREATE] users table...")
            
            if is_postgres:
                create_sql = text("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        
                        -- Identity
                        anonymous_id UUID NOT NULL UNIQUE,
                        email VARCHAR(255) UNIQUE,
                        
                        -- Profile (populated after registration)
                        name VARCHAR(100),
                        name_he VARCHAR(100),
                        phone VARCHAR(20),
                        preferred_language VARCHAR(5) DEFAULT 'he',
                        
                        -- Tracking counters
                        first_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        total_sessions INTEGER DEFAULT 1,
                        total_searches INTEGER DEFAULT 0,
                        total_clicks INTEGER DEFAULT 0,
                        
                        -- Status
                        is_registered BOOLEAN DEFAULT FALSE,
                        is_active BOOLEAN DEFAULT TRUE,
                        
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
            else:
                # SQLite version
                create_sql = text("""
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        anonymous_id TEXT NOT NULL UNIQUE,
                        email TEXT UNIQUE,
                        name TEXT,
                        name_he TEXT,
                        phone TEXT,
                        preferred_language TEXT DEFAULT 'he',
                        first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_sessions INTEGER DEFAULT 1,
                        total_searches INTEGER DEFAULT 0,
                        total_clicks INTEGER DEFAULT 0,
                        is_registered INTEGER DEFAULT 0,
                        is_active INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            session.execute(create_sql)
            session.commit()
            
            # Create indexes
            indexes = [
                "CREATE INDEX idx_users_anonymous_id ON users(anonymous_id)",
                "CREATE INDEX idx_users_last_seen ON users(last_seen_at)",
            ]
            if is_postgres:
                indexes.append(
                    "CREATE INDEX idx_users_email ON users(email) WHERE email IS NOT NULL"
                )
            
            for idx_sql in indexes:
                try:
                    session.execute(text(idx_sql))
                except Exception as e:
                    print(f"  WARNING: Index issue: {e}")
            
            session.commit()
            print("  SUCCESS: Created users table with indexes")
        
        # ============================================
        # TABLE 2: sessions
        # Tracks browsing sessions
        # device_type comes from frontend (not user-agent parsing)
        # ============================================
        if check_table_exists('sessions'):
            print("[SKIP] sessions table already exists")
        else:
            print("[CREATE] sessions table...")
            
            if is_postgres:
                create_sql = text("""
                    CREATE TABLE sessions (
                        id SERIAL PRIMARY KEY,
                        
                        -- Identity
                        session_id UUID NOT NULL UNIQUE,
                        user_id INTEGER REFERENCES users(id),
                        anonymous_id UUID NOT NULL,
                        
                        -- Timing
                        started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        ended_at TIMESTAMP WITH TIME ZONE,
                        duration_seconds INTEGER,
                        
                        -- Device/context (device_type from frontend)
                        user_agent TEXT,
                        ip_address INET,
                        referrer TEXT,
                        device_type VARCHAR(20),
                        
                        -- Activity counters
                        search_count INTEGER DEFAULT 0,
                        click_count INTEGER DEFAULT 0,
                        save_count INTEGER DEFAULT 0,
                        contact_count INTEGER DEFAULT 0,
                        
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
            else:
                create_sql = text("""
                    CREATE TABLE sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL UNIQUE,
                        user_id INTEGER REFERENCES users(id),
                        anonymous_id TEXT NOT NULL,
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ended_at TIMESTAMP,
                        duration_seconds INTEGER,
                        user_agent TEXT,
                        ip_address TEXT,
                        referrer TEXT,
                        device_type TEXT,
                        search_count INTEGER DEFAULT 0,
                        click_count INTEGER DEFAULT 0,
                        save_count INTEGER DEFAULT 0,
                        contact_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            session.execute(create_sql)
            session.commit()
            
            indexes = [
                "CREATE INDEX idx_sessions_session_id ON sessions(session_id)",
                "CREATE INDEX idx_sessions_user_id ON sessions(user_id)",
                "CREATE INDEX idx_sessions_started_at ON sessions(started_at)",
                "CREATE INDEX idx_sessions_anonymous_id ON sessions(anonymous_id)",
            ]
            
            for idx_sql in indexes:
                try:
                    session.execute(text(idx_sql))
                except Exception as e:
                    print(f"  WARNING: Index issue: {e}")
            
            session.commit()
            print("  SUCCESS: Created sessions table with indexes")
        
        # ============================================
        # TABLE 3: events
        # Core event tracking with flexible metadata
        # Supports: duration_seconds, filter_name, source, etc.
        # ============================================
        if check_table_exists('events'):
            print("[SKIP] events table already exists")
        else:
            print("[CREATE] events table...")
            
            if is_postgres:
                create_sql = text("""
                    CREATE TABLE events (
                        id BIGSERIAL PRIMARY KEY,
                        
                        -- Identity
                        user_id INTEGER REFERENCES users(id),
                        session_id UUID NOT NULL,
                        anonymous_id UUID NOT NULL,
                        
                        -- Event classification
                        event_type VARCHAR(50) NOT NULL,
                        event_category VARCHAR(30) NOT NULL,
                        
                        -- Context
                        trip_id INTEGER,
                        recommendation_request_id UUID,
                        
                        -- Source field for click attribution
                        source VARCHAR(50),
                        
                        -- Flexible event data (JSONB for queries)
                        -- Stores: duration_seconds, filter_name, old_value, new_value, etc.
                        -- Note: Named 'event_data' because 'metadata' is reserved by SQLAlchemy ORM
                        event_data JSONB DEFAULT '{}',
                        
                        -- Position/ranking context (for ML training)
                        position_in_results INTEGER,
                        score_at_time DECIMAL(5,2),
                        
                        -- Timing
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        client_timestamp TIMESTAMP WITH TIME ZONE,
                        
                        -- Page context
                        page_url TEXT,
                        referrer TEXT,
                        
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
            else:
                create_sql = text("""
                    CREATE TABLE events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER REFERENCES users(id),
                        session_id TEXT NOT NULL,
                        anonymous_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        event_category TEXT NOT NULL,
                        trip_id INTEGER,
                        recommendation_request_id TEXT,
                        source TEXT,
                        event_data TEXT DEFAULT '{}',
                        position_in_results INTEGER,
                        score_at_time REAL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        client_timestamp TIMESTAMP,
                        page_url TEXT,
                        referrer TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            session.execute(create_sql)
            session.commit()
            
            # Comprehensive indexes for analytics queries
            indexes = [
                "CREATE INDEX idx_events_user_id ON events(user_id)",
                "CREATE INDEX idx_events_session_id ON events(session_id)",
                "CREATE INDEX idx_events_trip_id ON events(trip_id)",
                "CREATE INDEX idx_events_type ON events(event_type)",
                "CREATE INDEX idx_events_timestamp ON events(timestamp)",
                "CREATE INDEX idx_events_category ON events(event_category)",
                "CREATE INDEX idx_events_source ON events(source)",
            ]
            
            # Composite indexes for common queries
            if is_postgres:
                indexes.extend([
                    "CREATE INDEX idx_events_user_timestamp ON events(user_id, timestamp)",
                    "CREATE INDEX idx_events_trip_timestamp ON events(trip_id, timestamp)",
                    "CREATE INDEX idx_events_conversions ON events(trip_id, timestamp) WHERE event_category = 'conversion'",
                ])
            
            for idx_sql in indexes:
                try:
                    session.execute(text(idx_sql))
                except Exception as e:
                    print(f"  WARNING: Index issue: {e}")
            
            session.commit()
            print("  SUCCESS: Created events table with indexes")
        
        # ============================================
        # TABLE 4: trip_interactions
        # Aggregated metrics for popularity ranking
        # ============================================
        if check_table_exists('trip_interactions'):
            print("[SKIP] trip_interactions table already exists")
        else:
            print("[CREATE] trip_interactions table...")
            
            if is_postgres:
                create_sql = text("""
                    CREATE TABLE trip_interactions (
                        id SERIAL PRIMARY KEY,
                        trip_id INTEGER NOT NULL UNIQUE,
                        
                        -- Impression metrics
                        impression_count INTEGER DEFAULT 0,
                        unique_viewers INTEGER DEFAULT 0,
                        
                        -- Engagement metrics
                        click_count INTEGER DEFAULT 0,
                        unique_clickers INTEGER DEFAULT 0,
                        total_dwell_time_seconds INTEGER DEFAULT 0,
                        avg_dwell_time_seconds INTEGER DEFAULT 0,
                        
                        -- Conversion metrics
                        save_count INTEGER DEFAULT 0,
                        whatsapp_contact_count INTEGER DEFAULT 0,
                        phone_contact_count INTEGER DEFAULT 0,
                        booking_start_count INTEGER DEFAULT 0,
                        
                        -- Computed rates
                        click_through_rate DECIMAL(5,4),
                        save_rate DECIMAL(5,4),
                        contact_rate DECIMAL(5,4),
                        
                        -- Time-based metrics (for trending)
                        impressions_7d INTEGER DEFAULT 0,
                        clicks_7d INTEGER DEFAULT 0,
                        last_clicked_at TIMESTAMP WITH TIME ZONE,
                        
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
            else:
                create_sql = text("""
                    CREATE TABLE trip_interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trip_id INTEGER NOT NULL UNIQUE,
                        impression_count INTEGER DEFAULT 0,
                        unique_viewers INTEGER DEFAULT 0,
                        click_count INTEGER DEFAULT 0,
                        unique_clickers INTEGER DEFAULT 0,
                        total_dwell_time_seconds INTEGER DEFAULT 0,
                        avg_dwell_time_seconds INTEGER DEFAULT 0,
                        save_count INTEGER DEFAULT 0,
                        whatsapp_contact_count INTEGER DEFAULT 0,
                        phone_contact_count INTEGER DEFAULT 0,
                        booking_start_count INTEGER DEFAULT 0,
                        click_through_rate REAL,
                        save_rate REAL,
                        contact_rate REAL,
                        impressions_7d INTEGER DEFAULT 0,
                        clicks_7d INTEGER DEFAULT 0,
                        last_clicked_at TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            session.execute(create_sql)
            session.commit()
            
            indexes = [
                "CREATE INDEX idx_trip_interactions_trip_id ON trip_interactions(trip_id)",
                "CREATE INDEX idx_trip_interactions_clicks ON trip_interactions(click_count DESC)",
            ]
            
            if is_postgres:
                indexes.append(
                    "CREATE INDEX idx_trip_interactions_ctr ON trip_interactions(click_through_rate DESC NULLS LAST)"
                )
            
            for idx_sql in indexes:
                try:
                    session.execute(text(idx_sql))
                except Exception as e:
                    print(f"  WARNING: Index issue: {e}")
            
            session.commit()
            print("  SUCCESS: Created trip_interactions table with indexes")
        
        print("\n" + "=" * 70)
        print("PHASE 1 MIGRATION COMPLETE")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: Migration failed: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        session.close()


def downgrade():
    """Remove user tracking tables (in correct order for foreign keys)."""
    
    print("\n" + "=" * 70)
    print("ROLLBACK: Remove User Tracking Tables")
    print("=" * 70 + "\n")
    
    session = SessionLocal()
    
    try:
        # Drop in reverse order due to foreign keys
        tables = ['events', 'trip_interactions', 'sessions', 'users']
        
        for table in tables:
            if check_table_exists(table):
                print(f"[DROP] {table}...")
                # Use CASCADE for PostgreSQL
                try:
                    session.execute(text(f"DROP TABLE {table} CASCADE"))
                except:
                    session.execute(text(f"DROP TABLE {table}"))
                print(f"  SUCCESS: Dropped {table}")
            else:
                print(f"[SKIP] {table} does not exist")
        
        session.commit()
        
        print("\n" + "=" * 70)
        print("ROLLBACK COMPLETE")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: Rollback failed: {e}")
        session.rollback()
        raise
    
    finally:
        session.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Phase 1 user tracking migration')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    
    args = parser.parse_args()
    
    if args.rollback:
        downgrade()
    else:
        upgrade()
