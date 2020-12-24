#!/bin/sh
python -m pytest --color=yes --cov=./payler --cov-report term-missing tests/
