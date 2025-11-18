import asyncio

from src.configs.settings import settings
from src.utils.langgraph.agent import get_langgraph_agent, get_checkpoint_saver


async def main():
    # async with get_checkpoint_saver() as saver:
    #     await saver.adelete_thread(thread_id=settings.DEFAULT_SESSION_ID)

    async with get_langgraph_agent(
        user_id=settings.DEFAULT_USER_ID, thread_id=settings.DEFAULT_SESSION_ID
    ) as (graph, config):
        async for state in graph.aget_state_history(config=config, limit=1):
            print(state)


if __name__ == "__main__":
    asyncio.run(main())
