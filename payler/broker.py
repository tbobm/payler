"""Broker-related utilities."""
import logging

import aio_pika

from payler.structs import Payload
from payler.logs import build_logger


class BrokerManager:
    """Service to fetch and re-inject payloads."""
    DEFAULT_ROUTING_KEY = "payloads"

    def __init__(self):
        self.logger = None
        self.connection = None

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
        async with self.connection:
            channel = await self.connection.channel()
            return await channel.default_exchange.publish(
                aio_pika.Message(
                    body=payload.message.encode(),
                    ),
                routing_key=routing_key or self.DEFAULT_ROUTING_KEY,
            )
