#!/bin/bash

SLEEP=0
DOMAIN=https://pve1.cluster.local


make TEST_ITER=1 TEST_DOMAIN="$DOMAIN" TEST_NAME="nightly-1" TEST_SLEEP="$SLEEP" clean tests-curl tests-firefox plots

# Stepsize 10 from 10 to 100
for i in {10..100..10}; do
    NAME="nighgtly-$i"
    make TEST_ITER="$i" \
        TEST_DOMAIN="$DOMAIN" \
        TEST_NAME="$NAME" \
        TEST_SLEEP="$SLEEP" \
        tests-curl \
        tests-firefox \
        plots
done

ITER=200
NAME="nighgtly-$ITER"
make TEST_ITER="$ITER" TEST_DOMAIN="$DOMAIN" TEST_NAME="$NAME" TEST_SLEEP="$SLEEP" clean tests-firefox plots

ITER=300
NAME="nighgtly-$ITER"
make TEST_ITER="$ITER" TEST_DOMAIN="$DOMAIN" TEST_NAME="$NAME" TEST_SLEEP="$SLEEP" clean tests-firefox plots

