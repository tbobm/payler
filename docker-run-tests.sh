#!/bin/sh
docker build -t payler:base .
docker build -t payler:tests -f Dockerfile.test .
docker run -i --rm payler:tests
