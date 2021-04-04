#!/bin/bash

# If this looks stupid, that's because it is.
# The issue is that Chromium often gets orphaned by selenium/chromedriver.
# This script runs as PID 1 (Docker entrypoint) to ensure these zombie processes get cleaned up.

CHILD_PID=0

handle_signal() {
    echo "caught signal, shutting down"
    if [[ $CHILD_PID != 0 ]]; then
        kill $CHILD_PID
        wait $CHILD_PID
    fi
    exit
}

trap handle_signal SIGHUP SIGINT SIGTERM

echo "starting: $@"
eval $@ &
CHILD_PID=$!
wait $CHILD_PID
