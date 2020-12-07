#!/bin/sh
python -m pytest --color=yes --cov=. --cov-report term-missing -s tests/
