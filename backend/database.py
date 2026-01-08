from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

DATABASE_URL = "sqlite+aiosqlite:///./app.db?check_same_thread=false"

engine = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None

Base = declarative_base()

async def init_db():
    global engine, SessionLocal

    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
    )

    SessionLocal = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

async def close_db():
    if engine:
        await engine.dispose()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")

    async with SessionLocal() as session:
        yield session
