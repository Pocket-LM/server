import re
from typing import Optional, cast
from fastapi import UploadFile, HTTPException
from crawl4ai import AsyncWebCrawler, CrawlResult
from crawl4ai.models import CrawlResultContainer
from pydantic import HttpUrl
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.configs import crawler_config
from src.schemas.capture import KnowledgeExtractionHelperOutput
from src.db.vectorstore import get_vector_store
from src.db.session import get_async_session


async def _handle_selection_capture(selection: str) -> KnowledgeExtractionHelperOutput:
    """
    Extracts text from a user's selection.
    """
    return KnowledgeExtractionHelperOutput(
        content="PDF content extraction not implemented yet.", metadata={}
    )


async def _handle_url_capture(url: HttpUrl) -> KnowledgeExtractionHelperOutput:
    """
    Extracts content from a URL using crawl4ai.
    """
    crawler = AsyncWebCrawler()
    result = cast(
        CrawlResultContainer[CrawlResult],
        await crawler.arun(str(url), config=crawler_config),
    )
    if result.success and hasattr(result.markdown, "fit_markdown"):
        fit_md = cast(str, result.markdown.fit_markdown)  # type: ignore
        fit_md = re.sub(r"\s+", " ", fit_md).strip()
        return KnowledgeExtractionHelperOutput(
            content=fit_md, metadata={"source": str(url)}
        )
    return KnowledgeExtractionHelperOutput(content="", metadata={"source": str(url)})


async def _handle_pdf_capture(pdf: UploadFile) -> KnowledgeExtractionHelperOutput:
    """
    Extracts content from a PDF file.
    """
    return KnowledgeExtractionHelperOutput(
        content="PDF content extraction not implemented yet.", metadata={}
    )


async def _save_to_vector_db(
    knowledge: KnowledgeExtractionHelperOutput, knowledge_base: str
):
    """
    Saves the extracted knowledge to the specified vector knowledge base.
    """

    # first -> create langchain document
    doc = Document(
        page_content=knowledge.content,
        metadata=knowledge.metadata,
    )

    # second -> split the document into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    docs = splitter.split_documents([doc])

    # thrid -> check if collection/knowledge_base exists
    vector_store = get_vector_store()

    # vector_store.collection_name = knowledge_base
    """ 
    Using the above line will create a new collection if it does not exist, 
    which is not the desired behavior. We want to check for existence only. 
    So, it is a two-step process!
    """
    async with get_async_session() as session:
        collection_store = await vector_store.aget_collection(session)
        collection = await collection_store.aget_by_name(session, knowledge_base)
        if not collection:
            raise HTTPException(
                status_code=400,
                detail=f"Knowledge base '{knowledge_base}' does not exist.",
            )
        await session.aclose()

    # fourth -> store the chunks in the vector store
    # set the collection name to the target knowledge base as we know it exists
    vector_store.collection_name = knowledge_base
    await vector_store.aadd_documents(documents=docs)


async def handle_knowledge_capture(
    type: str,
    knowledge_base: str,
    url: Optional[HttpUrl] = None,
    selection: Optional[str] = None,
    pdf: Optional[UploadFile] = None,
):
    """
    Main API function to handle knowledge capture from different sources.
    """

    knowledge: Optional[KnowledgeExtractionHelperOutput] = None

    if type == "selection" and selection and url:
        knowledge = await _handle_selection_capture(selection)
    elif type == "url" and url:
        knowledge = await _handle_url_capture(url)
    elif type == "pdf" and pdf:
        knowledge = await _handle_pdf_capture(pdf)
    else:
        raise HTTPException(
            status_code=400, detail="Missing data for the specified capture type."
        )

    if knowledge.content == "":
        raise HTTPException(
            status_code=400, detail="No content extracted from the provided source."
        )

    await _save_to_vector_db(knowledge, knowledge_base)

    return {
        "message": f"Content from {type} captured successfully for knowledge base '{knowledge_base}'.",
        "content": knowledge.content,
    }
