from contextlib import asynccontextmanager
from typing import Annotated, List
from datetime import datetime, timezone
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph
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
from src.configs.memzero import get_memory


class AgentState(MessagesState):
    summary: Annotated[str, "A brief summary of the conversation so far."]
    history: Annotated[List[AnyMessage], add_messages]


llm = ChatGoogleGenerativeAI(
    google_api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_LLM_MODEL
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

SUMMARY_PROMPT = """Previous conversation summary: {summary}
Please create a concise summary of the following conversation messages: {messages}
Provide a brief summary that captures the key points and context."""

GENERATE_PROMPT = """Using the following context documents:{context}\n
Based on the conversation summary: {summary}\n
And the conversation messages: {messages}\n
Generate a comprehensive response to the user's latest query."""


async def manage_context(state: AgentState) -> AgentState:
    messages = state["messages"]
    summary = state.get("summary", "")
    history = state["history"]
    limit = 20  # Number of messages before summarization

    if len(messages) >= limit:
        messages_to_summarize = messages[
            :-5
        ]  # Exclude last 5 messages from summarization
        summarization_prompt = SUMMARY_PROMPT.format(
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


async def respond_or_retrieve(state: AgentState) -> AgentState:
    llm_with_tools = llm.bind_tools([retrieve_context])
    prompt_messages: List[AnyMessage] = [
        SystemMessage(
            content=f"Conversation summary so far: {state.get('summary', "No summary yet.")}"
        ),
    ]
    prompt_messages.extend(state["messages"])
    response = await llm_with_tools.ainvoke(prompt_messages)

    # if (
    #     not response.tool_calls
    #     and isinstance(response.content, list)
    #     and isinstance(response.content[0], dict)
    # ):
    #     response.content = response.content[0]["text"]
    return {
        "messages": [response],
        "summary": state.get("summary", ""),
        "history": [response],
    }


@tool(response_format="content_and_artifact")
async def retrieve_context(query: str):
    """
    A tool to retrieve relevant context documents from the vector database."""
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity", search_kwargs={"k": 20}
    )
    docs = await retriever.ainvoke(query)
    serialized = "\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}") for doc in docs
    )

    return serialized, docs


async def generate_using_context(state: AgentState):
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break

    tool_messages = recent_tool_messages[::-1]  # Reverse to maintain original order
    docs_content = "\n".join(doc.content for doc in tool_messages)
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    conversation_summary = state.get("summary", "No summary yet.")
    prompt = GENERATE_PROMPT.format(
        context=docs_content,
        summary=conversation_summary,
        messages=chr(10).join(
            [f"{msg.type}: {msg.content}" for msg in conversation_messages]
        ),
    )
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    # if (
    #     not response.tool_calls
    #     and isinstance(response.content, list)
    #     and isinstance(response.content[0], dict)
    # ):
    #     response.content = response.content[0]["text"]

    return {
        "messages": [response],
        "summary": conversation_summary,
        "history": [response],
    }


async def save_to_memory(state: AgentState):
    """Saves relevant information to Mem0 memory."""

    conversation_messages = [
        {
            "role": "user" if message.type == "human" else "assistant",
            "content": message.content,
        }
        for message in state["messages"]
        if message.type == "human" or (message.type == "ai" and not message.tool_calls)
    ]

    print(conversation_messages)

    async with get_memory() as memory:
        mem = await memory.get_all(user_id=settings.DEFAULT_USER_ID)
        print(f"Current memory items: {mem}")
        await memory.add(conversation_messages, user_id=settings.DEFAULT_USER_ID)

    return state


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
        builder.add_node("generate_using_context", generate_using_context)
        builder.add_node("save_to_memory", save_to_memory)

        builder.set_entry_point("manage_context")
        builder.add_edge("manage_context", "respond_or_retrieve")
        builder.add_conditional_edges(
            "respond_or_retrieve",
            tools_condition,  # this condition checks if tools were called and return either tools or __end__ only, we can create a custom one though
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

    async for message_chunk, metadata in graph.astream(
        {"messages": [human], "history": [human]},
        config,
        stream_mode="messages",
    ):
        if message_chunk.content:
            if hasattr(message_chunk, "text"):
                print(message_chunk.text, end="|", flush=True)
            else:
                print(message_chunk.content, end="|", flush=True)

    return None


async def main():
    async with get_langgraph_agent(
        user_id=settings.DEFAULT_USER_ID,
        thread_id=settings.DEFAULT_SESSION_ID,
    ) as (graph, config):
        for query in [
            "Hi, my name is Julian.",
            "I am currently studying computer science at King Mongkut's University of Technology Thonburi and a third-year student.",
        ]:
            print(f"\n=== Query: {query} ===")
            await run_agent_message(graph, config, query)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
