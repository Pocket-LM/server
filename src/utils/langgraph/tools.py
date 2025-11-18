from langchain_core.tools import tool

from src.db.vectorstore import get_vector_store
from src.configs.settings import settings
from src.configs.memzero import get_memory


@tool(response_format="content_and_artifact")
async def retrieve_docs(query: str) -> tuple[str, list]:
    """
    Retrieve relevant context documents from the vector database.
    Use this for factual information, procedures, or document-based knowledge.

    Args:
        query: The search query to find relevant documents

    Returns:
        Serialized documents with metadata and content
    """
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity", search_kwargs={"k": 5}
    )
    docs = await retriever.ainvoke(query)

    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}" for doc in docs
    )

    return serialized, docs


@tool(response_format="content_and_artifact")
async def retrieve_memory(query: str) -> tuple[str, dict]:
    """
    Retrieve relevant information from Mem0 memory about the user.
    Use this for personal information, preferences, or past conversation context.

    Args:
        query: The search query to find relevant memories

    Returns:
        Serialized memories with metadata
    """
    async with get_memory() as memory:
        mem = await memory.search(query, user_id=settings.DEFAULT_USER_ID, limit=5)

    if not mem.get("results"):
        return "No relevant memories found.", {}

    serialized = "\n\n".join(
        f"Source: {item['metadata']}\nMemory: {item['memory']}"
        for item in mem["results"]
    )

    return serialized, mem
