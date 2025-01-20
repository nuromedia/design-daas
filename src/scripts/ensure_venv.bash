#!/bin/bash

# Usage
usage() { 
    echo "Usage: $0 [-d <directory>] [-p "PACKAGE1 PACKAGE2 PACKAGEN"]";
}

# Parse args
DIR_VENV=.venv
while getopts ":d p:" o; do
    case "$o" in
        d)
            DIR_VENV=${OPTARG}
            ;;
        p)
            PACKAGES=("${OPTARG[@]}")
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

# Check args
if [ "$DIR_VENV" = "" ]; then
    usage
    echo "Path not valid"
    exit 1
fi

# Create venv
if [[ ! -d "$DIR_VENV" ]]; then
    echo "Creating virtual environment..."
    python3 -m venv "$DIR_VENV"
fi
source "$DIR_VENV/bin/activate"

# Install packages
if [[ "${PACKAGES[*]}" != "" ]]; then
    bash -c "pip install ${PACKAGES[*]}"
fi

exit 0
