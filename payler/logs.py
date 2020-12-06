"""Logging-related utility functions.

Provide a friendly interface to log payler's operations.
"""
import logging


LOG_FORMAT = "%(asctime)s - [%(levelname)8s] - %(name)s: %(message)s"


# TODO: Variabilize verbosity
def build_logger(name: str) -> logging.Logger:
    """Configure a logger with a `name`.

    Example output:
        2020-10-30 17:55:59,927 - [    INFO ] - SpookManager: inserted document with _id=...
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger
