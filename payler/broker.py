"""Broker-related utilities."""
import logging
import typing

import aio_pika

from payler.db import SpoolManager
from payler.errors import ProcessingError
from payler.structs import Payload
from payler.logs import build_logger


class BrokerManager:
    """Service to fetch and re-inject payloads."""
    DEFAULT_ROUTING_KEY = "payloads"
    # NOTE: Maybe bind queue to exchange + routing key in configure ?
    DEFAULT_QUEUE_NAME = "payler-jobs"

    def __init__(self):
        self.logger = None  # type: logging.Logger
        self.connection = None  # type: aio_pika.RobustConnection
        self.queue = None  # type: aio_pika.Queue
        self.action: typing.Callable
        self.driver = None  # type: SpoolManager
        self.configured = False

    @classmethod
    async def create(cls, url: str = None, loop = None, logger: logging.Logger = None):
        """Create the backend connection."""
        broker_manager = BrokerManager()
        if logger is None:
            broker_manager.logger = build_logger(cls.__name__)
        broker_manager.connection = await aio_pika.connect_robust(
            url,
            loop=loop,
        )
        return broker_manager

    async def is_reachable(self) -> bool:
        """Ensure connection integrity."""
        result = await self.connection.ready()
        return result is None

    async def send_payload(self, payload: Payload, routing_key: str = None):
        """Send a Payload to self.routing_key."""
        self.logger.info('awaiting connection')
        # import ipdb; ipdb.set_trace()
        self.logger.info('awaiting channel')
        channel = await self.connection.channel()
        routing = routing_key or self.DEFAULT_ROUTING_KEY
        self.logger.info('Processing payload %s', payload)
        result = await channel.default_exchange.publish(
            aio_pika.Message(
                body=payload.message,
            ),
            routing_key=routing,
        )
        self.logger.info('Sent payload to %s', routing)
        await channel.close()
        return result

    def configure(self, action: typing.Callable = print, driver=None, **kwargs):
        """Configure the BrokerManager to serve the listening Queue."""
        # NOTE: could set as property / create BrokerManagerConfig
        self.action = action
        self.driver = driver
        self.configured = True

    async def declare_queue(self, queue_name: str = None, **kwargs) -> aio_pika.Queue:
        """Instantiate a Queue and configure self.queue."""
        # NOTE: could provide default configuration and override using kwargs
        queue_name = queue_name or self.DEFAULT_QUEUE_NAME
        channel = await self.connection.channel()
        queue = await channel.declare_queue(queue_name, **kwargs)
        await channel.close()
        return queue

    async def serve(self, listen_queue: aio_pika.Queue = None, **kwargs):
        """Consume messages from `queue`."""
        self.logger.info(
            "Listening for events (action=%s, driver=%s)",
            self.action.__name__,
            type(self.driver),
        )
        if not self.configured:
            raise ProcessingError(
                f'Configure the {self.__class__.__name__} before using serve',
            )
        async with self.connection:
            async with self.connection.channel() as channel:
                # TODO: Variabilize queue name based on listen_queue or equivalent
                queue = await channel.declare_queue(self.DEFAULT_QUEUE_NAME, **kwargs)
                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            try:
                                await self.action(message, self.driver, **kwargs)
                            except ProcessingError as reason:
                                # NOTE: handle this properly (logging)
                                self.logger.error('could not parse message %s', reason)
                                continue
