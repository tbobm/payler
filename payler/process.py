"""Processing functions for broker operations."""
import json

import aio_pika
import pendulum

from payler.db import SpoolManager
from payler.errors import ProcessingError
from payler.structs import Payload


async def spool_message(message: aio_pika.Message, driver: SpoolManager, **kwargs):
    """Decode and spool `message` using `driver`."""
    body = message.body
    print(body)
    try:
        original = json.loads(body)
    except json.decoder.JSONDecodeError as err:
        raise ProcessingError('Could not parse body') from err
    try:
        data = original.pop('payload')
        reference = pendulum.parse(original.pop('reference'))
        source = 'payler-jobs'
        destination = 'payler-out'
    except KeyError as err:
        raise ProcessingError('bad format') from err
    payload = Payload(
        data,
        reference,
        source,
        destination,
    )
    result = await driver.store_payload(payload)
    if result:
        print('stored payload')
        return
    print('did not store payload')
