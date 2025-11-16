from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr
from src.configs import settings
from src.utils.logging import get_logger
from .session import get_async_engine

logger = get_logger(__name__)


def get_vector_store() -> PGVector:
    return PGVector(
        embeddings=GoogleGenerativeAIEmbeddings(
            google_api_key=SecretStr(settings.GEMINI_API_KEY),
            model=settings.GEMINI_EMBEDDING_MODEL,
        ),
        connection=get_async_engine(),
        embedding_length=1536,
        collection_name="default",
        collection_metadata={
            "about": "Default collection provided by PocketLM",
        },
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
