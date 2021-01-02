#!/bin/bash

set -e

usage() {
    [ -n "$1" ] && echo "error: $1"
    echo
    echo "usage for discord, slack, or telegram:"
    echo "  $0 -a DISCORD|SLACK|TELEGRAM -w WEBHOOK_URL [-d TELEGRAM_CHAT_ID] -c CONFIG"
    echo
    echo "usage for pushover:"
    echo "  $0 -a PUSHOVER -u USER_KEY -t ACCESS_TOKEN -c CONFIG" 
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

while getopts a:c:d:e:i:q:r:u:t:w: arg
do
    case "${arg}" in
        a) alerter=${OPTARG};;
        c) config=${OPTARG};;
        d) chat_id=${OPTARG};;
        e) emails+=(${OPTARG});;
        i) image=${OPTARG};;
        q) alerter_config=${OPTARG};;
        r) relay=${OPTARG};;
        u) user_key=${OPTARG};;
        t) access_token=${OPTARG};;
        w) webhook=${OPTARG};;
    esac
done

[ -z "$config" ] && usage "missing config argument"
[ ! -f "$config" ] && usage "$config does not exist or is not a regular file"

if [ ! -z "$alerter_config" ]; then
    [ ! -f "$alerter_config" ] && usage "$alerter_config does not exist or is not a regular file"
elif [ "$alerter" = "email" ]; then
    [ -z "$emails" ] && usage "missing email argument"
    [ -z "$relay" ] && usage "missing relay argument"
elif [ "$alerter" = "pushover" ]; then
    [ -z "$user_key" ] && usage "missing user key argument"
    [ -z "$access_token" ] && usage "missing access token argument"
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

volumes="-v $data_dir:/data -v $log_file:/log.txt -v $config:/config.yaml"
[ ! -z "$alerter_config" ] && volumes="$volumes -v $alerter_config:/alerters.yaml"

docker_run_cmd="docker run -d --rm --name $container_name --network host $volumes $image --alerter $alerter"

if [ ! -z "$alerter_config" ]; then
    docker_run_cmd="$docker_run_cmd --alerter-config /alerters.yaml"
elif [ "$alerter" = "email" ]; then
    docker_run_cmd="$docker_run_cmd --email ${emails[@]} --relay $relay"
elif [ "$alerter" = "pushover" ]; then
    docker_run_cmd="$docker_run_cmd --user-key $user_key --access-token $access_token"
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
