#!/bin/bash


# Parse args
TEST_ITER=1
SLEEP_BETWEEN=20
TEST_DOMAIN=http://localhost:4444
DIR_RESULTS="data/results"
URLLIST=()
PROC=firefox-esr

while getopts ":i:u:d:o:s:" o; do
    case "$o" in
        i)
            TEST_ITER=${OPTARG}
            ;;
        d)
            TEST_DOMAIN=${OPTARG}
            ;;
        u)
            URLLIST+=("$OPTARG")
            ;;
        s)
            SLEEP_BETWEEN=${OPTARG}
            ;;
        o)
            DIR_RESULTS=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

for URL in "${URLLIST[@]}"; do
    echo "-- Testing $URL"
    "$PROC" -new-instance "$TEST_DOMAIN/testbrowser/$TEST_ITER/$URL"
    sleep "$SLEEP_BETWEEN"
done
mkdir -p "$DIR_RESULTS"
mv ~/Downloads/firefox-*.csv "$DIR_RESULTS"

