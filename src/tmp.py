import asyncio
from langchain_ollama import ChatOllama
from typing import TypedDict, Annotated, List
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    AnyMessage,
    ToolCall,
    ToolMessage,
    trim_messages,
)
from langchain_core.runnables import RunnableConfig
from src.configs.settings import settings
from datetime import datetime, timezone


class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    summary: Annotated[str, "A brief summary of the conversation so far."]
    history: Annotated[List[AnyMessage], add_messages]


llm = ChatOllama(
    model=settings.OLLAMA_LLM_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    validate_model_on_init=True,
    # reasoning=True,
    temperature=0.1,
)

test_queries = [
    "hi! I'm bob",
    "what's my name?",
]


async def get_checkpointer():
    async with AsyncPostgresSaver.from_conn_string(
        settings.PLAIN_DATABASE_URL
    ) as checkpointer:
        yield checkpointer


async def main():
    async for checkpointer in get_checkpointer():
        await checkpointer.setup()
        await checkpointer.adelete_thread(
            thread_id=settings.DEFAULT_SESSION_ID,
        )

        async def call_model(state: MessagesState):
            response = await llm.ainvoke(state["messages"])
            return {"messages": response}

        builder = StateGraph(state_schema=MessagesState)
        builder.add_node(call_model)
        builder.add_edge(START, "call_model")

        graph = builder.compile(checkpointer=checkpointer)

        config = RunnableConfig(
            configurable={
                "user_id": settings.DEFAULT_USER_ID,
                "thread_id": settings.DEFAULT_SESSION_ID,
            }
        )

        for query in test_queries:
            print(f"\n=== Query: {query} ===")

            human = HumanMessage(
                content=query,
                additional_kwargs={
                    "generated_at": datetime.now(timezone.utc).isoformat()
                },
            )

            async for chunk in graph.astream(
                {
                    "messages": [human],
                },
                config,
                stream_mode="values",
            ):
                chunk["messages"][-1].pretty_print()

        print("\n=== State History ===\n")
        async for state in graph.aget_state_history(config=config, limit=1):
            print(state, "\n")


if __name__ == "__main__":
    asyncio.run(main())
