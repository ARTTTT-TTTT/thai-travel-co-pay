# session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from typing import AsyncGenerator
from app.configs.app_config import app_config

DATABASE_URL = str(app_config.SQLALCHEMY_DATABASE_URI)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
