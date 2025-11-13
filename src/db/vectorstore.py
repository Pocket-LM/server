from langchain_postgres import PGVector
from langchain_ollama import OllamaEmbeddings
from src.configs import settings
from .session import get_async_engine


def get_vector_store() -> PGVector:
    return PGVector(
        embeddings=OllamaEmbeddings(model=settings.OLLAMA_EMBEDDING_MODEL),
        connection=get_async_engine(),
        collection_name="default",
    )
