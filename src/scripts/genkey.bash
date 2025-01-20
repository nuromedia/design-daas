#!/bin/bash

usage() { 
    echo "Usage: $0 -n NAME [-b <bits>] [-d <dir>] [-v <days valid>] [-f] "; 
}

DIR_KEYS=data/keys
OPT_COUNTRY=DE
OPT_STATE=Berlin
OPT_LAND=Berlin
OPT_ORG=org
OPT_UNIT=S29
OPT_NAME=
KEYBITS=4096
DAYS_VALID=365
USE_FORCE=0

while getopts ":b:d:n:v:f" o; do
    case "$o" in
        b)
            KEYBITS=${OPTARG}
            ;;
        d)
            DIR_KEYS=${OPTARG}
            ;;
        n)
            OPT_NAME=${OPTARG}
            ;;
        f)
            USE_FORCE=1
            ;;
        v)
            DAYS_VALID=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

# Check args
if [[ ! -d "$DIR_KEYS" ]]; then
    usage
    echo "Path not valid"
    exit 1
fi
if [ "$OPT_NAME" = "" ]; then
    usage
    echo "Name is required"
    exit 2
fi
if [ -f "$DIR_KEYS/key.pem" ] || [ -f "$DIR_KEYS/cert.pem" ] ; then
    if [[ $USE_FORCE -eq 0 ]]; then
        echo "Key already exists. Use -f to enforce overwrite."
        exit 3
    fi
fi

# Params
SUB="/C=$OPT_COUNTRY/ST=$OPT_STATE/L=$OPT_LAND/O=$OPT_ORG/OU=$OPT_UNIT/CN=$OPT_NAME"
echo "### Params ##############################################################"
echo "Directory : $DIR_KEYS"
echo "Subject   : $SUB"
echo "Bits      : $KEYBITS"
echo "Valid     : $DAYS_VALID days"

# Create certs
echo "### GENERATE ############################################################"
mkdir -p "$DIR_KEYS"
ret=$(openssl req -x509 \
    -newkey rsa:"$KEYBITS" \
    -days "$DAYS_VALID" -nodes \
    -out "$DIR_KEYS"/cert.pem \
    -keyout "$DIR_KEYS"/key.pem \
    -subj "$SUB")
if [[ $ret -ne 0 ]] ; then
    echo "ERROR! Certificates not created!"
    exit 4
fi
echo "### OUTPUT ##############################################################"
openssl x509 -in "$DIR_KEYS/cert.pem" -text -noout
echo "#########################################################################"
exit 0
