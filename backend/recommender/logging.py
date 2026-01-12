"""
Recommendation Request/Response Logging
========================================

Handles structured logging of all recommendation API calls for analysis.
"""

import uuid
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional
from decimal import Decimal

# Import database components
from app.core.database import SessionLocal
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


class RecommendationLogger:
    """
    Handles logging of recommendation requests and responses.
    
    Usage:
        logger = RecommendationLogger()
        request_id = logger.start_request(session_id='abc123')
        
        # ... process recommendations ...
        
        logger.log_request(
            request_id=request_id,
            preferences=prefs,
            results=results,
            total_candidates=100,
            primary_count=8,
            relaxed_count=2
        )
    """
    
    def __init__(self, enabled: bool = True, async_mode: bool = False):
        """
        Initialize the recommendation logger.
        
        Args:
            enabled: Whether logging is enabled
            async_mode: Whether to log asynchronously (not blocking)
        """
        self.enabled = enabled
        self.async_mode = async_mode
        self._request_timers: Dict[str, float] = {}
    
    def generate_request_id(self) -> str:
        """Generate a unique request ID (UUID4)."""
        return str(uuid.uuid4())
    
    def start_request_timer(self, request_id: str) -> None:
        """Mark the start time for a request."""
        self._request_timers[request_id] = time.time()
    
    def get_response_time_ms(self, request_id: str) -> int:
        """
        Calculate response time in milliseconds.
        
        Returns:
            Response time in ms, or 0 if timer not found
        """
        start_time = self._request_timers.pop(request_id, None)
        if start_time is None:
            return 0
        return int((time.time() - start_time) * 1000)
    
    def parse_preferences(self, prefs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse preferences into queryable fields.
        
        Args:
            prefs: Raw preferences dict from API request
            
        Returns:
            Dict with parsed, queryable fields
        """
        return {
            'selected_countries': prefs.get('selected_countries', []),
            'selected_continents': prefs.get('selected_continents', []),
            'preferred_type_id': prefs.get('preferred_type_id'),
            'preferred_theme_ids': prefs.get('preferred_theme_ids', []),
            'min_duration': prefs.get('min_duration'),
            'max_duration': prefs.get('max_duration'),
            'budget': float(prefs['budget']) if prefs.get('budget') else None,
            'difficulty': prefs.get('difficulty'),
            'year': prefs.get('year'),
            'month': prefs.get('month'),
        }
    
    def calculate_score_stats(self, scores: List[float]) -> Dict[str, Optional[float]]:
        """
        Calculate score statistics.
        
        Args:
            scores: List of match scores
            
        Returns:
            Dict with top, avg, min, std_dev scores
        """
        if not scores:
            return {
                'top_score': None,
                'avg_score': None,
                'min_score': None,
                'score_std_dev': None,
            }
        
        return {
            'top_score': round(max(scores), 2),
            'avg_score': round(statistics.mean(scores), 2),
            'min_score': round(min(scores), 2),
            'score_std_dev': round(statistics.stdev(scores), 2) if len(scores) > 1 else 0.0,
        }
    
    def log_request(
        self,
        request_id: str,
        preferences: Dict[str, Any],
        results: List[Dict[str, Any]],
        total_candidates: int,
        primary_count: int,
        relaxed_count: int = 0,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        algorithm_version: str = 'v1.0',
        search_type: str = 'exploration',  # Phase 1: 'exploration' or 'focused_search'
    ) -> bool:
        """
        Log a recommendation request to the database.
        
        Args:
            request_id: Unique request identifier
            preferences: User preferences dict
            results: List of recommended trips
            total_candidates: Number of trips that passed hard filters
            primary_count: Number of primary tier results
            relaxed_count: Number of relaxed tier results
            session_id: Browser session ID (optional)
            user_id: User ID if logged in (optional)
            algorithm_version: Version of the algorithm used
            search_type: Phase 1 classification ('exploration' or 'focused_search')
            
        Returns:
            True if logged successfully, False otherwise
        """
        if not self.enabled:
            return True
        
        try:
            # Calculate response time
            response_time_ms = self.get_response_time_ms(request_id)
            
            # Parse preferences
            parsed_prefs = self.parse_preferences(preferences)
            
            # Extract scores and trip IDs
            result_trip_ids = [r.get('id') for r in results if r.get('id')]
            result_scores = [r.get('match_score', 0) for r in results]
            
            # Calculate score statistics
            score_stats = self.calculate_score_stats(result_scores)
            
            # Determine flags
            final_count = len(results)
            has_relaxed = relaxed_count > 0
            has_no_results = final_count == 0
            
            # Build log record
            log_record = {
                'request_id': request_id,
                'session_id': session_id,
                'user_id': user_id,
                'created_at': datetime.utcnow(),
                'preferences': preferences,
                'selected_countries': parsed_prefs['selected_countries'],
                'selected_continents': parsed_prefs['selected_continents'],
                'preferred_type_id': parsed_prefs['preferred_type_id'],
                'preferred_theme_ids': parsed_prefs['preferred_theme_ids'],
                'min_duration': parsed_prefs['min_duration'],
                'max_duration': parsed_prefs['max_duration'],
                'budget': parsed_prefs['budget'],
                'difficulty': parsed_prefs['difficulty'],
                'year': parsed_prefs['year'],
                'month': parsed_prefs['month'],
                'response_time_ms': response_time_ms,
                'total_candidates': total_candidates,
                'primary_count': primary_count,
                'relaxed_count': relaxed_count,
                'final_count': final_count,
                'has_relaxed_results': has_relaxed,
                'has_no_results': has_no_results,
                'top_score': score_stats['top_score'],
                'avg_score': score_stats['avg_score'],
                'min_score': score_stats['min_score'],
                'score_std_dev': score_stats['score_std_dev'],
                'result_trip_ids': result_trip_ids,
                'result_scores': result_scores,
                'algorithm_version': algorithm_version,
            }
            
            # Store in database
            return self._store_log(log_record)
            
        except Exception as e:
            # Never let logging break the recommendation flow
            print(f"[WARNING] Failed to log recommendation request: {e}")
            return False
    
    def _store_log(self, log_record: Dict[str, Any]) -> bool:
        """
        Store log record in database.
        
        This is a placeholder - the actual implementation will use SQLAlchemy
        once the migration is run.
        """
        try:
            session = SessionLocal()
            
            # Check if table exists (graceful degradation)
            from sqlalchemy import inspect
            inspector = inspect(session.bind)
            
            if 'recommendation_requests' not in inspector.get_table_names():
                # Table doesn't exist yet - log to console instead
                print(f"[LOG] Request {log_record['request_id']}: "
                      f"{log_record['final_count']} results, "
                      f"top_score={log_record['top_score']}, "
                      f"time={log_record['response_time_ms']}ms")
                session.close()
                return True
            
            # Insert into recommendation_requests table
            from sqlalchemy import text
            
            insert_sql = text("""
                INSERT INTO recommendation_requests (
                    request_id, session_id, user_id, created_at, preferences,
                    selected_countries, selected_continents, preferred_type_id,
                    preferred_theme_ids, min_duration, max_duration, budget,
                    difficulty, year, month, response_time_ms, total_candidates,
                    primary_count, relaxed_count, final_count, has_relaxed_results,
                    has_no_results, top_score, avg_score, min_score, score_std_dev,
                    result_trip_ids, result_scores, algorithm_version
                ) VALUES (
                    :request_id, :session_id, :user_id, :created_at, :preferences,
                    :selected_countries, :selected_continents, :preferred_type_id,
                    :preferred_theme_ids, :min_duration, :max_duration, :budget,
                    :difficulty, :year, :month, :response_time_ms, :total_candidates,
                    :primary_count, :relaxed_count, :final_count, :has_relaxed_results,
                    :has_no_results, :top_score, :avg_score, :min_score, :score_std_dev,
                    :result_trip_ids, :result_scores, :algorithm_version
                )
            """)
            
            # Convert to JSON strings for PostgreSQL
            import json
            params = log_record.copy()
            params['preferences'] = json.dumps(params['preferences'])
            params['selected_countries'] = params['selected_countries'] or []
            params['selected_continents'] = params['selected_continents'] or []
            params['preferred_theme_ids'] = params['preferred_theme_ids'] or []
            params['result_trip_ids'] = params['result_trip_ids'] or []
            params['result_scores'] = params['result_scores'] or []
            
            session.execute(insert_sql, params)
            session.commit()
            session.close()
            
            return True
            
        except Exception as e:
            print(f"[WARNING] Database logging failed: {e}")
            # Fall back to console logging
            print(f"[LOG] Request {log_record['request_id']}: "
                  f"{log_record['final_count']} results, "
                  f"top_score={log_record['top_score']}, "
                  f"time={log_record['response_time_ms']}ms")
            return False


# Singleton instance for easy access
_logger_instance = None

def get_logger() -> RecommendationLogger:
    """Get the singleton logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = RecommendationLogger()
    return _logger_instance
