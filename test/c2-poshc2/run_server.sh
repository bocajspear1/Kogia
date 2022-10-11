#!/bin/bash

posh-server 2>&1 >output1.log &
SERVER_PID=$!; 
DONE=0; 
while [ "$DONE" -eq "0" ]; do 
    sleep 5; 
    if grep -q "Server Started" "output1.log"; then 
        kill $SERVER_PID; 
        DONE=1; 
    fi; 
done;
