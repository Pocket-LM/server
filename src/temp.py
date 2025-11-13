from crawl4ai import AsyncWebCrawler
from sqlalchemy import select
from src.db.session import get_async_session
from src.db.vectorstore import get_vector_store
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def temp():
    vector_store = get_vector_store()
    async with get_async_session() as session:
        collection_store = await vector_store.aget_collection(session)
        name = await collection_store.aget_by_name(session, "default")
        logger.info(f"Collection fetched: {name}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(temp())
