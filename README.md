# Inventory Hunter

![Build](https://github.com/EricJMarti/inventory-hunter/workflows/Build/badge.svg) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/ericjmarti/inventory-hunter/latest)

This bot helped me snag an RTX 3070... hopefully it will help you get your hands on your next CPU, GPU, or game console.

## Requirements

- Raspberry Pi (alternatively, you can use an always-on PC)
- [Docker](https://www.docker.com/) ([tutorial](https://phoenixnap.com/kb/docker-on-raspberry-pi))

You will also need one of the following:
- [Discord Webhook URL](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)
- [Slack Webhook URL](https://api.slack.com/messaging/webhooks)
- [SMTP relay to send automated emails](https://medium.com/swlh/setting-up-gmail-and-other-email-on-a-raspberry-pi-6f7e3ad3d0e)

## Quick Start

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
