from typing import Annotated
from fastapi import APIRouter, Form

from src.apis.capture import handle_knowledge_capture
from src.schemas.capture import KnowledgeCaptureRequest
from src.utils.response_builder import ResponseBuilder

capture_router = APIRouter()


@capture_router.post("")
async def capture_knowledge(
    body: Annotated[KnowledgeCaptureRequest, Form(...)],
):
    """
    API endpoint to capture knowledge from a URL, text, or PDF.
    """
    try:
        await handle_knowledge_capture(
            type=body.type,
            knowledge_base=body.knowledge_base,
            url=body.url,
            selection=body.selection,
            pdf=body.pdf,
        )
        return ResponseBuilder.success(
            message=f"Content from {body.type} captured successfully for knowledge base: {body.knowledge_base}.",
            data=None,
        )
    except Exception as e:
        raise e
