# Inventory Hunter

![Build](https://github.com/phikai/inventory-hunter/workflows/Build/badge.svg) ![Docker Pulls](https://img.shields.io/docker/pulls/phikai/inventory-hunter) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/phikai/inventory-hunter/latest)

This is a FORK of [EricJMarti/inventory-hunter](https://github.com/EricJMarti/inventory-hunter) which uses an alternative image which supports mentions on the Slack Alerter. Will be deprecated if https://github.com/EricJMarti/inventory-hunter/pull/164 is merged.

## Requirements

- Raspberry Pi 2 or newer (alternatively, you can use an always-on PC or Mac)
- [Docker](https://www.docker.com/) ([tutorial](https://phoenixnap.com/kb/docker-on-raspberry-pi))

You will also need one of the following:
- [Discord Webhook URL](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)
- [Slack Webhook URL](https://api.slack.com/messaging/webhooks)
- [Telegram Webhook URL and Chat ID](https://core.telegram.org/bots/api)
- [SMTP relay to send automated emails](https://medium.com/swlh/setting-up-gmail-and-other-email-on-a-raspberry-pi-6f7e3ad3d0e)

## Quick Start

For instructions specific to Windows, please see this guide instead: [Instructions for Windows](https://github.com/EricJMarti/inventory-hunter/wiki/Instructions-for-Windows)

These steps *should* work on any supported Docker platform, but they have been specifically tested on Raspberry Pi OS with Docker already installed.

1. Clone this repository and pull the latest image from [Docker Hub](https://hub.docker.com/r/ericjmarti/inventory-hunter):
    ```
    pi@raspberrypi:~
    $ git clone https://github.com/EricJMarti/inventory-hunter

    pi@raspberrypi:~
    $ cd inventory-hunter

    pi@raspberrypi:~/inventory-hunter
    $ docker pull ericjmarti/inventory-hunter:latest
    ```

2. Create your own configuration file based on one of the provided examples:

    - [Amazon RTX 3080 config](config/amazon_rtx_3080.yaml)
    - [Best Buy RTX 3060 Ti config](config/bestbuy_rtx_3060_ti.yaml)
    - [B&H Photo Video RTX 3070 config](config/bhphoto_rtx_3070.yaml)
    - [Micro Center RTX 3070 config](config/microcenter_rtx_3070.yaml)
    - [Newegg RTX 3070 config](config/newegg_rtx_3070.yaml)

3. Start the Docker container using the provided `docker_run.bash` script, specifying the required arguments.

    If using Discord or Slack, the format of your command will look like this:

    ```
    $ ./docker_run.bash -c <config_file> -a <discord_or_slack> -w <webhook_url>

    # Discord example:
    pi@raspberrypi:~/inventory-hunter
    $ ./docker_run.bash -c ./config/newegg_rtx_3070.yaml -a discord -w https://discord.com/api/webhooks/...
    ```

    If using an SMTP relay, the format of your command will look like this:

    ```
    $ ./docker_run.bash -c <config_file> -e <email_address> -r <relay_ip_address>

    # SMTP example:
    pi@raspberrypi:~/inventory-hunter
    $ ./docker_run.bash -c ./config/newegg_rtx_3070.yaml -e myemail@email.com -r 127.0.0.1
    ```

## Getting New Code

1. First identify any running container names related to inventory-hunter
    ```
    $ docker ps
    ```
2. Stop and remove all containers related to inventory-hunter
    ```
    $ docker stop CONTAINER_NAME
    $ docker rm CONTAINER_NAME
    ```
3. Pull repo updates
    ```
    $ git pull
    ```
4. Rerun the docker_run.bash command to start containers back up with updates.
    ```
    $ ./docker_run.bash -c <config_file> -a <discord_or_slack> -w <webhook_url>
    ```

## Configuring Alerters

If you are interested in configuring multiple alerters or would like to keep your alerter settings saved in a file, you can configure inventory-hunter's alerting mechanism using a config file similar to the existing scraper configs.

1. Create a file called alerters.yaml in the config directory.

2. Configure the alerters you would like to use based on this example:

    ```
    ---
    alerters:
      discord:
        webhook_url: https://discord.com/api/webhooks/XXXXXXXXXXXX...
        mentions:
          - XXXXXXXXXXXXXXX
          - XXXXXXXXXXXXXXX
      telegram:
        webhook_url: https://api.telegram.org/botXXXXXXXXXXXXXXXXXXXX/sendMessage
        chat_id: XXXXXXXX
      email:
        sender: myemail@email.com
        recipients:
          - myemail@email.com
          - myfriendsemail@email.com
        relay: 127.0.0.1
        password: XXXXXXXXXX   # optional
      slack:
        webhook_url: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
        mentions:
          - XXXXXXXXXXXXXXX
          - XXXXXXXXXXXXXXX
    ...
    ```

3. Add this config file to your run command:

    ```
    pi@raspberrypi:~/inventory-hunter
    $ ./docker_run.bash -c ./config/newegg_rtx_3070.yaml -q ./config/alerters.yaml
    ```

## How it works

The general idea is if you can get notified as soon as a product becomes in stock, you might have a chance to purchase it before scalpers clear out inventory. This script continually refreshes a set of URLs, looking for the "add to cart" phrase. Once detected, an automated alert is sent, giving you an opportunity to react.

## FAQ

### How is this different from existing online inventory trackers?

Before developing inventory-hunter, I used several existing services without any luck. By the time I received an alert, the product had already been scalped. This bot alerts faster than existing trackers for several reasons:

- it runs on your own hardware, so no processing time is spent servicing other users
- you get to choose which products you want to track
- you are in control of the refresh frequency

### What if inventory-hunter gets used by scalpers?

I sure hope this doesn't happen... 2020 is bad enough already. My hope is that inventory-hunter levels the playing field a bit by giving real customers a better opportunity than they had previously. Serious scalpers will continue using automated checkout bots, and it is up to online retailers to combat this malarkey.

### Do I really need Docker?

No, but I highly recommend it. If you know your way around python and pip/conda, then you should be able to replicate the environment I created using Docker.
