#!/bin/sh
curl -XPOST -k -F submission=@${1} https://localhost:4000/api/v1/submission/new