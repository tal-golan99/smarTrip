"""
Helper Utilities for Schema Serialization
"""

from flask import jsonify
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


def serialize_response(data, schema_class: Type[T], status_code: int = 200, include_count: bool = False):
    """
    Helper to serialize SQLAlchemy model(s) to Pydantic schema(s).
    
    Args:
        data: SQLAlchemy model instance or list of instances
        schema_class: Pydantic schema class to serialize to
        status_code: HTTP status code (default: 200)
        include_count: Whether to include count in response (for lists)
    
    Returns:
        Flask JSON response with serialized data
    
    Usage:
        template = db.session.get(TripTemplate, id)
        return serialize_response(template, TripTemplateSchema)
        
        templates = db.session.query(TripTemplate).all()
        return serialize_response(templates, TripTemplateSchema, include_count=True)
    """
    if isinstance(data, list):
        schemas = [schema_class.model_validate(item) for item in data]
        result = [schema.model_dump(by_alias=True) for schema in schemas]
        response_data = {'data': result}
        if include_count:
            response_data['count'] = len(result)
    else:
        schema = schema_class.model_validate(data)
        result = schema.model_dump(by_alias=True)
        response_data = {'data': result}
    
    return jsonify({
        'success': True,
        **response_data
    }), status_code
