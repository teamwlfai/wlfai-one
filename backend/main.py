from fastapi import FastAPI

from contextlib import asynccontextmanager
from app.api.v1.api_router import api_v1_router
from app.core.database import engine, SessionLocal
from app.core.exceptions import register_exception_handlers, register_openapi_override
from app.models.role import metadata

import logging
from sqlalchemy import text

# ✅ Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_connection():
    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
            logger.info("DB connection successful ✅")
    except Exception as e:
        logger.error("DB connection failed ❌: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application lifespan...")
    await test_connection()

    # Startup: create tables (optional for dev)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
            logger.info("Tables created successfully ✅")
    except Exception as e:
        logger.error("Error creating tables ❌: %s", e)

    yield
    logger.info("Shutting down application...")


# Attach lifespan
app = FastAPI(
    title="WLFAI ONE PROJECT",
    version="1.0.0",
    lifespan=lifespan,
)

# V1 routes
app.include_router(api_v1_router, prefix="/api/v1")

# Register global exception handlers
register_exception_handlers(app)
# Override OpenAPI docs so Swagger shows APIResponse
register_openapi_override(app)
