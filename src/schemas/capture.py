from typing import Literal, Optional, Dict
from pydantic import HttpUrl, Field
from fastapi import UploadFile

from src.schemas.custom_base_model import CamelCaseBaseModel

CaptureType = Literal["selection", "url", "pdf"]


class KnowledgeExtractionHelperOutput(CamelCaseBaseModel):
    content: str = Field(..., description="Extracted content from the knowledge source")
    metadata: Dict = Field(..., description="Metadata related to the extracted content")


class KnowledgeCaptureRequest(CamelCaseBaseModel):
    type: CaptureType = Field(..., description="Type of knowledge capture")
    knowledge_base: str = Field(..., description="Target knowledge base name")
    url: Optional[HttpUrl] = Field(None, description="URL to capture knowledge from")
    selection: Optional[str] = Field(
        None, description="Text selection to capture knowledge from"
    )
    pdf: Optional[UploadFile] = Field(
        None, description="PDF file to capture knowledge from"
    )
