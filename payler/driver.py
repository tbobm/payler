"""Core components of Payler.

The :class:`BaseDriver` class is the foundation of the plugin mechanism of
Payler.  It allows wrapping common methods such as
:meth:`BaseDriver.process` or :meth:`BaseDriver.listen`
"""
from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop
from dataclasses import dataclass, field
import logging
import typing
from typing import Any, Dict, Union, Optional


from payler.logs import build_logger
from payler.metrics import JOB_COUNTER
from payler.structs import Payload


@dataclass
class Result:
    """Wrapper class to ease post-processing."""
    success: bool
    headers: dict
    payload: Payload
    data: Any


def _generate_empty_dict() -> Dict[str,Any]:
    _empty = dict()  # type: Dict[str,Any]
    return _empty


@dataclass
class DriverConfiguration:
    """Configuration for the :class:`BaseDriver` class.

    Provide a common interface to create new drivers based on the
    :class:`BaseDriver`.

    :attr:`DriverConfiguration.extra` can be used to further customize
    the backends configurations.

    :attr name: the driver instance name
    :attr url: the connection URL for the backend
    :attr loop: the main asyncio EventLoop
    :attr logger: logging interface to be used by the :class:`BaseDriver`
    :attr extra: kwargs-style extra argument for further driver configuration
    """
    name: str
    url: str
    loop: AbstractEventLoop
    logger: logging.Logger
    extra: Dict[str, Any] = field(default_factory=_generate_empty_dict)


class BaseDriver(ABC):
    """Parent class for driver implementation.

    Drivers **must** inherit the :class:`BaseDriver` class and implement
    the following methods:

    - :meth:`BaseDriver.listen` - Use driver as input
    - :meth:`BaseDriver.process` - Use driver as output

    The :attr:`BaseDriver.DEFAULTS` class attribute **may** be used to expose
    default values for the setup or processing methods.

    Use-cases can be any of:

    - timeout values (highly encouraged) for remote backends
    - queue name, collection name
    """
    DEFAULTS = {
        'version': '0',
    }  # type: Dict[str,Union[str,int]]

    def __init__(self, config: DriverConfiguration):
        """Configure and instantiate the driver.

        Current method configures the logging mechanism if missing by
        calling :func:`build_logger` with the instantiated class name.

        Additional :attr:`kwargs` are configured using :param:`config.extra`
        """
        if config.logger is None:
            self.logger = build_logger(self.__class__.__name__)  # type: logging.Logger
        else:
            self.logger = config.logger

        self.action: typing.Callable
        self.driver = None  # type: Optional[BaseDriver]
        self.kwargs = config.extra

    def __str__(self):
        return f'{type(self)}'

    @abstractmethod
    async def setup(self, **kwargs: Dict[str, Any]) -> typing.Any:
        # NOTE: Maybe allow both async and sync ?
        """Configure the :class:`BaseDriver` backend.

        Implementation can be:

        - Add indexes on table / collection
        - Create Queue / Exchange
        - Register to a pool of worker to receive workfload
        """

    @abstractmethod
    async def is_reachable(self) -> bool:
        """Ensure connection integrity to the remote Backend."""
        ...

    @abstractmethod
    async def process(self, payload: Payload, **kwargs) -> Result:
        """Interact with a single Payload.

        Behaviour can be described as a sink behaviour.

        Implementations can be:

        - Store a :class:`Payload` in a Database
        - Historize a :class:`Payload` to S3
        - Send a message in RabbitMQ
        - Enrich :class:`payload` and publish in a Redis

        :class:`Result` **must** conform to the following principles:

        - The :attr:`Result.success` **must** inform of the processing state
        - The :attr:`Result.payload` **must** match the final data
        - The :attr:`Result.data` **can** be used as a way to return feedback
        """
        ...

    def configure(self,
                  action: typing.Callable,
                  driver: Optional['BaseDriver']=None,
                  **kwargs: Dict[str, Any]):
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
