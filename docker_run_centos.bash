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
network="inventory_hunter"

while getopts a:c:d:e:i:n:q:r:w:t arg
do
    case "${arg}" in
        a) alerter=${OPTARG};;
        c) config=${OPTARG};;
        d) chat_id=${OPTARG};;
        e) emails+=(${OPTARG});;
        i) image=${OPTARG};;
        n) network=${OPTARG};;
        q) alerter_config=${OPTARG};;
        r) relay=${OPTARG};;
        w) webhook=${OPTARG};;
        t) test_alert=1;;
    esac
done

[ -z "$config" ] && usage "missing config argument"
[ ! -f "$config" ] && usage "$config does not exist or is not a regular file"

if [ ! -z "$alerter_config" ]; then
    [ ! -f "$alerter_config" ] && usage "$alerter_config does not exist or is not a regular file"
elif [ "$alerter" = "email" ]; then
    [ -z "$emails" ] && usage "missing email argument"
    [ -z "$relay" ] && usage "missing relay argument"
else
    [ -z "$webhook" ] && usage "missing webhook argument"
    if [ "$alerter" = "telegram" ]; then
        [ -z "$chat_id" ] && usage "missing telegram chat id argument"
    fi
fi

if [ "$image" = "$default_image" ]; then
    docker pull "$image"
else
    result=$(docker images -q $image)
    if [ -z "$result" ]; then
        echo "the $image docker image does not exist... please build the image and try again"
        echo "build command: docker build -t $image ."
        exit 1
    fi
fi

# docker requires absolute paths
if [ "$(uname)" = "Darwin" ]; then
    if [[ ! "$config" == /* ]]; then
        config="$(pwd -P)/${config#./}"
    fi
    if [ ! -z "$alerter_config" ] && [[ ! "$alerter_config" == /* ]]; then
        alerter_config="$(pwd -P)/${alerter_config#./}"
    fi
else
    config=$(readlink -f $config)
    if [ ! -z "$alerter_config" ]; then
        alerter_config=$(readlink -f $alerter_config)
    fi
fi

script_dir=$(cd "$(dirname "$0")" && pwd -P)
log_dir="$script_dir/log"
mkdir -p $log_dir

container_name=$(basename $config .yaml)
data_dir="$script_dir/data/$container_name"
log_file="$log_dir/$container_name.txt"
mkdir -p $data_dir
touch $log_file

volumes="-v $data_dir:/data:z -v $log_file:/log.txt:z -v $config:/config.yaml:z"
[ ! -z "$alerter_config" ] && volumes="$volumes -v $alerter_config:/alerters.yaml"

(docker network inspect $network &> /dev/null) || docker network create $network

entrypoint="--entrypoint=/src/run.bash"

docker_run_cmd="docker run -d --rm $entrypoint --name $container_name --network $network $volumes $image --alerter $alerter"

if [ ! -z "$alerter_config" ]; then
    docker_run_cmd="$docker_run_cmd --alerter-config /alerters.yaml"
elif [ "$alerter" = "email" ]; then
    docker_run_cmd="$docker_run_cmd --email ${emails[@]} --relay $relay"
else
    docker_run_cmd="$docker_run_cmd --webhook $webhook"
    if [ "$alerter" = "telegram" ]; then
        docker_run_cmd="$docker_run_cmd --chat-id $chat_id"
    fi
fi
if [ $test_alert ]; then
    docker_run_cmd="$docker_run_cmd -t"
fi
docker_ps_cmd="docker ps -a -f name=$container_name"

echo "\$ $docker_run_cmd"
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
