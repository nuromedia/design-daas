
AMOUNT=10
URL="http://localhost:4444/baseline2"
RESULT_FILE=results.csv
TMP_FILE=para.tmp
TOKEN_FILE="access_token.json"
OBJID="vmDeb12"

# Parse args
while getopts ":c:u:o:t:" o; do
    case "$o" in
        c)
            AMOUNT=${OPTARG}
            ;;
        u)
            URL=${OPTARG}
            ;;
        o)
            RESULT_FILE=${OPTARG}
            ;;
        t)
            TOKEN_FILE=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))
rm -rf "$TMP_FILE" > /dev/null
rm -rf "$RESULT_FILE" > /dev/null
TS_GLOBAL=$(date +%s%3N)
if [ ! -f "$TOKEN_FILE" ] ; then 
    echo "Not token present"
    exit 1
fi

function testrun() {
    counter=$1
    timestamp1=$(date +%s%3N)
    token=$(cat "$TOKEN_FILE")
    response=$(curl -k -s -X "POST" \
        -H "Authorization: Bearer $token" \
        -H "accept: application/json" \
        --data-urlencode "id=$OBJID" \
        --data-urlencode "counter=$counter" \
        --data-urlencode "timestamp=$timestamp1" \
        "$URL")
    
    echo "$counter" >> "$TMP_FILE"
    timestamp2=$(date +%s%3N)
    diff=$((timestamp2 - timestamp1))
    rps=$((1000 / diff))
    reqend=$(echo "$response" | jq -r '.timings.request.end')
    if [ "$reqend" -eq 0 ]; then
        delay=0
    else
        delay=$((timestamp2 - reqend))
    fi
    # echo -n "$counter" >>"$RESULT_FILE"
    echo "$response" | jq -r \
        --arg tsbegin "$timestamp1" \
        --arg tsend "$timestamp2" \
        --arg tsdiff "$diff" \
        --arg tsdelay "$delay" \
        --arg rps "$rps" \
        '
        [
            .http_params_form.counter,
            $tsbegin,
            $tsend,
            $rps,
            $tsdiff,
            .timings.request_delay,
            $tsdelay,
            .timings.context.diff,
            .timings.processing.diff,
            .timings.authentication.diff
        ]
        | @csv
        | gsub("\""; "")
    ' >> "$RESULT_FILE"
}

export -f testrun
export URL
export RESULT_FILE
export TMP_FILE
export TS_GLOBAL
export TOKEN_FILE
export OBJID

# Run testrun function in parallel
echo "CNT,TS_BEGIN,TS_END,RPS,DIFF,DELAY_CLI,DELAY_BCK,CTXTIME,PROCTIME,AUTHTIME" > "$RESULT_FILE"
echo "" > "$TMP_FILE"
seq 0 "$AMOUNT" | parallel -j "$AMOUNT" testrun 

# Create results
echo -n "-- $RESULT_FILE -> "
awk -F, '
{
    sum4+=$4; sum5+=$5; sum6+=$6; sum7+=$7; sum8+=$8; sum9+=$9; sum10+=$10; count++
}
END {
    printf "RPS: %7.2f R/S ", sum4/(count-1)
    printf "RTT: %7.2f ms ", sum5/(count-1)
    printf "OWD-CLI: %7.2f ms ", sum6/(count-1)
    printf "OWD-BCK: %7.2f ms ", sum7/(count-1)
    printf "RTT-Ctx: %7.2f ms ", sum8/(count-1)
    printf "RTT-Proc: %7.2f ms ", sum9/(count-1)
    printf "RTT-Auth: %7.2f ms\n", sum10/(count-1)
}' "$RESULT_FILE"
rm -rf "$TMP_FILE" > /dev/null
