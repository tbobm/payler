"""Packaging file for payler."""
from distutils.core import setup


__version__ = "0.0.0"
URL = "https://github.com/tbobm/payler/archive/{}.tar.gz".format(__version__)

setup(
    name="payler",
    packages=["payler"],
    install_requires=['click', "pymongo", 'pyyaml', 'motor', "aio_pika"],
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
            "payler=payler.client:run_cli",
        ],
    },
)
