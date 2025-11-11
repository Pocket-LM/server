from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application configuration
    ENVIRONMENT: str = "development"
    NAME: str = "<your-app-name>"
    VERSION: str = "<your-app-version>"
    API_PREFIX: str = "<your-api-prefix>"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
