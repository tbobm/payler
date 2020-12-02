"""Configuration variables for payler."""
import os


def get(key):
    """Return the matching configuration value."""
    try:
        return os.environ[key]
    except KeyError as err:
        raise RuntimeError(f'Missing configuration variable {err}') from err
