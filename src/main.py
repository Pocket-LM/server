from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.configs import settings
from src.routers import entry_router
from src.utils.logging import get_logger

# Initialize the logger
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manages application startup and shutdown events."""
    logger.info("PocketLM Server is starting up...")
    yield
    logger.info("PocketLM Server is shutting down...")


def create_application() -> FastAPI:
    """Sets up and returns the main FastAPI application instance."""
    application = FastAPI(
        title=settings.NAME, version=settings.VERSION, lifespan=lifespan
    )

    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "authorization"],
    )

    # Routers
    application.include_router(entry_router, prefix=settings.API_PREFIX, tags=["APIs"])

    return application


app = create_application()


# Health check endpoint
@app.get("/health", summary="Health Check")
async def health_check():
    """Provides a simple health check endpoint."""
    return {
        "success": True,
        "status": "success",
        "message": "Service is running",
        "data": None,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
