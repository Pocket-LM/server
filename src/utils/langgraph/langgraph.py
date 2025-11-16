from contextlib import asynccontextmanager
from typing import Annotated, List
from datetime import datetime, timezone
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages, MessagesState
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    SystemMessage,
    RemoveMessage,
)
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from src.db.vectorstore import get_vector_store
from src.configs.settings import settings


class AgentState(MessagesState):
    summary: Annotated[str, "A brief summary of the conversation so far."]
    history: Annotated[List[AnyMessage], add_messages]


llm = ChatOllama(
    model=settings.OLLAMA_LLM_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    validate_model_on_init=True,
    temperature=0.1,
)


SYSTEM_PROMPT = """You are a Retrieval-Augmented Generation (RAG) assistant.
Use the provided context documents to answer the user's question.
If the answer is clearly supported by the retrieved context, cite or paraphrase it.
If no relevant information is found in the context, say so and provide a helpful general answer, but do NOT invent facts.

Rules:
- Never assume information not present in the provided context.
- Prefer quotes, paraphrases, or summaries from the retrieved context.
- If the user asks something outside the retrieved context, say: 
  "I could not find this in the provided documents, but here is what I can tell in general…"
- Keep answers clear, structured, and concise."""

SUMMARIZATION_PROMPT = """Previous conversation summary: {summary}
Please create a concise summary of the following conversation messages: {messages}
Provide a brief summary that captures the key points and context."""


async def manage_context(state: AgentState) -> AgentState:
    messages = state["messages"]
    summary = state.get("summary", "")
    history = state["history"]
    limit = 20  # Number of messages before summarization

    if len(messages) >= limit:
        messages_to_summarize = messages[
            :-5
        ]  # Exclude last 5 messages from summarization
        summarization_prompt = SUMMARIZATION_PROMPT.format(
            summary=summary if summary else "None",
            messages=chr(10).join(
                [f"{msg.type}: {msg.content}" for msg in messages_to_summarize]
            ),
        )
        summary_response = await llm.ainvoke(
            [HumanMessage(content=summarization_prompt)]
        )
        remaining = [
            RemoveMessage(id=str(msg.id)) for msg in messages[:-5]
        ]  # Remove all but last 5 messages

        return {
            "messages": remaining,  # type: ignore
            "summary": str(summary_response.content),
            "history": history,
        }

    return state


async def respond_or_retrieve(state: AgentState):
    llm_with_tools = llm.bind_tools([retrieve_context])
    prompt_messages: List[AnyMessage] = [
        SystemMessage(
            content=f"Conversation summary so far: {state.get('summary', "No summary yet.")}"
        ),
    ]
    prompt_messages.extend(state["messages"])
    response = await llm.ainvoke(prompt_messages)
    return {
        "messages": [response],
        "summary": state.get("summary", ""),
    }


@tool(response_format="content_and_artifact")
async def retrieve_context(query: str):
    """
    A tool to retrieve relevant context documents from the vector database."""
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity", search_kwargs={"k": 20}
    )
    docs = retriever.invoke(query)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}") for doc in docs
    )
    return serialized, docs


async def generate_using_context():
    pass


@asynccontextmanager
async def get_checkpoint_saver():
    async with AsyncPostgresSaver.from_conn_string(
        settings.PLAIN_DATABASE_URL
    ) as checkpoint_saver:
        try:
            yield checkpoint_saver
        finally:
            pass


@asynccontextmanager
async def get_langgraph_agent(user_id: str, thread_id: str):
    """
    Returns (graph, config) for the LangGraph agent.
    This can be used inside an API route.
    """

    async with get_checkpoint_saver() as checkpoint_saver:
        await checkpoint_saver.setup()
        await checkpoint_saver.adelete_thread(thread_id=settings.DEFAULT_SESSION_ID)

        builder = StateGraph(AgentState)
        builder.add_node("manage_context", manage_context)
        builder.add_node("respond_or_retrieve", respond_or_retrieve)
        builder.add_node("tools", ToolNode(tools=[retrieve_context]))
        # builder.add_node("generate_using_context", generate_using_context)

        # builder.add_edge(START, "manage_context")
        # builder.add_edge("manage_context", "respond_or_retrieve")
        # builder.add_edge("respond_or_retrieve", END)

        builder.add_edge(START, "manage_context")
        builder.add_edge("manage_context", "respond_or_retrieve")
        builder.add_conditional_edges(
            "respond_or_retrieve", tools_condition, {END: END, "tools": "tools"}
        )
        builder.add_edge("tools", END)
        # builder.add_edge("tools", "generate_using_context")
        # builder.add_edge("generate_using_context", END)

        graph = builder.compile(checkpointer=checkpoint_saver)

        config = RunnableConfig(
            configurable={
                "user_id": user_id,
                "thread_id": thread_id,
            }
        )

        try:
            yield graph, config
        finally:
            pass


async def run_agent_message(graph, config, query: str):
    """Send one human message to the agent and return the AI reply."""

    human = HumanMessage(
        content=query,
        additional_kwargs={"generated_at": datetime.now(timezone.utc).isoformat()},
    )

    result_msg = None

    async for chunk in graph.astream(
        {"messages": [human], "history": [human]},
        config,
        stream_mode="values",
    ):
        result_msg = chunk["messages"][-1]

    return result_msg


async def main():
    async with get_langgraph_agent(
        user_id=settings.DEFAULT_USER_ID,
        thread_id=settings.DEFAULT_SESSION_ID,
    ) as (graph, config):
        for query in [
            "Hi, my name is Julian.",
            "Can you remind me what my name is?",
            "What's the capital of France?",
        ]:
            print(f"\n=== Query: {query} ===")

            response = await run_agent_message(graph, config, query)
            response.pretty_print()  # type: ignore

        print(f"\n=== State History ===")
        async for state in graph.aget_state_history(config=config, limit=1):
            print(state, "\n")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
