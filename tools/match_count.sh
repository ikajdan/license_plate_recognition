#!/usr/bin/env bash

set -eu

TRAIN_SET_DIR="./train_set"
OUTPUT_FILE="./output.json"

if [ -f "${OUTPUT_FILE}" ]; then
    rm "${OUTPUT_FILE}"
fi

if [ $(ls -1 *.py 2>/dev/null | wc -l) -ne 1 ]; then
    echo "There should be exactly one .py file in the current directory"
    exit 1
fi

python *.py ${TRAIN_SET_DIR} ${OUTPUT_FILE}

total_points=0
possible_points=0

while read -r key value; do
    key="${key%.jpg}" # Remove the .jpg extension from the key
    match_points=0

    for (( i=0; i<${#key}; i++ )); do
        possible_points=$((possible_points + 1))
        if [ "${key:i:1}" == "${value:i:1}" ]; then
            match_points=$((match_points + 1))
        fi
    done

    possible_points=$((possible_points + 3))
    if [ $match_points -eq ${#key} ]; then
        match_points=$((match_points + 3))
    fi

    echo "Match: $key $value | Points: $match_points"
    total_points=$((total_points + match_points))
done < <(jq -r 'to_entries[] | .key + " " + .value' "${OUTPUT_FILE}")

total_images=$(find "${TRAIN_SET_DIR}" -type f -name '*.jpg' | wc -l)
total_matches=$(jq length "${OUTPUT_FILE}")

echo ""
echo "License plates detected: ${total_matches}/${total_images}"
echo "Total points: ${total_points}/${possible_points}"
