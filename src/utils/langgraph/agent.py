from contextlib import asynccontextmanager

from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.runnables import RunnableConfig

from src.configs.settings import settings
from src.schemas.langgraph import AgentState
from src.utils.langgraph.tools import retrieve_docs, retrieve_memory
from src.utils.langgraph.nodes import (
    manage_context,
    respond_or_retrieve,
    generate_using_context,
    save_to_memory,
)


@asynccontextmanager
async def get_checkpoint_saver():
    """Context manager for PostgreSQL checkpoint saver."""
    async with AsyncPostgresSaver.from_conn_string(
        settings.PLAIN_DATABASE_URL
    ) as checkpoint_saver:
        yield checkpoint_saver


@asynccontextmanager
async def get_langgraph_agent(user_id: str, thread_id: str):
    """
    Create and configure the LangGraph agent with all nodes and edges.

    Args:
        user_id: Unique identifier for the user
        thread_id: Unique identifier for the conversation thread

    Yields:
        Tuple of (compiled_graph, runnable_config)
    """
    async with get_checkpoint_saver() as checkpoint_saver:
        await checkpoint_saver.setup()

        # Build the state graph
        builder = StateGraph(AgentState)

        # Add nodes
        builder.add_node("manage_context", manage_context)
        builder.add_node("respond_or_retrieve", respond_or_retrieve)
        builder.add_node("tools", ToolNode(tools=[retrieve_docs, retrieve_memory]))
        builder.add_node("generate_using_context", generate_using_context)
        builder.add_node("save_to_memory", save_to_memory)

        # Define edges
        builder.set_entry_point("manage_context")
        builder.add_edge("manage_context", "respond_or_retrieve")
        builder.add_conditional_edges(
            "respond_or_retrieve",
            tools_condition,
            {"__end__": "save_to_memory", "tools": "tools"},
        )
        builder.add_edge("tools", "generate_using_context")
        builder.add_edge("generate_using_context", "save_to_memory")
        builder.set_finish_point("save_to_memory")

        graph = builder.compile(checkpointer=checkpoint_saver)

        config = RunnableConfig(
            configurable={
                "user_id": user_id,
                "thread_id": thread_id,
            }
        )

        yield graph, config
