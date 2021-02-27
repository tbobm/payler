"""Processing functions for broker operations."""
import aio_pika
import pendulum

from payler.broker import BrokerManager
from payler.db import SpoolManager
from payler.driver import Result
from payler.structs import Payload


async def spool_message(message: aio_pika.Message, driver: SpoolManager, **kwargs) -> Result:
    """Decode and spool `message` using `driver`."""
    delay = int(message.headers.get('x-delay'))
    # NOTE: transform default destination in constant
    destination = message.headers.get('x-destination', 'payler-out')
    data = message.body
    now = pendulum.now()
    reference = now.add(microseconds=delay * 1000)  # switch form us to ms
    # TODO: Variabilize source
    source = 'payler-jobs'
    payload = Payload(
        data,
        reference,
        source,
        destination,
    )
    result = await driver.process(payload, **kwargs)
    # TODO: do correct post-processing logging
    return result


async def send_message_back(document: dict, driver: BrokerManager, **kwargs):
    """Inject the Payload back in the Broker."""
    payload = Payload(
        message=document['message'],
        reference_date=document['reference_date'],
        source=document['source'],
        destination=document['destination'],
    )
    return await driver.process(payload, routing_key=payload.destination, **kwargs)
