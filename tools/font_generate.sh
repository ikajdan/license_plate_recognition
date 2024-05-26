#!/usr/bin/env bash

set -eu

FONT_NAME=${1:-"arklatrs.ttf"}
OUTPUT_DIR=${2:-"./characters"}
FONT_SIZE=${3:-"128"}
CHARSET=${4:-"ABCDEFGHIJKLMNOPRSTUVWXYZ0123456789"}

temp_dir=$(mktemp -d)
trap 'rm -r "${temp_dir}"' EXIT

if [ ! -f "${FONT_NAME}" ]; then
    echo "Font file not found: ${FONT_NAME}"
    exit 1
fi

if [ ! -d "./${OUTPUT_DIR}" ]; then
    mkdir "./${OUTPUT_DIR}"
fi

for char in $(echo $CHARSET | grep -o .); do
    FILE_NAME="${char}.png"
    echo "Generating ${FILE_NAME}"
    convert \
        -font "${FONT_NAME}" \
        -pointsize "${FONT_SIZE}" \
        label:"${char}" \
        "${temp_dir}/${FILE_NAME}"

    convert \
        "${temp_dir}/${FILE_NAME}" \
        -gravity East -chop 8x0 \
        -gravity South -chop 0x3 \
        -gravity West -chop 7x0 \
        "./${OUTPUT_DIR}/${FILE_NAME}"
done
