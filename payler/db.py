"""Database-related utilities."""
import asyncio

import typing

import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorCollection
import pendulum
import pymongo

from payler.driver import BaseDriver, DriverConfiguration, Result
from payler.errors import ProcessingError
from payler.structs import Payload


class SpoolManager(BaseDriver):
    """Service to store payloads and interact with the Database."""
    # TODO: Move to conf.py
    DEFAULTS = {
        'spool_collection': 'payloads',
        'sleep_duration': 30,
        'default_collection_name': 'payloads',
    }

    def __init__(self, configuration: DriverConfiguration):
        """Create the backend connection."""
        super().__init__(configuration)

        url = configuration.url
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            url,
            connectTimeoutMS=5000,
            serverSelectionTimeoutMS=5000,
            io_loop=configuration.loop,
        )
        self.database = self.client.get_default_database()

        collection_name = configuration.extra.get(
            'spool_collection',
            self.DEFAULTS['default_collection_name'],
        )
        self.collection = self.database[collection_name]  # type: AsyncIOMotorCollection

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

    async def process(self, payload: Payload, **kwargs) -> Result:
        """Store the Payload in the collection along its metadatas."""
        inserted = await self.collection.insert_one(payload.asdict())
        self.logger.debug(
            'stored payload with id=%s reference_date=%s kwargs=%s',
            inserted.inserted_id,
            payload.reference_date,
            kwargs,
        )
        headers = {'location': self.collection.name}
        result = Result(
            success=True,
            headers=headers,
            payload=payload,
            data=inserted,
        )
        return result

    async def _search_ready(self, match_date: pendulum.DateTime) -> typing.Any:
        query = {
            'reference_date': {'$lte': match_date},
        }
        documents = self.collection.find(query)
        async for doc in documents:
            yield doc
        else:
            self.logger.debug('no matching document')
        return

    async def listen(self, **kwargs):
        """Find documents with a `reference_date` older than `match_date`."""
        should_loop = kwargs.get('should_loop', True)
        self.logger.info(
            "Engaging database polling - Applying (action=%s, driver=%s) to events",
            self.action.__name__,
            type(self.driver),
        )
        if not should_loop:
            return await self.process_and_cleanup()
        while True:
            await self.process_and_cleanup()
            self.logger.debug('waiting for %ds', self.DEFAULTS.get('sleep_duration'))
            await asyncio.sleep(self.DEFAULTS['sleep_duration'])

    async def process_and_cleanup(self):
        """Find the matching jobs, process them and remove them from storage."""
        match_date = pendulum.now()
        async for doc in self._search_ready(match_date):
            try:
                result = await self.action(doc, self.driver)
                self.logger.info(
                    'Processed job with id=%s result=%s', doc['_id'], result,
                )
                self._notify_done('success')
            except ProcessingError as err:
                self.logger.error(
                    'Could not process id=%s reason=%s payload=%r',
                    doc['_id'],
                    err,
                    doc,
                )
                self._notify_done('success')
                continue
            if result:
                await self.collection.delete_one({'_id': doc['_id']})
                self.logger.debug('deleted job _id=%s', doc['_id'])
        else:
            self.logger.info('Could not find any document with match_date=%s', match_date)
