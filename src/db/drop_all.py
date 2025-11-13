if __name__ == "__main__":
    import asyncio
    from .vectorstore import get_vector_store

    asyncio.run(get_vector_store().adrop_tables())
