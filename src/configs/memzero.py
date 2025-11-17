from mem0 import AsyncMemory
from mem0.configs.base import (
    MemoryConfig,
    VectorStoreConfig,
    LlmConfig,
    EmbedderConfig,
    RerankerConfig,
)
from contextlib import asynccontextmanager

from src.configs.settings import settings


config = MemoryConfig(
    vector_store=VectorStoreConfig(
        provider="pgvector",
        config={
            "connection_string": settings.PLAIN_DATABASE_URL,
            "embedding_model_dims": settings.GEMINI_EMBEDDING_DIMS,
        },
    ),
    llm=LlmConfig(
        provider="gemini",
        config={
            "model": settings.GEMINI_LLM_MODEL,
            "temperature": 0.1,
        },
    ),
    embedder=EmbedderConfig(
        provider="gemini",
        config={
            "model": settings.GEMINI_EMBEDDING_MODEL,
            "api_key": settings.GEMINI_API_KEY,
            "embedding_dims": settings.GEMINI_EMBEDDING_DIMS,
        },
    ),
    # reranker=RerankerConfig(
    #     provider="huggingface",
    #     config={
    #         "model": settings.MEM0_RERANKER_MODEL,
    #         "device": "cpu",
    #     },
    # ),
)


@asynccontextmanager
async def get_memory():
    memory = AsyncMemory(config=config)
    try:
        memory.collection_name = "default"
        yield memory
    finally:
        pass
