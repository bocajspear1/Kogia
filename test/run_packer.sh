#!/bin/sh
./run_builder.sh
cp ./builder/out/test.x86-64.exe ./packer/test.x86-64.exe
cp ./builder/out/test.x86.exe ./packer/test.x86.exe

cd packer
rm ./out/*
DOCKER_BUILDKIT=1 docker build --target artifact --output type=local,dest=. .
cd ..