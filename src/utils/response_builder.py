from typing import Any
from fastapi import status
from fastapi.responses import JSONResponse

from src.schemas.response import ApiResponse, ResponseStatus


class ResponseBuilder:
    """Builder class for creating standardized responses"""

    @staticmethod
    def success(
        status_code: int = status.HTTP_200_OK,
        message: str = "Request successful",
        data: Any = None,
    ) -> JSONResponse:
        """Builds a standardized successful API response."""
        response = ApiResponse(
            success=True,
            status=ResponseStatus.SUCCESS,
            message=message,
            data=data,
        )
        return JSONResponse(
            status_code=status_code,
            content=response.model_dump(exclude_none=True),
        )

    @staticmethod
    def error(
        status_code: int = status.HTTP_400_BAD_REQUEST,
        message: str = "An error occurred",
        data: Any = None,
    ) -> JSONResponse:
        """Builds a standardized error API response."""
        response = ApiResponse(
            success=False,
            status=ResponseStatus.ERROR,
            message=message,
            data=data,
        )
        return JSONResponse(
            status_code=status_code, content=response.model_dump(exclude_none=True)
        )

    @staticmethod
    def warning(
        status_code: int = status.HTTP_200_OK,
        message: str = "Request completed with warnings",
        data: Any = None,
    ) -> JSONResponse:
        """Builds a standardized warning API response."""
        response = ApiResponse(
            success=True,
            status=ResponseStatus.WARNING,
            message=message,
            data=data,
        )
        return JSONResponse(
            status_code=status_code, content=response.model_dump(exclude_none=True)
        )
