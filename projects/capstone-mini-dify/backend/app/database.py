"""
Mini-Dify - 异步数据库引擎 (PostgreSQL + asyncpg)
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """FastAPI 依赖：获取数据库会话"""
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
