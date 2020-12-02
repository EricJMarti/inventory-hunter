#!/bin/bash

set -e

usage() {
    [ -n "$1" ] && echo "error: $1"
    echo "usage: $0 -c CONFIG -e EMAIL -r RELAY"
    exit 1
}

[ $# -eq 0 ] && usage

alerter="email"
while getopts a:c:e:r:w: arg
do
    case "${arg}" in
        a) alerter=${OPTARG};;
        c) config=${OPTARG};;
        e) emails+=(${OPTARG});;
        r) relay=${OPTARG};;
        w) webhook=${OPTARG};;
    esac
done

[ -z "$config" ] && usage "missing config argument"
[ ! -f "$config" ] && usage "$config does not exist or is not a regular file"

if [ "$alerter" = "email" ]; then
    [ -z "$emails" ] && usage "missing email argument"
    [ -z "$relay" ] && usage "missing relay argument"
else
    [ -z "$webhook" ] && usage "missing webhook argument"
fi

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

container_name=$(basename $config .yaml)

docker_run_cmd="docker run -d --name $container_name --network host -v $config:/config.yaml $image --alerter $alerter"

if [ "$alerter" = "email" ]; then
    docker_run_cmd="$docker_run_cmd --email ${emails[@]} --relay $relay"
else
    docker_run_cmd="$docker_run_cmd --webhook $webhook"
fi

docker_ps_cmd="docker ps -a -f name=$container_name"

# echo "\$ $docker_run_cmd"
eval $docker_run_cmd
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
