#!/bin/bash

set -e

usage() {
    [ -n "$1" ] && echo "error: $1"
    echo
    echo "usage for discord, slack, or telegram:"
    echo "  $0 -a DISCORD|SLACK|TELEGRAM -w WEBHOOK_URL [-d TELEGRAM_CHAT_ID] -c CONFIG"
    echo
    echo "usage for email:"
    echo "  $0 -c CONFIG -e EMAIL -r RELAY"
    echo
    exit 1
}

[ $# -eq 0 ] && usage

alerter="email"
default_image="ericjmarti/inventory-hunter:latest"
image=$default_image

while getopts a:c:d:e:i:r:w: arg
do
    case "${arg}" in
        a) alerter=${OPTARG};;
        c) config=${OPTARG};;
        d) chat_id=${OPTARG};;
        e) emails+=(${OPTARG});;
        i) image=${OPTARG};;
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
    if [ "$alerter" = "telegram" ]; then
        [ -z "$chat_id" ] && usage "missing telegram chat id argument"
    fi
fi

retcode=0
[ "$image" = "$default_image" ] || (docker image inspect $image &> /dev/null) || retcode=1

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

docker_run_cmd="docker run -d -rm --name $container_name --network host -v $config:/config.yaml $image --alerter $alerter"

if [ "$alerter" = "email" ]; then
    docker_run_cmd="$docker_run_cmd --email ${emails[@]} --relay $relay"
else
    docker_run_cmd="$docker_run_cmd --webhook $webhook"
    if [ "$alerter" = "telegram" ]; then
        docker_run_cmd="$docker_run_cmd --chat-id $chat_id"
    fi
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
