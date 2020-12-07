#!/usr/bin/env sh

docker network create payler_local || true

docker run --rm -d -p 27017:27017 \
    -e MONGO_INITDB_ROOT_USERNAME=payler \
    -e MONGO_INITDB_ROOT_PASSWORD=secret \
    -e MONGO_INITDB_DATABASE=payloads \
    --network payler_local \
    --name payler_storage \
    mongo:4.4

docker run --rm -d -p 5672:5672 -p 15672:15672\
    -e RABBITMQ_DEFAULT_USER=payler \
    -e RABBITMQ_DEFAULT_PASS=secret \
    -e RABBITMQ_DEFAULT_VHOST=payler \
    --network payler_local \
    --name payler_broker \
    rabbitmq:3.8-management
