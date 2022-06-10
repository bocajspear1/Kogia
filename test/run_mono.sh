#!/bin/sh
cd mono
rm ./out/*
DOCKER_BUILDKIT=1 docker build --target artifact --output type=local,dest=. .
cd ..