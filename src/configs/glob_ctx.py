from contextvars import ContextVar

from src.configs.settings import settings

ctx = ContextVar("collection_name", default=settings.DEFAULT_COLLECTION_NAME)
