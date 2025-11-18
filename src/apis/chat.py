from langchain.messages import HumanMessage
from datetime import datetime, timezone
from fastapi import HTTPException

from src.configs.glob_ctx import ctx
from src.configs.settings import settings
from src.schemas.langgraph import AgentState
from src.utils.langgraph.agent import get_langgraph_agent
from src.utils.langgraph.agent import get_checkpoint_saver


async def handle_chat_history():
    async with get_langgraph_agent(
        user_id=settings.DEFAULT_USER_ID,
        thread_id=settings.DEFAULT_SESSION_ID,
    ) as (graph, config):
        async for state in graph.aget_state_history(config=config, limit=1):
            filtered_messages = [
                msg
                for msg in state.values.get("history", [])
                if msg.type == "human"
                or (msg.type == "ai" and len(msg.tool_calls) == 0)
            ]
            return filtered_messages


async def handle_chat_message(collection_name: str, user_query: str):
    ctx.set(collection_name)

    human_msg = HumanMessage(
        content=user_query,
        additional_kwargs={"generated_at": datetime.now(timezone.utc).isoformat()},
    )

    async with get_langgraph_agent(
        user_id=settings.DEFAULT_USER_ID,
        thread_id=settings.DEFAULT_SESSION_ID,
    ) as (graph, config):

        state = await graph.aget_state(config=config)

        try:
            updated_messages_state = (
                await graph.ainvoke(
                    AgentState(
                        messages=[human_msg],
                        summary=state.values.get("summary", ""),
                        history=[human_msg],
                    ),
                    config,
                    stream_mode="values",
                )
            ).get("messages", [])[-1]
            return updated_messages_state
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


async def handle_clear_chat():
    try:
        async with get_checkpoint_saver() as checkpoint_saver:
            await checkpoint_saver.adelete_thread(thread_id=settings.DEFAULT_SESSION_ID)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
