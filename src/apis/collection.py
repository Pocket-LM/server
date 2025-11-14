from typing import Sequence
from sqlalchemy import text
from fastapi import HTTPException
from src.configs.settings import settings
from src.db.session import get_async_session
from src.db.vectorstore import get_vector_store


async def handle_collection_listing() -> Sequence[str]:
    """
    Handles the logic for listing all available collections (knowledge bases).
    """
    async with get_async_session() as session:
        statement = f"SELECT name FROM {settings.COLLECTIONS_TABLE}"
        collections = (await session.execute(text(statement))).scalars().all()

        await session.aclose()
    return collections


async def handle_collection_creation(name: str):
    """
    Handles the logic for creating a new collection (knowledge base).
    """
    async with get_async_session() as session:
        statement = f"SELECT uuid FROM {settings.COLLECTIONS_TABLE} WHERE name=:name"
        collection = (
            (await session.execute(text(statement), {"name": name})).scalars().first()
        )
        if collection:
            raise HTTPException(
                status_code=400, detail=f"Collection with name '{name}' already exists."
            )

        # create a new collection
        vector_store = get_vector_store()
        vector_store.collection_name = (
            name  # this will create a new collection if the name does not exist
        )
        await vector_store.acreate_collection()

        await session.commit()
        await session.aclose()

    return None


async def handle_collection_deletion(name: str):
    """
    Handles the logic for deleting an existing collection (knowledge base).
    """
    async with get_async_session() as session:
        statement = f"SELECT uuid FROM {settings.COLLECTIONS_TABLE} WHERE name=:name"
        collection = (
            (await session.execute(text(statement), {"name": name})).scalars().first()
        )
        if not collection:
            raise HTTPException(
                status_code=400, detail=f"Collection with name '{name}' does not exist."
            )

        # delete the collection
        vector_store = get_vector_store()
        vector_store.collection_name = name
        await vector_store.adelete_collection()

        await session.commit()
        await session.aclose()

    return None
