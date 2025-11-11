from enum import Enum
from typing import Any, Optional
from pydantic import Field

from src.schemas.custom_base_model import CamelCaseBaseModel as BaseModel


class ResponseStatus(str, Enum):
    """Response status enumeration"""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class ApiResponse(BaseModel):
    """Standardized API response format"""

    success: bool = Field(..., description="Whether the request was successful")
    status: ResponseStatus = Field(..., description="Response status")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Any] = Field(default=None, description="Response data")
