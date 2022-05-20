#!/bin/sh

EXTRA_ARGS=""

mkdir /tmp/out

if [[ ${SUBMITFILE} == *zip ]]; then
    if 7z l -slt ${TMPDIR}/${SUBMITFILE} | grep -v "Encrypted = +"; then
        EXTRA_ARGS='-pinfected '
    fi
    7za x ${TMPDIR}/${SUBMITFILE} -tzip ${EXTRA_ARGS} -o/tmp/out
fi

chmod -R 444 /tmp/out/*

ls -la /tmp/out/*