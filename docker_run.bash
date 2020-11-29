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
        e) emails+=(${OPTARG});;
        r) relay=${OPTARG};;
    esac
done

[ -z "$config" ] && usage "missing config argument"
[ -z "$emails" ] && usage "missing email argument"
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
if [ "$(uname)" = "Darwin" ]; then
    if [[ ! "$config" == /* ]]; then
        config="$(pwd -P)/${config#./}"
    fi
else
    config=$(readlink -f $config)
fi

container_name=$(basename $config)
container_name=${container_name%.yaml}

docker run -d \
    --name $container_name \
    --network host \
    -v $config:/config.yaml \
    $image \
    --email ${emails[@]} \
    --relay $relay

docker_ps_cmd="docker ps -a -f name=$container_name"

echo
echo "started docker container named $container_name"
echo
echo "view the status of this container using the following command:"
echo "\$ $docker_ps_cmd"
echo
eval $docker_ps_cmd
echo
echo "view logs for this container using the following command:"
echo "\$ docker logs -f $container_name"
echo
