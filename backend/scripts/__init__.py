"""
Background Job Scripts Module
=============================

This module contains background job functions for the SmartTrip application:

- aggregate_trip_interactions: Compute CTR and engagement metrics
- cleanup_sessions: Close stale user sessions
- aggregate_daily_metrics: Aggregate recommendation metrics daily
"""

from .aggregate_trip_interactions import aggregate_trip_interactions
from .cleanup_sessions import cleanup_sessions
from .aggregate_daily_metrics import aggregate_daily_metrics

__all__ = [
    'aggregate_trip_interactions',
    'cleanup_sessions',
    'aggregate_daily_metrics',
]
