#!/bin/sh
python -m pytest --color=yes --cov animator --cov-report term-missing -s tests/
