#!/bin/bash

while true; do
    echo "starting: $@"
    eval $@
    sleep 60
done
