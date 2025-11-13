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
    DATABASE_URL: str = "<your-database-url>"

    # Ollama configuration
    OLLAMA_EMBEDDING_MODEL: str = "<your-ollama-embedding-model>"
    OLLAMA_LLM_MODEL: str = "<your-ollama-llm-model>"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
