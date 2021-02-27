"""Broker-related utilities."""
import aio_pika

from payler.driver import BaseDriver, DriverConfiguration, Result
from payler.errors import ProcessingError
from payler.logs import build_logger
from payler.structs import Payload


class BrokerManager(BaseDriver):
    """Service to fetch and re-inject payloads."""
    # NOTE: Maybe bind queue to exchange + routing key in configure ?
    DEFAULTS = {
        'routing_key': 'payloads',
        'queue_name': 'payler-jobs',
    }

    def __init__(self, config: DriverConfiguration):
        super().__init__(config)
        self.connection: aio_pika.RobustConnection
        self.queue: aio_pika.Queue

    @classmethod
    async def create(cls, configuration: DriverConfiguration):
        """Create the backend connection."""
        broker_manager = BrokerManager(configuration)
        broker_manager.logger = configuration.logger
        if broker_manager.logger is None:
            broker_manager.logger = build_logger(cls.__name__)
        broker_manager.connection = await aio_pika.connect_robust(
            configuration.url,
            loop=configuration.loop,
        )
        return broker_manager

    async def is_reachable(self) -> bool:
        """Ensure connection integrity."""
        result = await self.connection.ready()
        return result is None

    async def process(self, payload: Payload, **kwargs) -> Result:
        """Send a Payload to self.routing_key."""
        routing = kwargs.get('routing_key', self.DEFAULTS['routing_key'])
        self.logger.info(
            'Processing payload due for %s with routing_key=%s and kwargs=%s',
            payload.reference_date.isoformat(),
            routing,
            kwargs,
        )

        try:
            message = aio_pika.Message(
                body=payload.message,
            )
        except TypeError as err:
            raise ProcessingError('Invalid payload') from err
        channel = await self.connection.channel()
        published = await channel.default_exchange.publish(
            message,
            routing_key=routing,
        )
        self.logger.debug('Sent payload to %s', routing)
        await channel.close()
        result = Result(
            success=True,
            headers={},
            payload=payload,
            data=published,
        )

        return result

    async def setup(self, **kwargs) -> aio_pika.Queue:
        """Instantiate a Queue and configure self.queue."""
        # NOTE: could provide default configuration and override using kwargs
        queue_name = kwargs.get('queue_name', self.DEFAULTS['queue_name'])
        channel = await self.connection.channel()
        queue = await channel.declare_queue(queue_name, **kwargs)
        await channel.close()
        return queue

    async def listen(self, **kwargs):
        """Consume messages from `queue`."""
        self.logger.info(
            "Listening for events (action=%s, driver=%s)",
            self.action.__name__,
            type(self.driver),
        )
        if self.action is None:
            raise ProcessingError(
                f'Configure the {self.__class__.__name__} before using serve',
            )
        async with self.connection:
            async with self.connection.channel() as channel:
                # TODO: Variabilize queue name based on listen_queue or equivalent
                queue = await channel.declare_queue(self.DEFAULTS['queue_name'], **kwargs)
                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            try:
                                self.logger.debug('Processing %s', message)
                                await self.action(message, self.driver, **kwargs)
                                self._notify_done('success')
                            except ProcessingError as reason:
                                self.logger.error(
                                    'Could not process reason=%s payload=%r',
                                    reason,
                                    message,
                                )
                                self._notify_done('success')
                                continue
