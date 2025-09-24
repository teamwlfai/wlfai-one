from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


# Input Schemas
class RoleCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Role name")
    description: str | None = Field(
        None, max_length=255, description="Role description"
    )
    created_by: int | None = Field(
        None, ge=1, description="Created By must be a valid number"
    )


class RoleUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=50)
    description: str | None = Field(None, max_length=255)
    updated_by: int | None = Field(None, ge=1)
    is_active: bool | None = None


# Output Schema
class RoleOut(BaseModel):
    id: int
    name: str
    description: str | None
    created_by: int | None
    created_at: datetime
    updated_by: int | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
