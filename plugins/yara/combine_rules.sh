#!/bin/sh

DIR=$1
OUT=$2
NAME=$(basename $OUT .yar)

find ${DIR} -type f -name "*.yar" -exec cat "{}" >> ${OUT} \;

sed -i "s/^rule /rule ${NAME}_/g" ${OUT}