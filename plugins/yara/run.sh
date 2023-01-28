#!/bin/ash

mkdir /tmp/out/


python3 /opt/runner.py ${TMPDIR}/${SUBMITFILE} /tmp/out/yara-malpedia.txt

yara -m /opt/combined/malpedia.yar \
     ${TMPDIR}/${SUBMITFILE} > /tmp/out/yara-malpedia.txt

yara -m /opt/combined/bartblaze.yar \
     /opt/combined/eset.yar \
     /opt/combined/capev2.yar \
     ${TMPDIR}/${SUBMITFILE} > /tmp/out/yara-out.txt