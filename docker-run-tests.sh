#!/bin/sh
if [ "$1" == "--build" ]
then
    docker build -t payler:base .
    docker build -t payler:tests -f Dockerfile.test .
fi

# ./run-background-service.sh

docker run -it --rm \
    -e MONGODB_URL='mongodb://payler:secret@payler_storage/payloads?authSource=admin' \
    --network payler_local \
    --name payler_tests \
    payler:tests
