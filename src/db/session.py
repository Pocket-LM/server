from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import MetaData
from src.configs.settings import settings

async_engine = create_async_engine(str(settings.DATABASE_URL), echo=False)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)


def get_async_engine():
    return async_engine


def get_async_session():
    return async_session
