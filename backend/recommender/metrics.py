"""
Recommendation Metrics Aggregation
==================================

Handles computation and storage of recommendation metrics.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import statistics

from app.core.database import SessionLocal


class MetricsAggregator:
    """
    Computes and stores recommendation metrics.
    
    Usage:
        aggregator = MetricsAggregator()
        
        # Compute daily metrics
        aggregator.aggregate_daily_metrics(date.today())
        
        # Get metrics for dashboard
        metrics = aggregator.get_metrics_range(
            start=date.today() - timedelta(days=7),
            end=date.today()
        )
    """
    
    def __init__(self):
        """Initialize the metrics aggregator."""
        pass
    
    def aggregate_daily_metrics(self, target_date: date) -> Dict[str, Any]:
        """
        Compute all metrics for a specific date.
        
        Args:
            target_date: Date to aggregate metrics for
            
        Returns:
            Dict with computed metrics
        """
        try:
            session = SessionLocal()
            
            # Check if tables exist
            from sqlalchemy import inspect, text
            inspector = inspect(session.bind)
            
            if 'recommendation_requests' not in inspector.get_table_names():
                session.close()
                return self._empty_metrics(target_date)
            
            # Query metrics for the date
            query = text("""
                SELECT
                    COUNT(*) as total_requests,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    AVG(response_time_ms) as avg_response_time_ms,
                    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY response_time_ms) as p50_response_time_ms,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_response_time_ms,
                    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time_ms) as p99_response_time_ms,
                    MAX(response_time_ms) as max_response_time_ms,
                    AVG(top_score) as avg_top_score,
                    AVG(final_count) as avg_result_count,
                    SUM(CASE WHEN has_relaxed_results THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*), 0) as relaxed_trigger_rate,
                    SUM(CASE WHEN has_no_results THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*), 0) as no_results_rate,
                    SUM(CASE WHEN top_score < 50 THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*), 0) as low_score_rate,
                    SUM(CASE WHEN cardinality(selected_countries) > 0 THEN 1 ELSE 0 END) as searches_with_country,
                    SUM(CASE WHEN cardinality(selected_continents) > 0 THEN 1 ELSE 0 END) as searches_with_continent,
                    SUM(CASE WHEN preferred_type_id IS NOT NULL THEN 1 ELSE 0 END) as searches_with_type,
                    SUM(CASE WHEN cardinality(preferred_theme_ids) > 0 THEN 1 ELSE 0 END) as searches_with_themes,
                    SUM(CASE WHEN budget IS NOT NULL THEN 1 ELSE 0 END) as searches_with_budget,
                    SUM(CASE WHEN year IS NOT NULL OR month IS NOT NULL THEN 1 ELSE 0 END) as searches_with_dates
                FROM recommendation_requests
                WHERE DATE(created_at) = :target_date
            """)
            
            result = session.execute(query, {'target_date': target_date}).fetchone()
            session.close()
            
            if result is None or result[0] == 0:
                return self._empty_metrics(target_date)
            
            return {
                'date': target_date.isoformat(),
                'total_requests': result[0] or 0,
                'unique_sessions': result[1] or 0,
                'avg_response_time_ms': round(result[2], 2) if result[2] else 0,
                'p50_response_time_ms': int(result[3]) if result[3] else 0,
                'p95_response_time_ms': int(result[4]) if result[4] else 0,
                'p99_response_time_ms': int(result[5]) if result[5] else 0,
                'max_response_time_ms': result[6] or 0,
                'avg_top_score': round(result[7], 2) if result[7] else 0,
                'avg_result_count': round(result[8], 2) if result[8] else 0,
                'relaxed_trigger_rate': round(result[9], 4) if result[9] else 0,
                'no_results_rate': round(result[10], 4) if result[10] else 0,
                'low_score_rate': round(result[11], 4) if result[11] else 0,
                'searches_with_country': result[12] or 0,
                'searches_with_continent': result[13] or 0,
                'searches_with_type': result[14] or 0,
                'searches_with_themes': result[15] or 0,
                'searches_with_budget': result[16] or 0,
                'searches_with_dates': result[17] or 0,
            }
            
        except Exception as e:
            print(f"[WARNING] Failed to aggregate metrics: {e}")
            return self._empty_metrics(target_date)
    
    def _empty_metrics(self, target_date: date) -> Dict[str, Any]:
        """Return empty metrics structure."""
        return {
            'date': target_date.isoformat(),
            'total_requests': 0,
            'unique_sessions': 0,
            'avg_response_time_ms': 0,
            'p50_response_time_ms': 0,
            'p95_response_time_ms': 0,
            'p99_response_time_ms': 0,
            'max_response_time_ms': 0,
            'avg_top_score': 0,
            'avg_result_count': 0,
            'relaxed_trigger_rate': 0,
            'no_results_rate': 0,
            'low_score_rate': 0,
            'searches_with_country': 0,
            'searches_with_continent': 0,
            'searches_with_type': 0,
            'searches_with_themes': 0,
            'searches_with_budget': 0,
            'searches_with_dates': 0,
        }
    
    def get_metrics_range(
        self, 
        start: date, 
        end: date
    ) -> List[Dict[str, Any]]:
        """
        Get metrics for a date range.
        
        Args:
            start: Start date (inclusive)
            end: End date (inclusive)
            
        Returns:
            List of daily metrics dicts
        """
        metrics = []
        current = start
        
        while current <= end:
            metrics.append(self.aggregate_daily_metrics(current))
            current += timedelta(days=1)
        
        return metrics
    
    def get_current_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get summary metrics for the last N days.
        
        Args:
            days: Number of days to include
            
        Returns:
            Dict with summary metrics
        """
        try:
            session = SessionLocal()
            
            from sqlalchemy import inspect, text
            inspector = inspect(session.bind)
            
            if 'recommendation_requests' not in inspector.get_table_names():
                session.close()
                return self._empty_summary(days)
            
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            query = text("""
                SELECT
                    COUNT(*) as total_requests,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    AVG(response_time_ms) as avg_response_time_ms,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_response_time_ms,
                    AVG(top_score) as avg_top_score,
                    SUM(CASE WHEN has_relaxed_results THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*), 0) as relaxed_trigger_rate,
                    SUM(CASE WHEN has_no_results THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*), 0) as no_results_rate
                FROM recommendation_requests
                WHERE created_at >= :cutoff
            """)
            
            result = session.execute(query, {'cutoff': cutoff}).fetchone()
            session.close()
            
            if result is None or result[0] == 0:
                return self._empty_summary(days)
            
            return {
                'period': f'last_{days}_days',
                'total_requests': result[0] or 0,
                'unique_sessions': result[1] or 0,
                'avg_response_time_ms': round(result[2], 2) if result[2] else 0,
                'p95_response_time_ms': int(result[3]) if result[3] else 0,
                'avg_top_score': round(result[4], 2) if result[4] else 0,
                'relaxed_trigger_rate': round(result[5], 4) if result[5] else 0,
                'no_results_rate': round(result[6], 4) if result[6] else 0,
            }
            
        except Exception as e:
            print(f"[WARNING] Failed to get current metrics: {e}")
            return self._empty_summary(days)
    
    def _empty_summary(self, days: int) -> Dict[str, Any]:
        """Return empty summary structure."""
        return {
            'period': f'last_{days}_days',
            'total_requests': 0,
            'unique_sessions': 0,
            'avg_response_time_ms': 0,
            'p95_response_time_ms': 0,
            'avg_top_score': 0,
            'relaxed_trigger_rate': 0,
            'no_results_rate': 0,
        }
    
    def get_top_searches(self, days: int = 7, limit: int = 10) -> Dict[str, Any]:
        """
        Get most common search patterns.
        
        Args:
            days: Number of days to analyze
            limit: Max items per category
            
        Returns:
            Dict with top countries, continents, types, themes
        """
        try:
            session = SessionLocal()
            
            from sqlalchemy import inspect, text
            inspector = inspect(session.bind)
            
            if 'recommendation_requests' not in inspector.get_table_names():
                session.close()
                return {'top_countries': [], 'top_continents': [], 'top_types': [], 'top_themes': []}
            
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            # Get top continents
            continent_query = text("""
                SELECT unnest(selected_continents) as continent, COUNT(*) as count
                FROM recommendation_requests
                WHERE created_at >= :cutoff AND cardinality(selected_continents) > 0
                GROUP BY continent
                ORDER BY count DESC
                LIMIT :limit
            """)
            
            continents = session.execute(continent_query, {'cutoff': cutoff, 'limit': limit}).fetchall()
            
            # Get top types
            type_query = text("""
                SELECT preferred_type_id, COUNT(*) as count
                FROM recommendation_requests
                WHERE created_at >= :cutoff AND preferred_type_id IS NOT NULL
                GROUP BY preferred_type_id
                ORDER BY count DESC
                LIMIT :limit
            """)
            
            types = session.execute(type_query, {'cutoff': cutoff, 'limit': limit}).fetchall()
            
            session.close()
            
            return {
                'top_continents': [{'name': r[0], 'count': r[1]} for r in continents],
                'top_types': [{'id': r[0], 'count': r[1]} for r in types],
            }
            
        except Exception as e:
            print(f"[WARNING] Failed to get top searches: {e}")
            return {'top_countries': [], 'top_continents': [], 'top_types': [], 'top_themes': []}


# Singleton instance
_aggregator_instance = None

def get_aggregator() -> MetricsAggregator:
    """Get the singleton aggregator instance."""
    global _aggregator_instance
    if _aggregator_instance is None:
        _aggregator_instance = MetricsAggregator()
    return _aggregator_instance
