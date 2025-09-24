# app/schemas/response.py
from pydantic import BaseModel
from typing import Any, List, Dict


class ValidationErrorItem(BaseModel):
    loc: List[str]
    msg: str
    type: str
    ctx: Dict[str, Any] | None = None


class ValidationErrorData(BaseModel):
    errors: List[ValidationErrorItem]
    body: Any  # the invalid payload


class APIResponse(BaseModel):
    code: int
    message: str
    data: Any | None = None


class ValidationErrorResponse(APIResponse):
    data: ValidationErrorData
