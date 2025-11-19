from langchain_core.tools import tool

from src.db.vectorstore import get_vector_store
from src.configs.settings import settings
from src.configs.memzero import get_memory
from src.configs.cohere import cohere_ranker


<<<<<<< HEAD
@tool(response_format="content_and_artifact")
async def retrieve_docs(query: str) -> tuple[str, list]:
=======
@tool(response_format="content")
async def retrieve_docs(query: str) -> str:
>>>>>>> eed57bbd488c87162e1ca2c5588b39a9ca109dce
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
<<<<<<< HEAD
        search_type="similarity", search_kwargs={"k": 5}
=======
        search_type="similarity", search_kwargs={"k": 50}
>>>>>>> eed57bbd488c87162e1ca2c5588b39a9ca109dce
    )
    docs = await retriever.ainvoke(query)
    unranked_content = [doc.page_content for doc in docs]

    if not unranked_content:
        return "No relevant context from docs found."

    # rerank the retrieved docs
    reranked_results = cohere_ranker.rerank(
        model=settings.COHERE_RERANKING_MODEL,
        query=query,
        documents=unranked_content,
        top_n=10,
    )

    if not reranked_results.results:
        return "\n\n".join(unranked_content)

    return "\n\n".join(
        [unranked_content[res.index] for res in reranked_results.results]
    )


<<<<<<< HEAD
@tool(response_format="content_and_artifact")
async def retrieve_memory(query: str) -> tuple[str, dict]:
=======
@tool(response_format="content")
async def retrieve_memory(query: str) -> str:
>>>>>>> eed57bbd488c87162e1ca2c5588b39a9ca109dce
    """
    Retrieve relevant information from Mem0 memory about the user.
    Use this for personal information, preferences, or past conversation context.

    Args:
        query: The search query to find relevant memories

    Returns:
        Serialized memories with metadata
    """
    async with get_memory() as memory:
        mem = await memory.search(query, user_id=settings.DEFAULT_USER_ID, limit=10)

    if not mem.get("results"):
        return "No relevant memory found."

    return "\n\n".join([item["memory"] for item in mem["results"]])
