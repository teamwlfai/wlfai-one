## PostgreSQL connection [SQLAlchemy]
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# ENV
load_dotenv()


DATABASE_URL = os.getenv(
    "PG_DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/wlfai"
)

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=AsyncSession
)


Base = declarative_base()


# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session
