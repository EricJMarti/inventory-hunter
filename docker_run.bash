#!/bin/bash

set -e

usage() {
    [ -n "$1" ] && echo "error: $1"
    echo "usage: $0 -c CONFIG -e EMAIL -r RELAY"
    exit 1
}

[ $# -eq 0 ] && usage

while getopts c:e:r: arg
do
    case "${arg}" in
        c) config=${OPTARG};;
        e) email=${OPTARG};;
        r) relay=${OPTARG};;
    esac
done

[ -z "$config" ] && usage "missing config argument"
[ -z "$email" ] && usage "missing email argument"
[ -z "$relay" ] && usage "missing relay argument"

[ ! -f "$config" ] && usage "$config does not exist or is not a regular file"

# docker requires absolute paths
config=$(readlink -f $config)

docker run -d \
    --network host \
    -v $config:/config.yaml \
    inventory-hunter \
    --email $email \
    --relay $relay
