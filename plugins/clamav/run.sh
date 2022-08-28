#!/bin/ash

mkdir /tmp/out

mkdir /tmp2

clamscan -v --log=/tmp/out/clamav.log --tempdir /tmp2 ${TMPDIR}/${SUBMITFILE}
