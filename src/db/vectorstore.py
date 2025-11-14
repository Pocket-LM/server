from langchain_postgres import PGVector
from langchain_ollama import OllamaEmbeddings
from src.configs import settings
from src.utils.logging import get_logger
from .session import get_async_engine

logger = get_logger(__name__)


def get_vector_store() -> PGVector:
    """Initializes and returns a PGVector store instance."""
    return PGVector(
        embeddings=OllamaEmbeddings(model=settings.OLLAMA_EMBEDDING_MODEL),
        connection=get_async_engine(),
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
