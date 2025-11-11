from fastapi import APIRouter

from src.utils.response_builder import ResponseBuilder

entry_router = APIRouter()


@entry_router.get("/health", summary="Health Check")
async def health_check():
    return ResponseBuilder.success(message="Service is healthy")
