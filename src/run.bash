#!/bin/bash

# export DISPLAY=:0

# Xvfb $DISPLAY -screen 0 1920x1080x24+32 &

/src/worker/watchdog.bash python /src/run_worker.py lean_and_mean &

python /src/run.py $@
