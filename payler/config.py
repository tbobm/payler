"""Configuration variables for payler."""
import os


AVAILABLE_SETTINGS = {
    'MONGODB_URL': 'mongodb://payler:secret@localhost/payler',
    'BROKER_URL': 'amqp://payler:secret@localhost/payler',
}


def get(key):
    """Return the matching configuration value."""
    try:
        value = os.environ[key]
        return value
    except KeyError as err:
        if key in AVAILABLE_SETTINGS:
            return AVAILABLE_SETTINGS[key]
        raise RuntimeError(f'Missing configuration variable {err}') from err
