import asyncio
from sqlalchemy import text

from src.db.vectorstore import get_vector_store
from src.db.session import get_async_session


async def main():
    await get_vector_store().adrop_tables()

    async with get_async_session() as session:
        await session.execute(
            text(
                """
                DROP TABLE IF EXISTS
                    checkpoint_blobs,
                    checkpoint_migrations,
                    checkpoint_writes,
                    checkpoints,
                    mem0,
                    mem0migrations
                CASCADE;
            """
            )
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
