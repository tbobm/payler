#!/bin/sh
# docker build -t payler:base .
# docker build -t payler:tests -f Dockerfile.test .

# ./run-background-service.sh

docker run -i --rm \
    -e MONGODB_URL='mongodb://payler:secret@payler_storage/payloads?authSource=admin' \
    --name payler_tests \
    payler:tests
