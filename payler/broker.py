"""Broker-related utilities."""
import logging

import aio_pika

from payler.logs import build_logger


class BrokerManager:
    """Service to fetch and re-inject payloads."""

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
