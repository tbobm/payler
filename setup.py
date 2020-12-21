"""Packaging file for payler."""
from distutils.core import setup


__version__ = "0.0.0"
URL = "https://github.com/tbobm/payler/archive/{}.tar.gz".format(__version__)

setup(
    name="payler",
    packages=["payler"],
    install_requires=[
        "aio_pika",
        "pymongo",
        'click',
        'motor',
        'pendulum',
        'pyyaml',
    ],
    version=__version__,
    description="Broker payload spooler",
    author="Theo 'Bob' Massard",
    author_email="tbobm@protonmail.com",
    url="https://github.com/tbobm/payler",
    download_url=URL,
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    entry_points={
        "console_scripts": [
            "payler-listen=payler.client:listen_to_broker",
            "payler-watch=payler.client:watch_payloads_ready",
        ],
    },
)
