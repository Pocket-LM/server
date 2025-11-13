from fastapi import APIRouter
from .capture import capture_router

entry_router = APIRouter()

entry_router.include_router(capture_router, prefix="/capture", tags=["capture"])
