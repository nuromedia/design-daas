#/bin/bash


ORGUNIT=pve
CNAME=pve.cluster.local

# help message
usage() { echo "Usage: $0 [-o <org-unit> -c <common-name>]" 1>&2; exit 1; }

# Read options
ORGUNIT=pve
CNAME=pve.cluster.local
while getopts ":o:c:" o; do
    case "${o}" in
        o)
            ORGUNIT=${OPTARG}
            ;;
        c)
            CNAME=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

CERTOPTS="/C=DE/ST=HE/L=FFM/O=PVE/OU=$ORGUNIT/CN=$CNAME"
KEYOUT=/etc/nginx/ssl/selfsigned.key
CRTOUT=/etc/nginx/ssl/selfsigned.crt

echo "CERT-Options: $CERTOPTS"
if [[ ! -f /etc/nginx/ssl/selfsigned.crt ]] ; then
    echo "Generate key and certificate"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$KEYOUT" -out "$CRTOUT" -subj "$CERTOPTS"
else
    echo "Certificate already present. Skipping generation of a new one..."
fi


