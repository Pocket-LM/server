from fastapi import APIRouter, Body

# from fastapi.responses import StreamingResponse
from typing import Annotated

from src.schemas.custom_base_model import CamelCaseBaseModel
from src.utils.response_builder import ResponseBuilder
from src.apis.chat import *

chat_router = APIRouter()


class ChatMessageRequest(CamelCaseBaseModel):
    user_query: str
    collection_name: str


@chat_router.get("/history")
async def chat_history():
    try:
        history = await handle_chat_history()
        return ResponseBuilder.success(
            status_code=200,
            message="Chat history retrieved successfully",
            data=history,
        )
    except Exception as e:
        raise e


@chat_router.post("/message")
async def chat_message(
    body: Annotated[ChatMessageRequest, Body(...)],
):
    try:
        ai_msg = await handle_chat_message(body.collection_name, body.user_query)
        return ResponseBuilder.success(
            status_code=200,
            message="Message processed successfully",
            data=ai_msg,
        )
    except Exception as e:
        raise e


@chat_router.delete("/clear")
async def clear_chat():
    try:
        await handle_clear_chat()
        return ResponseBuilder.success(
            status_code=200,
            message="Chat history cleared successfully",
            data=None,
        )
    except Exception as e:
        raise e
