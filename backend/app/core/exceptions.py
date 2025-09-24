from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from utils.response_wrapper import wrap_response
from app.schemas.response import APIResponse  # your wrapper schema
import logging
import json

logger = logging.getLogger(__name__)


# Map Pydantic error types to friendly messages
ERROR_MESSAGES = {
    "missing": "is required",
    "string_type": "should be a valid string",
    "int_parsing": "should be a valid integer, unable to parse string as an integer",
    "string_too_short": "should have at least {min_length} characters",
    "string_too_long": "should have at most {max_length} characters",
    "bool_parsing": "should be true or false",
    "value_error": "invalid value",
    "type_error": "invalid type",
    # Legacy error types (for older Pydantic versions)
    "value_error.missing": "is required",
    "type_error.integer": "should be a valid integer",
    "type_error.string": "should be a valid string",
    "value_error.any_str.min_length": "should have at least {limit_value} characters",
    "value_error.any_str.max_length": "should have at most {limit_value} characters",
    "type_error.bool": "should be true or false",
}


def get_friendly_error_message(errors):
    """Convert Pydantic validation errors to user-friendly messages"""
    messages = []

    for err in errors:
        # Get field name - handle nested fields
        field_path = err["loc"]
        if len(field_path) > 1 and field_path[0] == "body":
            field = field_path[-1]  # Get the actual field name
        else:
            field = field_path[-1] if field_path else "field"

        err_type = err["type"]
        ctx = err.get("ctx", {})

        # Try to get friendly message
        template = ERROR_MESSAGES.get(err_type)

        # If no exact match, try partial matches
        if not template:
            for key, msg in ERROR_MESSAGES.items():
                if key in err_type:
                    template = msg
                    break

        # Fallback to original message
        if not template:
            template = err.get("msg", "validation error")

        # Format template with context
        try:
            if isinstance(template, str) and "{" in template:
                # Handle both ctx keys and direct error keys
                format_dict = {**ctx}
                if "limit_value" not in format_dict and "min_length" in ctx:
                    format_dict["limit_value"] = ctx["min_length"]
                if "limit_value" not in format_dict and "max_length" in ctx:
                    format_dict["limit_value"] = ctx["max_length"]

                formatted_message = template.format(**format_dict)
            else:
                formatted_message = template
        except (KeyError, ValueError):
            formatted_message = template

        messages.append(f"{field} {formatted_message}")

    return ", ".join(messages)


def register_exception_handlers(app: FastAPI):
    """
    Registers global exception handlers that wrap all errors in APIResponse.
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return wrap_response(
            data=None,
            message=exc.detail if exc.detail else "HTTP error occurred",
            code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        # Friendly messages: "field_name: error message"
        friendly_message = get_friendly_error_message(exc.errors())
        return wrap_response(
            data=None,  # keep data empty
            message=friendly_message,
            code=status.HTTP_400_BAD_REQUEST,  # 400 Bad Request
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return wrap_response(
            data=None,
            message="Internal server error: " + str(exc),
            code=500,
        )


def register_openapi_override(app: FastAPI):
    """
    Ensures Swagger always shows APIResponse instead of raw FastAPI/Starlette errors.
    """

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = app.openapi()
    # Inject our APIResponse schema globally
    openapi_schema["components"]["schemas"][
        "APIResponse"
    ] = APIResponse.model_json_schema()

    for path, methods in openapi_schema.get("paths", {}).items():
        for method, endpoint in methods.items():
            responses = endpoint.get("responses", {})
            for status_code, response in responses.items():
                response["content"] = {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/APIResponse"}
                    }
                }

    app.openapi_schema = openapi_schema
    app.openapi = lambda: openapi_schema
    return openapi_schema
