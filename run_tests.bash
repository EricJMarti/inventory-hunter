#!/bin/bash

set -e

usage() {
    [ -n "$1" ] && echo "error: $1"
    echo
    echo "usage:"
    echo "  $0 [-i IMAGE]"
    echo
    exit 1
}

default_image="ericjmarti/inventory-hunter:latest"
image=$default_image

while getopts i: arg
do
    case "${arg}" in
        i) image=${OPTARG};;
    esac
done

if [ "$image" = "$default_image" ]; then
    docker pull "$image"
else
    result=$(docker images -q $image)
    if [ -z "$result" ]; then
        echo "the $image docker image does not exist... please build the image and try again"
        echo "build command: docker build -t $image ."
        usage
    fi
fi

script_dir=$(cd "$(dirname "$0")" && pwd -P)
tests_dir="$script_dir/tests"

volumes="-v $tests_dir:/src/tests"

docker_run_cmd="docker run --rm $volumes --entrypoint=pytest --workdir=/src $image"

echo "\$ $docker_run_cmd"
eval $docker_run_cmd
