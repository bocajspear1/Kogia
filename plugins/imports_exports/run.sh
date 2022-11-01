#!/bin/sh

mkdir /tmp/out

python3 /opt/runner.py ${TMPDIR}/${SUBMITFILE} > /tmp/out/output.txt
