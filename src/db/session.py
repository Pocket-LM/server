from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.configs.settings import settings

async_engine = create_async_engine(str(settings.DATABASE_URL), echo=False)
AsyncSession = async_sessionmaker(async_engine, expire_on_commit=False)


def get_async_engine():
    """Provides the SQLAlchemy asynchronous engine instance."""
    return async_engine


def get_async_session():
    """Creates and returns a new asynchronous database session."""
    return AsyncSession()
