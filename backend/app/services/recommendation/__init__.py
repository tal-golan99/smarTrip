"""
Recommendation Service Package

Business logic for trip recommendations and scoring algorithm.
"""

from .engine import get_recommendations

__all__ = ['get_recommendations']
