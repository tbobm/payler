"""Database-related utilities."""
import asyncio

import logging
import typing

import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorCollection
import pendulum
import pymongo

from payler.errors import ProcessingError
from payler.structs import Payload
from payler.logs import build_logger


# NOTE: Create a common class with BrokerManager
class SpoolManager:
    """Service to store payloads and interact with the Database."""
    DEFAULT_COLLECTION_NAME = 'payloads'
    # TODO: Move to conf.py
    DEFAULT_SLEEP_DURATION = 30

    def __init__(self, url: str, loop, spool_collection: str = None, logger: logging.Logger = None):
        """Create the backend connection."""
        if logger is None:
            self.logger = build_logger(self.__class__.__name__)  # type: logging.Logger
        else:
            self.logger = logger
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

    def __str__(self):
        return f'{type(self)} - {self.database}'

    async def setup(self) -> str:
        """Prepare the OutputDriver configuration.

        Create an index on the storage collection to improve querying spooled payloads.
        Index is created on the `reference_date` field.
        """
        infos = await self.collection.index_information()
        for key in infos:
            if 'reference_date' not in key:
                continue
            self.logger.info('Index %s exists', key)
            return key

        result = await self.collection.create_index(
            [('reference_date', pymongo.ASCENDING),],
        )
        if result:
            self.logger.info('Index %s created', result)
        return result

    async def is_reachable(self) -> bool:
        """Ensure connection integrity."""
        result = await self.client.server_info()
        return result is not None

    # TODO: return object
    # NOTE: create DriverResult
    async def store_payload(self, payload: Payload, **kwargs) -> bool:
        """Store the Payload with corresponding metadatas."""
        result = await self.collection.insert_one(payload.asdict())
        self.logger.debug(
            'stored payload with id=%s reference_date=%s kwargs=%s',
            result.inserted_id,
            payload.reference_date,
            kwargs,
        )
        return result

    # TODO: Common method with BrokerManager
    def configure(self, action: typing.Callable, driver=None):
        """Configure the manager for post-spooling processing."""
        self.action = action
        self.driver = driver

    async def _search_ready(self, match_date: pendulum.datetime) -> typing.Any:
        query = {
            'reference_date': {'$lte': match_date},
        }
        documents = self.collection.find(query)
        async for doc in documents:
            yield doc
        else:
            self.logger.debug('no matching document')
        return

    async def search_ready(self, should_loop=True):
        """Find documents with a `reference_date` older than `match_date`."""
        self.logger.info(
            "Engaging database polling - Applying (action=%s, driver=%s) to events",
            self.action.__name__,
            type(self.driver),
        )
        if not should_loop:
            return await self.process_and_cleanup()
        while True:
            await self.process_and_cleanup()
            self.logger.debug('waiting for %ds', self.DEFAULT_SLEEP_DURATION)
            await asyncio.sleep(self.DEFAULT_SLEEP_DURATION)

    async def process_and_cleanup(self):
        """Find the matching jobs, process them and remove them from storage."""
        match_date = pendulum.now()
        async for doc in self._search_ready(match_date):
            try:
                result = await self.action(doc, self.driver)
                self.logger.info(
                    'Processed job with id=%s result=%s', doc['_id'], result,
                )
            except ProcessingError as err:
                self.logger.error('Could not parse %s: %s', doc['_id'], err)
                continue
            if result:
                await self.collection.delete_one({'_id': doc['_id']})
                self.logger.debug('deleted job _id=%s', doc['_id'])
        else:
            self.logger.info('Could not find any document with match_date=%s', match_date)
