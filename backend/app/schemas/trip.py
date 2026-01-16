"""
Schemas for Trip Models (TripTemplate, TripOccurrence, Trip)
"""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from pydantic import ConfigDict
from app.schemas.base import BaseSchema
from app.schemas.resources import CompanySchema, TripTypeSchema, CountrySchema, TagSchema, GuideSchema


class TripTemplateSchema(BaseSchema):
    """
    Schema for TripTemplate API responses.
    
    All fields use snake_case internally but serialize to camelCase.
    Example: image_url → imageUrl in JSON response
    """
    id: int
    title: str
    title_he: str  # Automatically becomes "titleHe" in JSON
    description: str
    description_he: str  # Automatically becomes "descriptionHe" in JSON
    short_description: Optional[str] = None  # Automatically becomes "shortDescription"
    short_description_he: Optional[str] = None  # Automatically becomes "shortDescriptionHe"
    image_url: Optional[str] = None  # Automatically becomes "imageUrl"
    base_price: Decimal  # Automatically becomes "basePrice"
    single_supplement_price: Optional[Decimal] = None  # Automatically becomes "singleSupplementPrice"
    typical_duration_days: int  # Automatically becomes "typicalDurationDays"
    default_max_capacity: int  # Automatically becomes "defaultMaxCapacity"
    difficulty_level: int  # Automatically becomes "difficultyLevel"
    company_id: int  # Automatically becomes "companyId"
    trip_type_id: Optional[int] = None  # Automatically becomes "tripTypeId"
    primary_country_id: Optional[int] = None  # Automatically becomes "primaryCountryId"
    is_active: bool  # Automatically becomes "isActive"
    properties: Optional[dict] = None  # JSONB - no transformation needed
    created_at: datetime  # Automatically becomes "createdAt"
    updated_at: datetime  # Automatically becomes "updatedAt"
    
    # Relations (optional, included when needed)
    company: Optional[CompanySchema] = None
    trip_type: Optional[TripTypeSchema] = None  # Automatically becomes "tripType"
    primary_country: Optional[CountrySchema] = None  # Automatically becomes "primaryCountry"
    # Note: countries and tags are excluded by default to avoid lazy loading issues
    # They can be included explicitly if needed via model_validate with proper eager loading
    countries: List[CountrySchema] = []
    tags: List[TagSchema] = []
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TripOccurrenceSchema(BaseSchema):
    """Schema for TripOccurrence API responses"""
    id: int
    trip_template_id: int
    guide_id: Optional[int] = None
    start_date: date
    end_date: date
    price_override: Optional[Decimal] = None
    single_supplement_override: Optional[Decimal] = None
    max_capacity_override: Optional[int] = None
    spots_left: int
    status: str
    image_url_override: Optional[str] = None
    notes: Optional[str] = None
    notes_he: Optional[str] = None
    properties: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed fields (from hybrid properties)
    effective_price: Optional[Decimal] = None
    effective_max_capacity: Optional[int] = None
    effective_image_url: Optional[str] = None
    duration_days: Optional[int] = None
    
    # Relations (optional, included when needed)
    template: Optional[TripTemplateSchema] = None
    guide: Optional[GuideSchema] = None
    
    model_config = ConfigDict(from_attributes=True)


