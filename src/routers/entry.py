from fastapi import APIRouter
from .capture import capture_router
from .collection import collection_router
from .chat import chat_router

entry_router = APIRouter()

entry_router.include_router(capture_router, prefix="/capture", tags=["capture"])
entry_router.include_router(
    collection_router, prefix="/collection", tags=["collection"]
)
entry_router.include_router(chat_router, prefix="/chat", tags=["chat"])
