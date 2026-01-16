"""
Pydantic Schemas for API Serialization

This package contains Pydantic schemas that handle:
- Automatic case conversion (snake_case ↔ camelCase)
- Request validation
- Response serialization
"""

from app.schemas.base import BaseSchema
from app.schemas.utils import serialize_response
from app.schemas.trip import TripTemplateSchema, TripOccurrenceSchema
from app.schemas.resources import CompanySchema, CountrySchema, TripTypeSchema, TagSchema, GuideSchema

__all__ = [
    'BaseSchema',
    'serialize_response',
    'TripTemplateSchema',
    'TripOccurrenceSchema',
    'CompanySchema',
    'CountrySchema',
    'TripTypeSchema',
    'TagSchema',
    'GuideSchema',
]
