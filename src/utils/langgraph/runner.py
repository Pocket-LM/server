import asyncio
from datetime import datetime, timezone
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.configs.settings import settings
from src.utils.langgraph.agent import get_langgraph_agent


async def run_agent_message(graph, config: RunnableConfig, query: str) -> None:
    """
    Send a message to the agent and stream the response.

    Args:
        graph: Compiled LangGraph agent
        config: Runnable configuration with user/thread IDs
        query: User's question or message
    """
    human = HumanMessage(
        content=query,
        additional_kwargs={"generated_at": datetime.now(timezone.utc).isoformat()},
    )

    async for message_chunk, metadata in graph.astream(
        {"messages": [human], "history": [human]},
        config,
        stream_mode="messages",
    ):
        if message_chunk.content:
            content = (
                message_chunk.text
                if hasattr(message_chunk, "text")
                else message_chunk.content
            )
            print(content, end="|", flush=True)


async def main():
    """Main entry point for testing the agent."""
    async with get_langgraph_agent(
        user_id=settings.DEFAULT_USER_ID,
        thread_id=settings.DEFAULT_SESSION_ID,
    ) as (graph, config):

        test_queries = [
            "Hi, my name is Julian.",
            "I am currently studying computer science at King Mongkut's University of Technology Thonburi and a third-year student.",
            "What's my name and where do I study?",
            "Tell me about machine learning algorithms.",
        ]

        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print("=" * 60)
            await run_agent_message(graph, config, query)
            print()  # New line after response


if __name__ == "__main__":
    asyncio.run(main())
