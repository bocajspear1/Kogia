#!/bin/sh

cp ${TMPDIR}/${SUBMITFILE} /tmp/input.md
cd /opt

unset TMPDIR

pandoc /tmp/input.md  -f markdown -o /tmp/output.pdf --template eisvogel --filter pandoc-latex-environment --listings

