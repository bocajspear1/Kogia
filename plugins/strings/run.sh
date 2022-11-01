#!/bin/sh

mkdir /tmp/out

strings -n ${CHAR_COUNT} ${TMPDIR}/${SUBMITFILE} > /tmp/out/strings.txt
strings -n ${CHAR_COUNT}-el ${TMPDIR}/${SUBMITFILE} > /tmp/out/strings-utf16.txt
strings -n ${CHAR_COUNT}-eL ${TMPDIR}/${SUBMITFILE} > /tmp/out/strings-utf32.txt
