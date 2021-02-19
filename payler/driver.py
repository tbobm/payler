"""Common Driver utility module."""
from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop
from dataclasses import dataclass, field
import logging
import typing


from payler.logs import build_logger
from payler.metrics import JOB_COUNTER
from payler.structs import Payload


@dataclass
class Result:
    """Wrapper class to ease post-processing."""
    success: bool
    headers: dict
    payload: Payload


@dataclass
class DriverConfiguration:
    """Common configuration for `BaseDriver` class.

    :attr name: driver instance name
    :attr url: connection URL for the backend
    :attr loop: asyncio EventLoop
    :attr logger: used by the Driver
    :attr extra: kwargs-style extra argument for further driver configuration
    """
    name: str
    url: str
    loop: AbstractEventLoop = None
    logger: logging.Logger = None
    extra: dict = field(default_factory = lambda _: dict())


class BaseDriver(ABC):
    """Parent class for Driver implementation."""

    def __init__(self, config: DriverConfiguration):
        """Create the backend connection."""
        self.logger = config.logger
        if self.logger is None:
            self.logger = build_logger(self.__class__.__name__)  # type: logging.Logger

        self.action: typing.Callable
        self.driver = None
        self.kwargs = None

    def __str__(self):
        return f'{type(self)}'

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
