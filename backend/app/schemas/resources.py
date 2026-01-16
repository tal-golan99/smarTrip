"""
Schemas for Resource Models (Company, Country, Guide, TripType, Tag)
"""

from datetime import datetime
from typing import Optional
from app.schemas.base import BaseSchema
from pydantic import ConfigDict, field_validator


class CompanySchema(BaseSchema):
    """Schema for Company API responses"""
    id: int
    name: str
    name_he: str
    description: Optional[str] = None
    description_he: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CountrySchema(BaseSchema):
    """Schema for Country API responses"""
    id: int
    name: str
    name_he: str
    continent: str  # Will be converted from Enum to string value
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GuideSchema(BaseSchema):
    """Schema for Guide API responses"""
    id: int
    name: str
    name_he: Optional[str] = None
    email: str
    phone: Optional[str] = None
    gender: str
    age: Optional[int] = None
    bio: Optional[str] = None
    bio_he: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TripTypeSchema(BaseSchema):
    """Schema for TripType API responses"""
    id: int
    name: str
    name_he: Optional[str] = None  # Allow None/empty - frontend will fallback to name
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    @field_validator('name_he', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty strings to None so frontend can properly fallback"""
        if v == '':
            return None
        return v
    
    model_config = ConfigDict(from_attributes=True)


class TagSchema(BaseSchema):
    """Schema for Tag API responses"""
    id: int
    name: str
    name_he: Optional[str] = None  # Allow None/empty - frontend will fallback to name
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    @field_validator('name_he', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty strings to None so frontend can properly fallback"""
        if v == '':
            return None
        return v
    
    model_config = ConfigDict(from_attributes=True)
