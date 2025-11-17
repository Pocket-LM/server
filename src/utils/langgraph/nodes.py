from typing import List
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    SystemMessage,
    RemoveMessage,
)

from src.schemas.langgraph import AgentState
from src.utils.langgraph.config import (
    llm,
    MESSAGE_LIMIT,
    MESSAGES_TO_KEEP,
    SYSTEM_PROMPT,
    SUMMARY_PROMPT,
    GENERATE_PROMPT,
)
from src.utils.langgraph.tools import retrieve_docs, retrieve_memory
from src.configs.settings import settings
from src.configs.memzero import get_memory


async def manage_context(state: AgentState) -> AgentState:
    """
    Manage conversation context by summarizing old messages when limit is reached.
    Keeps recent messages while summarizing older ones to maintain context window.
    """
    messages = state["messages"]
    summary = state.get("summary", "")
    history = state["history"]

    if len(messages) < MESSAGE_LIMIT:
        return state

    # Summarize all but the most recent messages
    messages_to_summarize = messages[:-MESSAGES_TO_KEEP]

    summarization_prompt = SUMMARY_PROMPT.format(
        summary=summary if summary else "None",
        messages="\n".join(
            f"{msg.type}: {msg.content}" for msg in messages_to_summarize
        ),
    )

    summary_response = await llm.ainvoke([HumanMessage(content=summarization_prompt)])

    # Mark old messages for removal
    messages_to_remove = [
        RemoveMessage(id=str(msg.id)) for msg in messages[:-MESSAGES_TO_KEEP]
    ]

    return {
        "messages": messages_to_remove,  # type: ignore
        "summary": str(summary_response.content),
        "history": history,
    }


async def respond_or_retrieve(state: AgentState) -> AgentState:
    """
    Entry node that decides which retrieval tools to use based on the query.
    The LLM will intelligently choose between retrieve_docs, retrieve_memory, or both.
    """
    llm_with_tools = llm.bind_tools([retrieve_docs, retrieve_memory])

    prompt_messages: List[AnyMessage] = [
        SystemMessage(content=SYSTEM_PROMPT),
        SystemMessage(
            content=f"Conversation summary: {state.get('summary', 'No summary yet.')}"
        ),
    ]
    prompt_messages.extend(state["messages"])

    response = await llm_with_tools.ainvoke(prompt_messages)

    return {
        "messages": [response],
        "summary": state.get("summary", ""),
        "history": [response],
    }


async def generate_using_context(state: AgentState) -> AgentState:
    """
    Generate a response using the retrieved context from tools.
    Combines tool results with conversation history to create a comprehensive answer.
    """
    # Extract recent tool messages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break

    # Reverse to maintain chronological order
    tool_messages = recent_tool_messages[::-1]
    docs_content = "\n\n".join(doc.content for doc in tool_messages)

    # Get conversation messages (exclude tool-related messages)
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
        messages="\n".join(
            f"{msg.type}: {msg.content}" for msg in conversation_messages
        ),
    )

    response = await llm.ainvoke([HumanMessage(content=prompt)])

    return {
        "messages": [response],
        "summary": conversation_summary,
        "history": [response],
    }


async def save_to_memory(state: AgentState) -> AgentState:
    """
    Save relevant conversation information to Mem0 memory for future retrieval.
    Stores user messages and assistant responses (excluding tool calls).
    """
    conversation_messages = [
        {
            "role": "user" if message.type == "human" else "assistant",
            "content": message.content,
        }
        for message in state["messages"]
        if message.type == "human" or (message.type == "ai" and not message.tool_calls)
    ]

    async with get_memory() as memory:
        await memory.add(conversation_messages, user_id=settings.DEFAULT_USER_ID)

    return state
