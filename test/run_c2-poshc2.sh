#!/bin/sh
cd c2-poshc2
rm ./out/*
DOCKER_BUILDKIT=1 docker build --progress=plain --target artifact --output type=local,dest=. .
cd ..