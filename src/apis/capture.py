import re
from typing import Optional, cast
from fastapi import UploadFile
from crawl4ai import AsyncWebCrawler, CrawlResult
from pydantic import HttpUrl
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.configs import crawler_config
from src.schemas.capture import KnowledgeExtractionHelperOutput
from src.db.vectorstore import get_vector_store


async def _handle_selection_capture(selection: str) -> KnowledgeExtractionHelperOutput:
    """
    Handles content extraction from a text selection.
    (Currently a placeholder)
    """
    return KnowledgeExtractionHelperOutput(
        content="PDF content extraction not implemented yet.", metadata={}
    )


async def _handle_url_capture(url: HttpUrl) -> KnowledgeExtractionHelperOutput:
    """
    Extracts content from a URL using crawl4ai.
    """
    crawler = AsyncWebCrawler()
    result: CrawlResult = await crawler.arun(str(url), config=crawler_config)
    if result.success and hasattr(result.markdown, "fit_markdown"):
        fit_md = cast(str, result.markdown.fit_markdown)  # type: ignore
        fit_md = re.sub(r"\s+", " ", fit_md).strip()
        return KnowledgeExtractionHelperOutput(
            content=fit_md, metadata={"source": str(url)}
        )
    return KnowledgeExtractionHelperOutput(content="", metadata={"source": str(url)})


async def _handle_pdf_capture(pdf: UploadFile) -> KnowledgeExtractionHelperOutput:
    """
    Handles content extraction from a PDF file.
    (Currently a placeholder)
    """
    return KnowledgeExtractionHelperOutput(
        content="PDF content extraction not implemented yet.", metadata={}
    )


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
        raise ValueError("Missing data for the specified capture type.")

    # TODO: Start writing the code for storing the content in the vector store
    # - The 'content' variable holds the extracted text.
    # - The 'knowledge_base' variable has the name of the target vector store.
    # - Use langchain/langgraph to create a pipeline that:
    #   1. Chunks the 'content'.
    #   2. Embeds the chunks.
    #   3. Stores the embeddings in the specified 'knowledge_base'.

    if knowledge.content == "":
        raise ValueError("No content extracted from the provided source.")

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

    # third -> store the chunks in the vector store
    vector_store = get_vector_store()
    await vector_store.aadd_documents(docs)

    return {
        "message": f"Content from {type} captured successfully for knowledge base '{knowledge_base}'.",
        "content": knowledge.content,
    }
