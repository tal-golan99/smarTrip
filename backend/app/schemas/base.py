"""
Base Schema with Automatic camelCase Alias Generation

All API schemas should inherit from BaseSchema to get automatic
case conversion from snake_case (database) to camelCase (API).
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    """
    Base schema class with automatic camelCase alias generation.
    
    All API schemas should inherit from this class.
    - Internal field names: snake_case (matches database)
    - External API names: camelCase (matches frontend)
    
    Example:
        class MySchema(BaseSchema):
            image_url: str  # Automatically becomes "imageUrl" in JSON
        
        schema = MySchema(image_url="test.jpg")
        schema.model_dump()  # Returns {"imageUrl": "test.jpg"}
    """
    model_config = ConfigDict(
        # Automatically generate camelCase aliases from snake_case field names
        alias_generator=to_camel,
        # Serialize to camelCase when converting to dict/JSON
        serialization_alias_generator=to_camel,
        # Allow reading from both alias (camelCase) and original name (snake_case)
        # This is needed when using from_attributes=True with alias_generator
        populate_by_name=True,
        # Use enum values instead of enum names
        use_enum_values=True,
        # Validate assignment after model creation
        validate_assignment=True,
    )
