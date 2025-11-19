from fastapi import APIRouter, Body

# from fastapi.responses import StreamingResponse
<<<<<<< HEAD
from typing import Annotated
=======
from typing import Annotated, Literal
>>>>>>> eed57bbd488c87162e1ca2c5588b39a9ca109dce

from src.schemas.custom_base_model import CamelCaseBaseModel
from src.utils.response_builder import ResponseBuilder
from src.apis.chat import *

chat_router = APIRouter()


class ChatMessageRequest(CamelCaseBaseModel):
    user_query: str
    collection_name: str


<<<<<<< HEAD
@chat_router.get("/history")
async def chat_history():
    try:
        history = await handle_chat_history()
        return ResponseBuilder.success(
            status_code=200,
            message="Chat history retrieved successfully",
            data=history,
=======
class ChatMessageResponse(CamelCaseBaseModel):
    message_content: str


class ChatHistoryResponse(ChatMessageResponse):
    type: Literal["human", "ai"]
    knowledge_base: str | None = None


@chat_router.get("/history")
async def chat_history():
    """
    Retrieves the chat history for the current session.

    Returns:
        ResponseBuilder.success: A success response containing the chat history.
    """
    try:
        history = await handle_chat_history()
        res_data = [
            ChatHistoryResponse(
                message_content=msg.content,
                type=msg.type,
                knowledge_base=(
                    msg.additional_kwargs.get("collection_name")
                    if msg.additional_kwargs
                    else None
                ),
            ).model_dump(by_alias=True)
            for msg in (history if history else [])
        ]

        return ResponseBuilder.success(
            status_code=200,
            message="Chat history retrieved successfully",
            data=res_data,
>>>>>>> eed57bbd488c87162e1ca2c5588b39a9ca109dce
        )
    except Exception as e:
        raise e


@chat_router.post("/message")
async def chat_message(
    body: Annotated[ChatMessageRequest, Body(...)],
):
<<<<<<< HEAD
    try:
        ai_msg = await handle_chat_message(body.collection_name, body.user_query)
        return ResponseBuilder.success(
            status_code=200,
            message="Message processed successfully",
            data=ai_msg,
=======
    """
    Processes a user's chat message and returns the AI's response.

    Args:
        body (ChatMessageRequest): The request body containing the user's query and collection name.

    Returns:
        ResponseBuilder.success: A success response containing the AI's message.
    """
    try:
        ai_msg = await handle_chat_message(body.collection_name, body.user_query)
        res_data = ChatMessageResponse(message_content=ai_msg.content).model_dump(
            by_alias=True
        )
        return ResponseBuilder.success(
            status_code=200,
            message="Message processed successfully",
            data=res_data,
>>>>>>> eed57bbd488c87162e1ca2c5588b39a9ca109dce
        )
    except Exception as e:
        raise e


@chat_router.delete("/clear")
async def clear_chat():
<<<<<<< HEAD
=======
    """
    Clears the chat history for the current session.

    Returns:
        ResponseBuilder.success: A success response indicating the chat history has been cleared.
    """
>>>>>>> eed57bbd488c87162e1ca2c5588b39a9ca109dce
    try:
        await handle_clear_chat()
        return ResponseBuilder.success(
            status_code=200,
            message="Chat history cleared successfully",
            data=None,
        )
    except Exception as e:
        raise e
