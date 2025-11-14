from crawl4ai import AsyncWebCrawler
from sqlalchemy import select, text
from src.db.session import get_async_session
from src.db.vectorstore import get_vector_store
from src.utils.logging import get_logger
from src.configs.settings import settings

logger = get_logger(__name__)


async def temp():
    vector_store = get_vector_store()
    async with get_async_session() as session:
        statement = f"SELECT name FROM {settings.COLLECTIONS_TABLE}"
        collections = (
            (await session.execute(text(statement), {"name": "default"}))
            .scalars()
            .all()
        )
        logger.info(collections)


if __name__ == "__main__":
    import asyncio

    asyncio.run(temp())
