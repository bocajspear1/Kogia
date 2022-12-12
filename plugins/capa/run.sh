#!/bin/sh
capa -j ${TMPDIR}/${SUBMITFILE} -q > /tmp/capa-output.json
capa ${TMPDIR}/${SUBMITFILE} -q -vv > /tmp/capa-output.txt &