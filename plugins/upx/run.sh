#!/bin/sh

mkdir /tmp/out

upx -d ${TMPDIR}/${SUBMITFILE}  -o /tmp/out/unpacked_${SUBMITFILE}
