"""Database-related utilities."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import typing

import motor.motor_asyncio
import pendulum
import pymongo
from motor.motor_asyncio import AsyncIOMotorCollection

from payler.errors import ProcessingError
from payler.logs import build_logger
from payler.metrics import JOB_COUNTER
from payler.structs import Payload


@dataclass
class Result:
    """Class to wrap process outputs."""
    success: bool
    headers: dict
    payload: Payload


# TODO: Class to wrap input paylod
# ex: aio_pika.Message
#    delay = int(message.headers.get('x-delay'))
#    # NOTE: transform default destination in constant
#    destination = message.headers.get('x-destination', 'payler-out')
#    data = message.body
#    now = pendulum.now()
#    reference = now.add(microseconds=delay * 1000)  # switch form us to ms
#    # TODO: Variabilize source
#    source = 'payler-jobs'
#    payload = Payload(
#        data,
#        reference,
#        source,
#        destination,
#    )


class BaseDriver(ABC):
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

        collection_name = spool_collection or self.DEFAULT_COLLECTION_NAME
        self.collection = self.database[collection_name]  # type: AsyncIOMotorCollection

        self.action: typing.Callable
        self.driver = None
        self.kwargs = None

    def __str__(self):
        return f'{type(self)} - {self.database}'

    @abstractmethod
    async def setup(self) -> str:
        # NOTE: Maybe allow both async and sync ?
        """Prepare the OutputDriver configuration.

        Create an index on the storage collection to improve querying spooled payloads.
        Index is created on the `reference_date` field.
        """

    @abstractmethod
    async def is_reachable(self) -> bool:
        """Ensure connection integrity to the remote Backend."""
        ...

    @abstractmethod
    async def process(self, payload: Payload, **kwargs) -> Result:
        """Store the Payload with corresponding metadatas."""
        ...

    def configure(self, action: typing.Callable, driver=None, **kwargs):
        """Configure the manager for post-spooling processing."""
        self.action = action
        self.driver = driver
        self.kwargs = kwargs

    @abstractmethod
    async def listen(self, **kwargs):
        """Find documents with a `reference_date` older than `match_date`."""
        ...

    def _notify_done(self, status: str):
        """Increase the counter with matching status label.


        status can be either 'success' or 'failed'
        """
        JOB_COUNTER.labels(
            self.kwargs.get('name', self.__class__.__name__),
            status,
        ).inc()
