#!/usr/bin/env sh

docker run --rm -d -p 27017:27017 \
    -e MONGO_INITDB_ROOT_USERNAME=payler \
    -e MONGO_INITDB_ROOT_PASSWORD=secret \
    -e MONGO_INITDB_DATABASE=payloads \
    --name payler_storage \
    mongo:4.4

docker run --rm -d -p 5672:5672 \
    -e RABBITMQ_DEFAULT_USER=payler -e RABBITMQ_DEFAULT_PASSWORD=empty \
    -e RABBITMQ_DEFAULT_EXCHANGE=local \
    --name payler_broker \
    rabbitmq:3.8-management
