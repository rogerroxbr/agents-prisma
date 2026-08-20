"""Async PostgreSQL session factory for LangGraph."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class AsyncSessionFactory:
    """Async session factory with context manager support."""

    def __init__(self, database_url: str = None):
        if not database_url:
            from src.db.models import get_database_url

            database_url = get_database_url()

        self.engine = create_async_engine(database_url, echo=False, pool_pre_ping=True)
        self.SessionLocal = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    async def get_session(self) -> AsyncSession:
        """Get async session with context manager."""
        async with self.SessionLocal() as session:
            try:
                yield session
            finally:
                pass

    async def create_session(self) -> AsyncSession:
        """Create and return a new async session."""
        return await self.SessionLocal()


# Singleton instance
session_factory = None


def get_async_session():
    """Get singleton session factory."""
    global session_factory
    if session_factory is None:
        from src.db.models import get_database_url

        session_factory = AsyncSessionFactory(get_database_url())
    return session_factory


__all__ = ["AsyncSessionFactory", "get_async_session"]
