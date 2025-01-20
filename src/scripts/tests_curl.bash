#!/bin/bash


# Parse args
ITER=1
SLEEP_BETWEEN=20
DOMAIN=https://localhost:5000
OUTDIR="data/results/csv"
URLLIST=()
USERNAME='johannes.bouche@fb2.fra-uas.de'
# USERNAME='ownertest@example.com'
# USERNAME='perfuser@example.com'
PASSWORD="Design.2024"
CLIENTID="test-client"
SCOPE="admin"
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

echo "DOMAIN $DOMAIN"
function testSync() {
    ./scripts/tests_curl_sync.bash \
        -c "$1" \
        -u "$DOMAIN/$3" \
        -t "$4/access_token".json \
        -o "$4/$2-$1-$3".csv
}
function testAsync() {
    ./scripts/tests_curl_async.bash \
        -c "$1" \
        -u "$DOMAIN/$3" \
        -o "$4/$2-$1-$3".csv \
        -t "$4/access_token".json \
        -t "$4/access_token".json

}
function create_token() {
    #Get token
    echo "Generate-Token:"
    curl -X POST \
        --silent \
        --insecure \
        --data-urlencode "username=$USERNAME" \
        --data-urlencode "password=$PASSWORD" \
        -d "client_id=$CLIENTID" \
        -d "scope=$SCOPE" \
        -d "grant_type=$GRANTTYPE" \
        "$URL"/oauth2/user/token > "$OUTDIR/token.json"
    cat "$OUTDIR/token.json" | jq .access_token | tr -d '"' > "$OUTDIR/access_token.json"
}
ulimit -n "$(ulimit -Hn)"
mkdir -p "$OUTDIR"
rm -rf "$OUTDIR/token.json"
rm -rf "$OUTDIR/access_token.json"
create_token
echo "Testing with token:"
cat "$OUTDIR/access_token.json"
echo ""
echo "Testing domain: $URL"

for URL in "${URLLIST[@]}"; do
    testSync "$ITER" "curl-sequence" "$URL" "$OUTDIR"
    sleep "$SLEEP_BETWEEN"
    testAsync "$ITER" "curl-parallel" "$URL" "$OUTDIR"
    sleep "$SLEEP_BETWEEN"
done
rm -rf "$OUTDIR/token.json"
rm -rf "$OUTDIR/access_token.json"
