"""Database-related utilities."""
import asyncio

import logging
import typing
import time

import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorCollection
import pendulum

from payler.structs import Payload
from payler.logs import build_logger


# NOTE: Create a common class with BrokerManager
class SpoolManager:
    """Service to store payloads and interact with the Database."""
    DEFAULT_COLLECTION_NAME = 'payloads'
    # TODO: Move to conf.py
    DEFAULT_SLEEP_DURATION = 5

    def __init__(self, url: str, loop, spool_collection: str = None, logger: logging.Logger = None):
        """Create the backend connection."""
        if logger is None:
            self.logger = build_logger(self.__class__.__name__)
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            url,
            connectTimeoutMS=5000,
            serverSelectionTimeoutMS=5000,
            io_loop=loop,
        )
        self.database = self.client.get_default_database()
        self.collection_name = spool_collection or self.DEFAULT_COLLECTION_NAME
        self.collection = self.database[self.collection_name]  # type: AsyncIOMotorCollection

        self.action: typing.Callable
        self.driver = None
        self.configured = False

    def __str__(self):
        return f'{type(self)} - {self.database}'

    async def is_reachable(self) -> bool:
        """Ensure connection integrity."""
        result = await self.client.server_info()
        return result is not None

    # TODO: return object
    # NOTE: create DriverResult
    async def store_payload(self, payload: Payload) -> bool:
        """Store the Payload with corresponding metadatas."""
        result = await self.collection.insert_one(payload.asdict())
        self.logger.debug(
            'stored payload with id=%s reference_date=%s',
            result.inserted_id,
            payload.reference_date,
        )
        return result.acknowledged

    # TODO: Common method with BrokerManager
    def configure(self, action: typing.Callable, driver=None):
        """Configure the manager for post-spooling processing."""
        self.action = action
        self.driver = driver
        self.configured = True

    async def _search_ready(self, match_date: pendulum.datetime, action) -> typing.Any:
        query = {
            'reference_date': {'$lte': match_date},
        }
        documents = self.collection.find(query)
        async for doc in documents:
            result = await self.action(doc, self.driver)
            self.logger.info(
                'Processed job with id=%s result=%s', doc['_id'], result,
            )
            if result:
                await self.collection.delete_one({'_id': doc['_id']}, )
        else:
            self.logger.info('no matching document')

    async def search_ready(self):
        """Find documents with a `reference_date` older than `match_date`."""
        self.logger.info(
            "Engaging database polling - Applying (action=%s, driver=%s) to events",
            self.action.__name__,
            type(self.driver),
        )
        while True:
            match_date = pendulum.now()
            self.logger.info('waiting for %d', self.DEFAULT_SLEEP_DURATION)
            await self._search_ready(match_date, self.action)
            await asyncio.sleep(self.DEFAULT_SLEEP_DURATION)
