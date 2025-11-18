from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr

from src.configs import settings
from src.utils.logging import get_logger
from src.db.session import get_async_engine
from src.configs.glob_ctx import ctx

logger = get_logger(__name__)


def get_vector_store() -> PGVector:
    return PGVector(
        embeddings=GoogleGenerativeAIEmbeddings(
            google_api_key=SecretStr(settings.GEMINI_API_KEY),
            model=settings.GEMINI_EMBEDDING_MODEL,
        ),
        connection=get_async_engine(),
        collection_name=ctx.get(),
    )


async def ensure_vector_store_initialized():
    """Ensures that the vector store is initialized."""
    vector_store = get_vector_store()
    await vector_store.acreate_collection()

    """    
    TODO: Fix this function to properly create tables if not exists. Currently, tables are not being created as expected.

    async with get_async_session() as session:
        vector_store = get_vector_store()
        await vector_store.acreate_tables_if_not_exists()

        await session.commit()
        await session.aclose()
    """
