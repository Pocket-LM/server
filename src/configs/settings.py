from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application configuration
    ENVIRONMENT: str = "development"
    NAME: str = "<your-app-name>"
    VERSION: str = "<your-app-version>"
    API_PREFIX: str = "<your-api-prefix>"

    # LangSmith configuration
    LANGSMITH_TRACING: str = "true"
    LANGSMITH_API_KEY: str = "<your-langsmith-api-key>"
    LANGSMITH_ENDPOINT: str = "<your-langsmith-endpoint>"
    LANGSMITH_PROJECT: str = "<your-langsmith-project>"

    # PostgreSQL/PGVector configuration
    ORM_DATABASE_URL: str = "<your-database-url>"
    PLAIN_DATABASE_URL: str = "<your-plain-database-url>"

    # Ollama configuration
    OLLAMA_BASE_URL: str = "<your-ollama-base-url>"
    OLLAMA_EMBEDDING_MODEL: str = "<your-ollama-embedding-model>"
    OLLAMA_LLM_MODEL: str = "<your-ollama-llm-model>"

    # PGVector tables names
    COLLECTIONS_TABLE: str = "<your-collections-table-name>"
    EMBEDDINGS_TABLE: str = "<your-embeddings-table-name>"

    # PocketLM default settings
    DEFAULT_COLLECTION_NAME: str = "<your-default-collection-name>"
    DEFAULT_USER_ID: str = "<your-default-user-id>"
    DEFAULT_SESSION_ID: str = "<your-default-session-id>"

    # Google GenAI configuration
    GEMINI_API_KEY: str = "<your-google-api-key>"
    GEMINI_EMBEDDING_MODEL: str = "<your-google-embedding-model>"
    GEMINI_LLM_MODEL: str = "<your-google-llm-model>"
    GEMINI_EMBEDDING_DIMS: int = 3072

    # Mem0 configuration
    MEM0_API_KEY: str = "<your-mem0-api-key>"
    MEM0_RERANKER_MODEL: str = "<your-memo-hf-reranker-model>"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
