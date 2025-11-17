from fastapi import APIRouter

from src.routers.capture import capture_router
from src.routers.collection import collection_router
from src.routers.chat import chat_router

entry_router = APIRouter()

entry_router.include_router(capture_router, prefix="/capture", tags=["capture"])
entry_router.include_router(
    collection_router, prefix="/collection", tags=["collection"]
)
entry_router.include_router(chat_router, prefix="/chat", tags=["chat"])
