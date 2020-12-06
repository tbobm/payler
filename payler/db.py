"""Database-related utilities."""
from datetime import datetime
import logging

import motor.motor_asyncio

from payler.structs import Payload
from payler.logs import build_logger


class SpoolManager:
    """Service to store payloads and interact with the Database."""
    DEFAULT_COLLECTION_NAME = 'payloads'

    def __init__(self, url: str, spool_collection: str = None, logger: logging.Logger = None):
        """Create the backend connection."""
        if logger is None:
            self.logger = build_logger(self.__class__.__name__)
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            url,
            connectTimeoutMS=5000,
            serverSelectionTimeoutMS=5000,
        )
        self.database = self.client.get_default_database()
        self.collection_name = spool_collection or self.DEFAULT_COLLECTION_NAME
        self.collection = self.database[self.collection_name]

    async def is_reachable(self) -> bool:
        """Ensure connection integrity."""
        result = await self.client.server_info()
        return result is not None

    async def store_payload(self, payload: Payload) -> bool:
        """Store the Payload with corresponding metadatas."""
        result = await self.collection.insert_one(payload.asdict())
        self.logger.debug(
            'stored payload with id=%s reference_date=%s',
            result.inserted_id,
            payload.reference_date,
        )
        return result.acknowledged


    async def search_ready(self, match_date: datetime):
        """Find documents with a `reference_date` older than `match_date`."""
