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

image="inventory-hunter"

retcode=0
(docker image inspect $image &> /dev/null) || retcode=1

if [ $retcode -ne 0 ]; then
    echo "the $image docker image does not exist... please build the image and try again"
    echo "build command: docker build -t $image ."
    exit 1
fi

# docker requires absolute paths
config=$(readlink -f $config)

docker run -d \
    --network host \
    -v $config:/config.yaml \
    $image \
    --email $email \
    --relay $relay
