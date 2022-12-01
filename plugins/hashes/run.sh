#!/bin/ash

mkdir /tmp/out

pehash -f json ${TMPDIR}/${SUBMITFILE} > /tmp/out/hashes.json
md5sum ${TMPDIR}/${SUBMITFILE} > /tmp/out/hashes.txt
sha1sum ${TMPDIR}/${SUBMITFILE} >> /tmp/out/hashes.txt
sha256sum ${TMPDIR}/${SUBMITFILE} >> /tmp/out/hashes.txt
