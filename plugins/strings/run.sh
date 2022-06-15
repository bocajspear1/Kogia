#!/bin/sh

mkdir /tmp/out

strings ${TMPDIR}/${SUBMITFILE} > /tmp/out/strings.txt
strings -el ${TMPDIR}/${SUBMITFILE} > /tmp/out/strings-utf16.txt
strings -eL ${TMPDIR}/${SUBMITFILE} > /tmp/out/strings-utf32.txt
