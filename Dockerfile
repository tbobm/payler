FROM python:3.7-slim

WORKDIR /app

COPY ./ .

RUN pip install .
