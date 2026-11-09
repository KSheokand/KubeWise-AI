import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import HTTPException
from pymongo import AsyncMongoClient, ASCENDING, DESCENDING

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "KubeWiseAI")

mongo_client = None
database = None


async def connect_database():
    """Initialize MongoDB connection and create indexes."""

    global mongo_client, database

    if not MONGODB_URL:
        raise RuntimeError("MONGODB_URL is not configured in .env")

    mongo_client = AsyncMongoClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=10000
    )

    try:
        await mongo_client.admin.command("ping")

        database = mongo_client[MONGODB_DATABASE]

        # Incident indexes
        await database.incidents.create_index(
            [("fingerprint", ASCENDING), ("status", ASCENDING)],
            name="fingerprint_status_idx"
        )

        await database.incidents.create_index(
            [("severity", ASCENDING), ("status", ASCENDING)],
            name="severity_status_idx"
        )

        await database.incidents.create_index(
            [("last_seen", DESCENDING)],
            name="last_seen_idx"
        )

        # Incident event indexes
        await database.incident_events.create_index(
            [("incident_id", ASCENDING), ("timestamp", DESCENDING)],
            name="incident_event_history_idx"
        )

        await database.incidents.create_index(
            [("fingerprint", ASCENDING)],
            unique=True,
            partialFilterExpression={"status":"active"},
            name="unique_active_incident_fingerprint"
        )

        print(f"Connected to MongoDB database: {MONGODB_DATABASE}")

    except Exception:
        await mongo_client.close()
        mongo_client = None
        database = None
        raise


async def close_database():
    """Close MongoDB connection."""

    global mongo_client, database

    if mongo_client is not None:
        await mongo_client.close()

    mongo_client = None
    database = None

    print("MongoDB connection closed")


def get_database():
    """Return the active database instance."""

    if database is None:
        raise HTTPException(
            status_code=503,
            detail="Database is not connected"
        )

    return database


def get_collection(collection_name: str):
    """Return a MongoDB collection."""

    return get_database()[collection_name]