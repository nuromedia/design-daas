#!/bin/bash


# Parse args
ITER=1
SLEEP_BETWEEN=20
DOMAIN=https://localhost:5000
OUTDIR="data/results/csv"
URLLIST=()
USERNAME="testuser123@example.com"
PASSWORD="Design.2024"
CLIENTID="test-client"
SCOPE="user"
GRANTTYPE="password"
URL="https://backend.application.daas-design.de"
while getopts ":i:u:d:o:s:" o; do
    case "$o" in
        i)
            ITER=${OPTARG}
            ;;
        d)
            DOMAIN=${OPTARG}
            ;;
        u)
            URLLIST+=("$OPTARG")
            ;;
        s)
            SLEEP_BETWEEN=${OPTARG}
            ;;
        o)
            OUTDIR=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

function create_token() {
    counter=$1
    echo "$counter"

    #Get token
    curl -X POST \
        --silent \
        --insecure \
        --data-urlencode "username=$USERNAME" \
        --data-urlencode "password=$PASSWORD" \
        -d "client_id=$CLIENTID" \
        -d "scope=$SCOPE" \
        -d "grant_type=$GRANTTYPE" \
        "$URL"/oauth2/user/token > "$OUTDIR/token$counter.json"
    # cat "$OUTDIR/token.json" | jq .access_token | tr -d '"' > "$OUTDIR/access_token.json"
    cat "$OUTDIR/token$counter.json"
}
ulimit -n "$(ulimit -Hn)"
mkdir -p "$OUTDIR"
rm -rf "$OUTDIR/token.json"
rm -rf "$OUTDIR/access_token.json"

# for item in {1..100} ; do
#     create_token
#     echo "$item"
# done
export -f create_token
export URL
export USERNAME
export PASSWORD
export CLIENTID
export SCOPE
export SCOPE
export GRANTTYPE
export OUTDIR
timestamp1=$(date +%s%3N)

AMOUNT=1000
seq 0 "$AMOUNT" | parallel -j "$AMOUNT" create_token
timestamp2=$(date +%s%3N)
diff=$((timestamp2 - timestamp1))
printf "\nSending %s requests finished in %d ms" "$AMOUNT" "$diff"

rm -rf "$OUTDIR/token.json"
rm -rf "$OUTDIR/access_token.json"
