from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    pass


def _build_engine():
    db_url = settings.DATABASE_URL
    # SQLite special kwargs
    if db_url.startswith("sqlite"):
        return create_async_engine(
            db_url,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False},
        )
    # PostgreSQL / Supabase - convert schema to use asyncpg
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

    return create_async_engine(db_url, echo=settings.DEBUG, pool_pre_ping=True)


engine = _build_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    """Create all tables on startup (SQLite fallback; Supabase uses schema.sql)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:  # type: ignore[override]
    """FastAPI dependency that provides a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
