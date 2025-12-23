"""
Migration: Add Recommendation Logging Tables
=============================================

Creates tables for Phase 0 measurement infrastructure:
- recommendation_requests: Logs all recommendation API calls
- recommendation_metrics_daily: Aggregated daily metrics
- evaluation_scenarios: Reproducible test scenarios

Run from backend folder: python migrations/001_add_recommendation_logging.py
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
    """Create recommendation logging tables."""
    
    print("\n" + "=" * 70)
    print("MIGRATION: Add Recommendation Logging Tables")
    print("=" * 70 + "\n")
    
    session = SessionLocal()
    
    try:
        # ============================================
        # TABLE 1: recommendation_requests
        # ============================================
        if check_table_exists('recommendation_requests'):
            print("[SKIP] recommendation_requests table already exists")
        else:
            print("[CREATE] recommendation_requests table...")
            
            # Check if we're using PostgreSQL or SQLite
            dialect = engine.dialect.name
            
            if dialect == 'postgresql':
                create_sql = text("""
                    CREATE TABLE recommendation_requests (
                        id SERIAL PRIMARY KEY,
                        
                        -- Request identification
                        request_id UUID NOT NULL UNIQUE,
                        session_id VARCHAR(64),
                        user_id INTEGER,
                        
                        -- Timestamp
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        
                        -- Request input (what user asked for)
                        preferences JSONB NOT NULL,
                        
                        -- Parsed preferences (for easy querying)
                        selected_countries INTEGER[],
                        selected_continents TEXT[],
                        preferred_type_id INTEGER,
                        preferred_theme_ids INTEGER[],
                        min_duration INTEGER,
                        max_duration INTEGER,
                        budget DECIMAL(10,2),
                        difficulty INTEGER,
                        year VARCHAR(4),
                        month VARCHAR(2),
                        
                        -- Response metrics
                        response_time_ms INTEGER NOT NULL,
                        total_candidates INTEGER NOT NULL,
                        primary_count INTEGER NOT NULL,
                        relaxed_count INTEGER NOT NULL DEFAULT 0,
                        final_count INTEGER NOT NULL,
                        
                        -- Flags
                        has_relaxed_results BOOLEAN DEFAULT FALSE,
                        has_no_results BOOLEAN DEFAULT FALSE,
                        
                        -- Score distribution
                        top_score DECIMAL(5,2),
                        avg_score DECIMAL(5,2),
                        min_score DECIMAL(5,2),
                        score_std_dev DECIMAL(5,2),
                        
                        -- Result details
                        result_trip_ids INTEGER[] NOT NULL,
                        result_scores DECIMAL(5,2)[] NOT NULL,
                        
                        -- Algorithm version
                        algorithm_version VARCHAR(32) DEFAULT 'v1.0'
                    )
                """)
            else:
                # SQLite version (simplified - no arrays)
                create_sql = text("""
                    CREATE TABLE recommendation_requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        request_id TEXT NOT NULL UNIQUE,
                        session_id TEXT,
                        user_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        preferences TEXT NOT NULL,
                        selected_countries TEXT,
                        selected_continents TEXT,
                        preferred_type_id INTEGER,
                        preferred_theme_ids TEXT,
                        min_duration INTEGER,
                        max_duration INTEGER,
                        budget REAL,
                        difficulty INTEGER,
                        year TEXT,
                        month TEXT,
                        response_time_ms INTEGER NOT NULL,
                        total_candidates INTEGER NOT NULL,
                        primary_count INTEGER NOT NULL,
                        relaxed_count INTEGER NOT NULL DEFAULT 0,
                        final_count INTEGER NOT NULL,
                        has_relaxed_results INTEGER DEFAULT 0,
                        has_no_results INTEGER DEFAULT 0,
                        top_score REAL,
                        avg_score REAL,
                        min_score REAL,
                        score_std_dev REAL,
                        result_trip_ids TEXT NOT NULL,
                        result_scores TEXT NOT NULL,
                        algorithm_version TEXT DEFAULT 'v1.0'
                    )
                """)
            
            session.execute(create_sql)
            session.commit()
            print("  SUCCESS: Created recommendation_requests table")
            
            # Create indexes (PostgreSQL only for array indexes)
            if dialect == 'postgresql':
                indexes = [
                    "CREATE INDEX idx_rec_requests_created_at ON recommendation_requests(created_at)",
                    "CREATE INDEX idx_rec_requests_session ON recommendation_requests(session_id)",
                    "CREATE INDEX idx_rec_requests_has_relaxed ON recommendation_requests(has_relaxed_results)",
                    "CREATE INDEX idx_rec_requests_no_results ON recommendation_requests(has_no_results)",
                    "CREATE INDEX idx_rec_requests_type ON recommendation_requests(preferred_type_id)",
                ]
            else:
                indexes = [
                    "CREATE INDEX idx_rec_requests_created_at ON recommendation_requests(created_at)",
                    "CREATE INDEX idx_rec_requests_session ON recommendation_requests(session_id)",
                ]
            
            for idx_sql in indexes:
                try:
                    session.execute(text(idx_sql))
                except Exception as e:
                    print(f"  WARNING: Index creation issue: {e}")
            
            session.commit()
            print("  SUCCESS: Created indexes")
        
        # ============================================
        # TABLE 2: recommendation_metrics_daily
        # ============================================
        if check_table_exists('recommendation_metrics_daily'):
            print("[SKIP] recommendation_metrics_daily table already exists")
        else:
            print("[CREATE] recommendation_metrics_daily table...")
            
            dialect = engine.dialect.name
            
            if dialect == 'postgresql':
                create_sql = text("""
                    CREATE TABLE recommendation_metrics_daily (
                        id SERIAL PRIMARY KEY,
                        date DATE NOT NULL UNIQUE,
                        
                        -- Volume metrics
                        total_requests INTEGER NOT NULL DEFAULT 0,
                        unique_sessions INTEGER NOT NULL DEFAULT 0,
                        
                        -- Response time metrics
                        avg_response_time_ms DECIMAL(10,2),
                        p50_response_time_ms INTEGER,
                        p95_response_time_ms INTEGER,
                        p99_response_time_ms INTEGER,
                        max_response_time_ms INTEGER,
                        
                        -- Result quality metrics
                        avg_top_score DECIMAL(5,2),
                        avg_result_count DECIMAL(5,2),
                        
                        -- Problem indicators
                        relaxed_trigger_rate DECIMAL(5,4),
                        no_results_rate DECIMAL(5,4),
                        low_score_rate DECIMAL(5,4),
                        
                        -- Search pattern distribution
                        searches_with_country INTEGER,
                        searches_with_continent INTEGER,
                        searches_with_type INTEGER,
                        searches_with_themes INTEGER,
                        searches_with_budget INTEGER,
                        searches_with_dates INTEGER,
                        
                        -- Top searched (JSONB)
                        top_countries JSONB,
                        top_continents JSONB,
                        top_types JSONB,
                        top_themes JSONB,
                        
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
            else:
                create_sql = text("""
                    CREATE TABLE recommendation_metrics_daily (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL UNIQUE,
                        total_requests INTEGER NOT NULL DEFAULT 0,
                        unique_sessions INTEGER NOT NULL DEFAULT 0,
                        avg_response_time_ms REAL,
                        p50_response_time_ms INTEGER,
                        p95_response_time_ms INTEGER,
                        p99_response_time_ms INTEGER,
                        max_response_time_ms INTEGER,
                        avg_top_score REAL,
                        avg_result_count REAL,
                        relaxed_trigger_rate REAL,
                        no_results_rate REAL,
                        low_score_rate REAL,
                        searches_with_country INTEGER,
                        searches_with_continent INTEGER,
                        searches_with_type INTEGER,
                        searches_with_themes INTEGER,
                        searches_with_budget INTEGER,
                        searches_with_dates INTEGER,
                        top_countries TEXT,
                        top_continents TEXT,
                        top_types TEXT,
                        top_themes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            session.execute(create_sql)
            session.commit()
            print("  SUCCESS: Created recommendation_metrics_daily table")
        
        # ============================================
        # TABLE 3: evaluation_scenarios
        # ============================================
        if check_table_exists('evaluation_scenarios'):
            print("[SKIP] evaluation_scenarios table already exists")
        else:
            print("[CREATE] evaluation_scenarios table...")
            
            dialect = engine.dialect.name
            
            if dialect == 'postgresql':
                create_sql = text("""
                    CREATE TABLE evaluation_scenarios (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        category VARCHAR(50),
                        preferences JSONB NOT NULL,
                        expected_min_results INTEGER DEFAULT 1,
                        expected_min_top_score DECIMAL(5,2),
                        expected_trip_types INTEGER[],
                        expected_countries INTEGER[],
                        baseline_result_ids INTEGER[],
                        baseline_scores DECIMAL(5,2)[],
                        baseline_captured_at TIMESTAMP WITH TIME ZONE,
                        is_active BOOLEAN DEFAULT TRUE,
                        priority INTEGER DEFAULT 5,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
            else:
                create_sql = text("""
                    CREATE TABLE evaluation_scenarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        category TEXT,
                        preferences TEXT NOT NULL,
                        expected_min_results INTEGER DEFAULT 1,
                        expected_min_top_score REAL,
                        expected_trip_types TEXT,
                        expected_countries TEXT,
                        baseline_result_ids TEXT,
                        baseline_scores TEXT,
                        baseline_captured_at TIMESTAMP,
                        is_active INTEGER DEFAULT 1,
                        priority INTEGER DEFAULT 5,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            session.execute(create_sql)
            session.commit()
            print("  SUCCESS: Created evaluation_scenarios table")
        
        print("\n" + "=" * 70)
        print("MIGRATION COMPLETE")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: Migration failed: {e}")
        session.rollback()
        raise
    
    finally:
        session.close()


def downgrade():
    """Remove recommendation logging tables."""
    
    print("\n" + "=" * 70)
    print("ROLLBACK: Remove Recommendation Logging Tables")
    print("=" * 70 + "\n")
    
    session = SessionLocal()
    
    try:
        tables = ['evaluation_scenarios', 'recommendation_metrics_daily', 'recommendation_requests']
        
        for table in tables:
            if check_table_exists(table):
                print(f"[DROP] {table}...")
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
    
    parser = argparse.ArgumentParser(description='Run database migration')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    
    args = parser.parse_args()
    
    if args.rollback:
        downgrade()
    else:
        upgrade()
