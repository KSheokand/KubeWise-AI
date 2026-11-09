import asyncio

from app.core.database import (
    connect_database,
    close_database,
    get_database
)

async def main():

    try:
        await connect_database()

        db = get_database()

        print("\nDatabase name:", db.name)

        collections = await db.list_collection_names()

        print("Collections:", collections)
        print("\nMongoDB connection test successfull!")

    except Exception as error:
        print("\nMongoDB connection failed:")
        print(type(error).__name__, str(error))

    finally:
        await close_database()

if __name__ == "__main__":
    asyncio.run(main())