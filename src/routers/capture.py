from typing import Annotated
from fastapi import APIRouter, Form
from src.apis.capture import handle_knowledge_capture
from src.schemas.capture import KnowledgeCaptureRequest

capture_router = APIRouter()


@capture_router.post("")
async def capture_knowledge(
    body: Annotated[KnowledgeCaptureRequest, Form(...)],
):
    """
    Capture knowledge from a URL, a text selection, or a PDF file.
    """
    try:
        result = await handle_knowledge_capture(
            type=body.type,
            knowledge_base=body.knowledge_base,
            url=body.url,
            selection=body.selection,
            pdf=body.pdf,
        )
        return result
    except Exception as e:
        raise e
