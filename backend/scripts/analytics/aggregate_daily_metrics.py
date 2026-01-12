"""
Daily Metrics Aggregator (Phase 1)
==================================

Aggregates recommendation request data into daily metrics.
Populates recommendation_metrics_daily table.

Run: python scripts/aggregate_daily_metrics.py [--date YYYY-MM-DD]
Schedule: Daily at 00:15 (after midnight)
"""

import os
import sys
from datetime import datetime, timedelta
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text


def aggregate_daily_metrics(target_date=None):
    """
    Aggregate metrics for a specific date.
    
    Args:
        target_date: Date to aggregate (default: yesterday)
    
    Computes:
    - Volume metrics (total requests, unique sessions)
    - Response time percentiles
    - Result quality metrics
    - Search pattern distribution
    """
    print("\n" + "="*60)
    print("DAILY METRICS AGGREGATION")
    print("="*60)
    
    # Default to yesterday
    if target_date is None:
        target_date = (datetime.utcnow() - timedelta(days=1)).date()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
    
    print(f"\nTarget date: {target_date}")
    
    with engine.connect() as conn:
        try:
            # Check if already aggregated
            existing = conn.execute(text("""
                SELECT id FROM recommendation_metrics_daily WHERE date = :date
            """), {'date': target_date}).fetchone()
            
            if existing:
                print(f"  [WARNING] Metrics for {target_date} already exist. Updating...")
            
            # Get requests for this date
            print("\n[STEP 1] Fetching request data...")
            
            requests_data = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_requests,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    
                    -- Response time stats
                    AVG(response_time_ms) as avg_response,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time_ms) as p50,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95,
                    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time_ms) as p99,
                    MAX(response_time_ms) as max_response,
                    
                    -- Result quality
                    AVG(top_score) as avg_top_score,
                    AVG(final_count) as avg_result_count,
                    
                    -- Problem indicators
                    AVG(CASE WHEN has_relaxed_results THEN 1 ELSE 0 END) as relaxed_rate,
                    AVG(CASE WHEN has_no_results THEN 1 ELSE 0 END) as no_results_rate,
                    AVG(CASE WHEN top_score < 50 AND top_score IS NOT NULL THEN 1 ELSE 0 END) as low_score_rate,
                    
                    -- Search patterns
                    COUNT(*) FILTER (WHERE selected_countries IS NOT NULL AND array_length(selected_countries, 1) > 0) as with_country,
                    COUNT(*) FILTER (WHERE selected_continents IS NOT NULL AND array_length(selected_continents, 1) > 0) as with_continent,
                    COUNT(*) FILTER (WHERE preferred_type_id IS NOT NULL) as with_type,
                    COUNT(*) FILTER (WHERE preferred_theme_ids IS NOT NULL AND array_length(preferred_theme_ids, 1) > 0) as with_themes,
                    COUNT(*) FILTER (WHERE budget IS NOT NULL) as with_budget,
                    COUNT(*) FILTER (WHERE year IS NOT NULL OR month IS NOT NULL) as with_dates
                    
                FROM recommendation_requests
                WHERE DATE(created_at) = :date
            """), {'date': target_date}).fetchone()
            
            total_requests = requests_data[0] or 0
            
            if total_requests == 0:
                print(f"  No requests found for {target_date}")
                return True
            
            print(f"  Found {total_requests} requests")
            
            # Build top searches (countries, continents, types, themes)
            print("\n[STEP 2] Computing top searches...")
            
            # Top countries
            top_countries = conn.execute(text("""
                SELECT c.id, c.name, COUNT(*) as count
                FROM recommendation_requests rr
                CROSS JOIN LATERAL unnest(rr.selected_countries) as country_id
                JOIN countries c ON c.id = country_id
                WHERE DATE(rr.created_at) = :date
                GROUP BY c.id, c.name
                ORDER BY count DESC
                LIMIT 10
            """), {'date': target_date}).fetchall()
            
            # Top continents
            top_continents = conn.execute(text("""
                SELECT continent, COUNT(*) as count
                FROM recommendation_requests rr
                CROSS JOIN LATERAL unnest(rr.selected_continents) as continent
                WHERE DATE(rr.created_at) = :date
                GROUP BY continent
                ORDER BY count DESC
                LIMIT 10
            """), {'date': target_date}).fetchall()
            
            # Top types
            top_types = conn.execute(text("""
                SELECT tt.id, tt.name, COUNT(*) as count
                FROM recommendation_requests rr
                JOIN trip_types tt ON tt.id = rr.preferred_type_id
                WHERE DATE(rr.created_at) = :date AND rr.preferred_type_id IS NOT NULL
                GROUP BY tt.id, tt.name
                ORDER BY count DESC
                LIMIT 10
            """), {'date': target_date}).fetchall()
            
            # Top themes
            top_themes = conn.execute(text("""
                SELECT t.id, t.name, COUNT(*) as count
                FROM recommendation_requests rr
                CROSS JOIN LATERAL unnest(rr.preferred_theme_ids) as theme_id
                JOIN tags t ON t.id = theme_id
                WHERE DATE(rr.created_at) = :date
                GROUP BY t.id, t.name
                ORDER BY count DESC
                LIMIT 10
            """), {'date': target_date}).fetchall()
            
            # Format as JSON
            import json
            top_countries_json = json.dumps([{'id': r[0], 'name': r[1], 'count': r[2]} for r in top_countries])
            top_continents_json = json.dumps([{'name': r[0], 'count': r[1]} for r in top_continents])
            top_types_json = json.dumps([{'id': r[0], 'name': r[1], 'count': r[2]} for r in top_types])
            top_themes_json = json.dumps([{'id': r[0], 'name': r[1], 'count': r[2]} for r in top_themes])
            
            # Upsert into daily metrics
            print("\n[STEP 3] Saving metrics...")
            
            conn.execute(text("""
                INSERT INTO recommendation_metrics_daily (
                    date, total_requests, unique_sessions,
                    avg_response_time_ms, p50_response_time_ms, p95_response_time_ms, 
                    p99_response_time_ms, max_response_time_ms,
                    avg_top_score, avg_result_count,
                    relaxed_trigger_rate, no_results_rate, low_score_rate,
                    searches_with_country, searches_with_continent, searches_with_type,
                    searches_with_themes, searches_with_budget, searches_with_dates,
                    top_countries, top_continents, top_types, top_themes,
                    created_at, updated_at
                ) VALUES (
                    :date, :total_requests, :unique_sessions,
                    :avg_response, :p50, :p95, :p99, :max_response,
                    :avg_top_score, :avg_result_count,
                    :relaxed_rate, :no_results_rate, :low_score_rate,
                    :with_country, :with_continent, :with_type,
                    :with_themes, :with_budget, :with_dates,
                    :top_countries::jsonb, :top_continents::jsonb, :top_types::jsonb, :top_themes::jsonb,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
                ON CONFLICT (date) DO UPDATE SET
                    total_requests = EXCLUDED.total_requests,
                    unique_sessions = EXCLUDED.unique_sessions,
                    avg_response_time_ms = EXCLUDED.avg_response_time_ms,
                    p50_response_time_ms = EXCLUDED.p50_response_time_ms,
                    p95_response_time_ms = EXCLUDED.p95_response_time_ms,
                    p99_response_time_ms = EXCLUDED.p99_response_time_ms,
                    max_response_time_ms = EXCLUDED.max_response_time_ms,
                    avg_top_score = EXCLUDED.avg_top_score,
                    avg_result_count = EXCLUDED.avg_result_count,
                    relaxed_trigger_rate = EXCLUDED.relaxed_trigger_rate,
                    no_results_rate = EXCLUDED.no_results_rate,
                    low_score_rate = EXCLUDED.low_score_rate,
                    searches_with_country = EXCLUDED.searches_with_country,
                    searches_with_continent = EXCLUDED.searches_with_continent,
                    searches_with_type = EXCLUDED.searches_with_type,
                    searches_with_themes = EXCLUDED.searches_with_themes,
                    searches_with_budget = EXCLUDED.searches_with_budget,
                    searches_with_dates = EXCLUDED.searches_with_dates,
                    top_countries = EXCLUDED.top_countries,
                    top_continents = EXCLUDED.top_continents,
                    top_types = EXCLUDED.top_types,
                    top_themes = EXCLUDED.top_themes,
                    updated_at = CURRENT_TIMESTAMP
            """), {
                'date': target_date,
                'total_requests': requests_data[0] or 0,
                'unique_sessions': requests_data[1] or 0,
                'avg_response': requests_data[2],
                'p50': int(requests_data[3]) if requests_data[3] else None,
                'p95': int(requests_data[4]) if requests_data[4] else None,
                'p99': int(requests_data[5]) if requests_data[5] else None,
                'max_response': requests_data[6],
                'avg_top_score': requests_data[7],
                'avg_result_count': requests_data[8],
                'relaxed_rate': requests_data[9],
                'no_results_rate': requests_data[10],
                'low_score_rate': requests_data[11],
                'with_country': requests_data[12] or 0,
                'with_continent': requests_data[13] or 0,
                'with_type': requests_data[14] or 0,
                'with_themes': requests_data[15] or 0,
                'with_budget': requests_data[16] or 0,
                'with_dates': requests_data[17] or 0,
                'top_countries': top_countries_json,
                'top_continents': top_continents_json,
                'top_types': top_types_json,
                'top_themes': top_themes_json,
            })
            
            conn.commit()
            
            # Verification
            print(f"\n[VERIFICATION]")
            print(f"  Date: {target_date}")
            print(f"  Total requests: {requests_data[0]}")
            print(f"  Unique sessions: {requests_data[1]}")
            print(f"  Avg response time: {requests_data[2]:.0f}ms" if requests_data[2] else "  Avg response: N/A")
            print(f"  Avg top score: {requests_data[7]:.1f}" if requests_data[7] else "  Avg top score: N/A")
            
            print("\n" + "="*60)
            print("AGGREGATION COMPLETE")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Aggregation failed: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Aggregate daily recommendation metrics')
    parser.add_argument('--date', type=str, help='Date to aggregate (YYYY-MM-DD), defaults to yesterday')
    args = parser.parse_args()
    
    success = aggregate_daily_metrics(args.date)
    exit(0 if success else 1)
