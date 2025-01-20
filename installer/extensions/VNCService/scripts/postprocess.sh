#!/bin/sh

SERVER_URL="http://localhost:8010/api/vnc/file"

# Cut only relevant part of the path
MESSAGE=$(echo "$1" | sed 's|.*/files||')

# Send response
response=$(curl -s -X POST -H "Content-Type: application/json" -d "{\"message\": \"$1\"}" "$SERVER_URL")

echo "Response from server: $response"