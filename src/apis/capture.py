import re
import os
from uuid import uuid4
from typing import Optional, List, cast
from fastapi import UploadFile, HTTPException
from crawl4ai import AsyncWebCrawler, CrawlResult
from crawl4ai.models import CrawlResultContainer
from pydantic import HttpUrl
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from src.configs import crawler_config
from src.schemas.capture import KnowledgeExtractionHelperOutput
from src.db.vectorstore import get_vector_store
from src.db.session import get_async_session
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def _handle_selection_capture(
    selection: str, url: HttpUrl
) -> List[KnowledgeExtractionHelperOutput] | None:
    """
    Extracts text from a user's selection.
    """
    cleaned = re.sub(r"\s+", " ", selection).strip()
    if len(cleaned) > 0:
        return [
            KnowledgeExtractionHelperOutput(
                content=cleaned, metadata={"source": str(url)}
            )
        ]

    return None


async def _handle_url_capture(
    url: HttpUrl,
) -> List[KnowledgeExtractionHelperOutput] | None:
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
        return [
            KnowledgeExtractionHelperOutput(
                content=fit_md, metadata={"source": str(url)}
            )
        ]
    return None


async def _handle_pdf_capture(
    pdf: UploadFile,
) -> List[KnowledgeExtractionHelperOutput] | None:
    """
    Extracts content from a PDF file.
    The UploadFile will be stored temporarily on disk for processing.
    Then it will be immediately deleted.
    """

    # write the uploaded file to a temp file
    tmp_filepath = f"{os.getcwd()}/tmp/{uuid4()}_{pdf.filename}"
    with open(tmp_filepath, "wb") as f:
        f.write(await pdf.read())

    # limitation: we do not extract images for now
    loader = PyMuPDF4LLMLoader(
        file_path=tmp_filepath,
        mode="page",
        extract_images=False,
        table_strategy="lines_strict",
    )

    # load and process the pdf
    try:
        docs = await loader.aload()
        if len(docs) == 0:
            return None

        knowledge = []
        for doc in docs:
            page_md = re.sub(r"\s+", " ", doc.page_content).strip()
            if len(page_md) > 0:
                knowledge.append(
                    KnowledgeExtractionHelperOutput(
                        content=page_md,
                        metadata={
                            "source": pdf.filename,
                            "page_number": doc.metadata.get("page", None),
                            "author": doc.metadata.get("author", None),
                            "title": doc.metadata.get("title", None),
                            "subject": doc.metadata.get("subject", None),
                            "keywords": doc.metadata.get("keywords", None),
                            "total_pages": doc.metadata.get("total_pages", None),
                            "creator": doc.metadata.get("creator", None),
                            "producer": doc.metadata.get("producer", None),
                        },
                    )
                )

        if len(knowledge) == 0:
            return None

        return knowledge
    finally:
        if os.path.exists(tmp_filepath):
            os.remove(tmp_filepath)


async def _save_to_vector_db(
    knowledge: List[KnowledgeExtractionHelperOutput], knowledge_base: str
):
    """
    Saves the extracted knowledge to the specified vector knowledge base.
    """

    # first -> check if collection/knowledge_base exists
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

    # second -> create langchain docs
    docs = [Document(page_content=k.content, metadata=k.metadata) for k in knowledge]

    # third -> split the documents into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    split_docs = splitter.split_documents(docs)

    # fourth -> store the chunks in the vector store
    # set the collection name to the target knowledge base as we know it exists
    vector_store.collection_name = knowledge_base
    await vector_store.aadd_documents(documents=split_docs)


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

    knowledge: Optional[List[KnowledgeExtractionHelperOutput]] = None

    if type == "selection" and selection and url:
        knowledge = await _handle_selection_capture(selection, url)
    elif type == "url" and url:
        knowledge = await _handle_url_capture(url)
    elif type == "pdf" and pdf:
        knowledge = await _handle_pdf_capture(pdf)
    else:
        raise HTTPException(
            status_code=400, detail="Missing data for the specified capture type."
        )

    if not knowledge:
        raise HTTPException(
            status_code=400, detail="No content extracted from the provided source."
        )

    await _save_to_vector_db(knowledge, knowledge_base)

    return None
