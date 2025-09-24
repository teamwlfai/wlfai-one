from functools import wraps
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.schemas.response import APIResponse


# Standard response function
def wrap_response(data=None, message="Success", code=200):
    return JSONResponse(
        status_code=code,
        content=jsonable_encoder({"code": code, "message": message, "data": data}),
    )


# Decorator for per-route messages (success only)
def standard_response(message: str = "Success"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            return APIResponse(code=200, message=message, data=result)

        # 👇 Hack: update FastAPI/OpenAPI docs
        wrapper.__annotations__["return"] = APIResponse
        wrapper.response_model = APIResponse
        return wrapper

    return decorator
