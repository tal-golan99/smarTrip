"""
Query Building and Filtering Functions
"""

from datetime import date
from sqlalchemy import or_, extract
from sqlalchemy.orm import joinedload, selectinload
from typing import Dict, List, Optional, Any

from app.core.database import db_session
from app.models.trip import (
    TripOccurrence, TripTemplate, TripTemplateTag, TripTemplateCountry, Country
)
from .constants import RecommendationConfig


def build_base_query():
    """
    Build base SQLAlchemy query with optimized eager loading.
    
    Uses joinedload for many-to-one relationships and selectinload
    for one-to-many to avoid cartesian products.
    """
    return db_session.query(TripOccurrence).options(
        joinedload(TripOccurrence.template).joinedload(TripTemplate.company),
        joinedload(TripOccurrence.template).joinedload(TripTemplate.trip_type),
        joinedload(TripOccurrence.template).joinedload(TripTemplate.primary_country),
        joinedload(TripOccurrence.template).selectinload(TripTemplate.template_tags).joinedload(TripTemplateTag.tag),
        joinedload(TripOccurrence.template).selectinload(TripTemplate.template_countries).joinedload(TripTemplateCountry.country),
        joinedload(TripOccurrence.guide),
    ).join(TripTemplate).filter(TripTemplate.is_active == True)


def apply_geographic_filters(
    query,
    selected_countries: List[int],
    selected_continents_enum: List[str]
):
    """Apply geographic filters (countries and continents)."""
    if not selected_countries and not selected_continents_enum:
        return query
    
    geo_filters = []
    
    if selected_countries:
        geo_filters.append(TripTemplate.primary_country_id.in_(selected_countries))
    
    if selected_continents_enum:
        query = query.join(Country, TripTemplate.primary_country_id == Country.id)
        geo_filters.append(Country.continent.in_(selected_continents_enum))
    
    if len(geo_filters) > 1:
        query = query.filter(or_(*geo_filters))
    elif geo_filters:
        query = query.filter(geo_filters[0])
    
    return query


def apply_date_filters(
    query,
    today: date,
    is_private_groups: bool,
    selected_year: Optional[str],
    selected_month: Optional[str],
    user_start_date: Optional[date],
    config: type
):
    """Apply date filters (year, month, start_date)."""
    if is_private_groups:
        return query
    
    query = query.filter(TripOccurrence.start_date >= today)
    
    # Limit to current year + next N years only (default: current + next year)
    current_year = today.year
    max_year = current_year + config.MAX_YEARS_AHEAD
    query = query.filter(extract('year', TripOccurrence.start_date) <= max_year)
    print(f"[Recommendation] Applied year filter: <= {max_year} (current year + {config.MAX_YEARS_AHEAD})", flush=True)
    
    if selected_year and selected_year != 'all':
        query = query.filter(extract('year', TripOccurrence.start_date) == int(selected_year))
        if selected_month and selected_month != 'all':
            query = query.filter(extract('month', TripOccurrence.start_date) == int(selected_month))
    
    # Legacy: If user specified a start date preference (old format)
    if user_start_date and user_start_date > today and not selected_year:
        query = query.filter(TripOccurrence.start_date >= user_start_date)
        print(f"[Recommendation] Applied user start date filter: >= {user_start_date}", flush=True)
    
    return query


def apply_status_filters(query, is_private_groups: bool):
    """Apply status filters (exclude Cancelled and Full trips)."""
    query = query.filter(TripOccurrence.status.notin_(['Cancelled', 'Full']))
    
    if not is_private_groups:
        query = query.filter(TripOccurrence.spots_left > 0)
    
    return query


def apply_difficulty_filter(query, difficulty: Optional[int], tolerance: int):
    """Apply difficulty filter with tolerance."""
    if difficulty is not None:
        query = query.filter(
            TripTemplate.difficulty_level.between(difficulty - tolerance, difficulty + tolerance)
        )
    return query


def apply_budget_filter(query, budget: Optional[float], multiplier: float):
    """Apply budget filter with multiplier."""
    if budget:
        max_price = budget * multiplier
        query = query.filter(TripOccurrence.effective_price <= max_price)
    return query


def build_primary_query(
    preferences: Dict[str, Any],
    context: Dict[str, Any],
    config: type
):
    """
    Build the primary filtered query based on preferences.
    
    Applies all filters in sequence:
    - Geographic filters (countries, continents)
    - Trip type filter
    - Date filters (year, month, start_date)
    - Status filters (exclude Cancelled, Full)
    - Difficulty filter
    - Budget filter
    
    Args:
        preferences: Normalized preferences dict
        context: Search context dict (from determine_search_context)
        config: RecommendationConfig class
    
    Returns:
        SQLAlchemy query object ready for execution
    """
    today = context['today']
    is_private_groups = context['is_private_groups']
    selected_countries = preferences['selected_countries']
    selected_continents_enum = preferences['selected_continents_enum']
    preferred_type_id = preferences['preferred_type_id']
    selected_year = preferences['year']
    selected_month = preferences['month']
    user_start_date = preferences['user_start_date']
    difficulty = preferences['difficulty']
    budget = preferences['budget']
    
    # Build base query
    query = build_base_query()
    
    # Apply filters
    query = apply_geographic_filters(query, selected_countries, selected_continents_enum)
    
    if preferred_type_id:
        query = query.filter(TripTemplate.trip_type_id == preferred_type_id)
    
    query = apply_date_filters(query, today, is_private_groups, selected_year, selected_month, user_start_date, config)
    query = apply_status_filters(query, is_private_groups)
    query = apply_difficulty_filter(query, difficulty, config.DIFFICULTY_TOLERANCE)
    query = apply_budget_filter(query, budget, config.BUDGET_MAX_MULTIPLIER)
    
    # Order by start_date
    query = query.order_by(TripOccurrence.start_date.asc())
    
    return query


def get_total_trips_count(today: date) -> int:
    """
    Get total count of available trips in database.
    
    Counts all active trips that are:
    - Not cancelled
    - Not full
    - Have spots available
    - Start date >= today
    
    Args:
        today: Current date for filtering
    
    Returns:
        Integer count of available trips
    """
    return db_session.query(TripOccurrence).join(TripTemplate).filter(
        TripTemplate.is_active == True,
        TripOccurrence.status.notin_(['Cancelled', 'Full']),
        TripOccurrence.spots_left > 0,
        TripOccurrence.start_date >= today
    ).count()
