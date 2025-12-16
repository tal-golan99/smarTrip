"""
SmartTrip Recommender Module
============================

This module contains the recommendation engine components:
- logging: Request/response logging for analysis
- metrics: Metrics computation and aggregation
- evaluation: Scenario evaluation and baseline comparison
"""

from .logging import RecommendationLogger
from .metrics import MetricsAggregator
from .evaluation import ScenarioEvaluator

__all__ = [
    'RecommendationLogger',
    'MetricsAggregator', 
    'ScenarioEvaluator',
]
