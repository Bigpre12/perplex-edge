class AsyncSession: pass
from db.session import async_session_maker

async def get_sqlmodel_session() -> AsyncSession:
    """
    Dependency that provides an async session for SQLModel.
    Reuses the existing database connection pool.
    """
    async with async_session_maker() as session:
        yield session
