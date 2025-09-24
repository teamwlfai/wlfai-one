"""
Base schemas and common patterns for Pydantic v2 models
"""

from datetime import datetime
from typing import Any, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.types import PositiveInt, NonNegativeInt


class BaseSchema(BaseModel):
    """Base schema with common configuration"""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)},
    )


class TimestampMixin(BaseSchema):
    """Mixin for entities with timestamps"""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UUIDMixin(BaseSchema):
    """Mixin for entities with UUID primary key"""

    id: UUID = Field(..., description="Unique identifier")


class PaginatedResponse(BaseSchema):
    """Generic paginated response wrapper"""

    items: List[Any]
    total: NonNegativeInt
    page: PositiveInt
    per_page: PositiveInt
    pages: NonNegativeInt
    has_next: bool
    has_prev: bool
