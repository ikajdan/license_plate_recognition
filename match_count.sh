#!/usr/bin/env bash

set -eu

TRAIN_SET_DIR="train_set"
OUTPUT_FILE="output.json"

if [ -f "${OUTPUT_FILE}" ]; then
    rm "${OUTPUT_FILE}"
fi

python ./*.py ${TRAIN_SET_DIR} ${OUTPUT_FILE}

false_matches=0
while read -r key value; do
    key=$(echo "$key" | sed 's/.jpg//g')
    if [ "$key" != "$value" ]; then
        echo "Incorrect match: $key $value"
        false_matches=$((false_matches + 1))
    fi
done < <(jq -r 'to_entries[] | .key + " " + .value' "${OUTPUT_FILE}")

echo ""
echo "Total number of images: $(ls -1q "${TRAIN_SET_DIR}" | wc -l)"
echo "Total matches: $(jq length "${OUTPUT_FILE}")"
echo "False matches: "${false_matches}""
