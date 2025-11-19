from fastapi import APIRouter, Depends, Body
from typing import Annotated

from src.apis.collection import *
from src.db.vectorstore import ensure_vector_store_initialized
from src.utils.response_builder import ResponseBuilder
from src.schemas.custom_base_model import CamelCaseBaseModel

collection_router = APIRouter(dependencies=[Depends(ensure_vector_store_initialized)])


class CollectionCreateRequest(CamelCaseBaseModel):
    name: str


@collection_router.get("")
async def list_collections():
    """
    API endpoint to list all collections (knowledge bases).
    """
    try:
        collections = await handle_collection_listing()
        return ResponseBuilder.success(
            message="Collections retrieved successfully.",
            data=collections,
        )
    except Exception as e:
        raise e


@collection_router.post("")
async def create_collection(
    body: Annotated[CollectionCreateRequest, Body(...)],
):
    """
    API endpoint to create a new collection (knowledge base).
    """
    try:
        await handle_collection_creation(body.name)
        return ResponseBuilder.success(
            message=f"Collection '{body.name}' created successfully.",
            data=None,
        )
    except Exception as e:
        raise e


@collection_router.delete("")
async def delete_collection(body: Annotated[CollectionCreateRequest, Body(...)]):
    """
    API endpoint to delete a collection (knowledge base).
    """
    try:
        await handle_collection_deletion(body.name)
        return ResponseBuilder.success(
            message=f"Collection '{body.name}' deleted successfully.",
            data=None,
        )
    except Exception as e:
        raise e
