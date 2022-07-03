#!/bin/sh

ls -la ${TMPDIR}

file -b ${TMPDIR}/${SUBMITFILE} > /tmp/file-out.txt
file --mime-type -b ${TMPDIR}/${SUBMITFILE} >> /tmp/file-out.txt


readelf -W -h -l ${TMPDIR}/${SUBMITFILE} > /tmp/readelf-out.txt || true
readpe -h coff -h optional -d --format json ${TMPDIR}/${SUBMITFILE} > /tmp/readpe-out.json || true
