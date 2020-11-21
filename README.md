# Inventory Hunter

This bot helped me snag an RTX 3070... hopefully it will help you get your hands on your next CPU or GPU.

## Requirements

- Raspberry Pi (alternatively, you can use an always-on PC)
- [Docker](https://www.docker.com/) ([tutorial](https://phoenixnap.com/kb/docker-on-raspberry-pi))
- SMTP relay to send automated emails ([tutorial](https://medium.com/swlh/setting-up-gmail-and-other-email-on-a-raspberry-pi-6f7e3ad3d0e))

## Quick Start

These steps *should* work on any supported Docker platform, but they have been specifically tested on Raspberry Pi OS with Docker already installed.

1. Clone this repository and build a Docker image using the provided [Dockerfile](Dockerfile):
```
$ git clone https://github.com/EricJMarti/inventory-hunter.git
$ cd inventory-hunter
$ docker build -t inventory-hunter .
```

Note: The `docker build` command may take a while to complete. 

2. Create your own configuration file based on one of the provided examples:
- [Newegg RTX 3070 config](config/newegg_rtx_3070.yaml)
- [B&H Photo Video RTX 3070 config](config/bhphoto_rtx_3070.yaml)
- [Micro Center RTX 3070 config](config/microcenter_rtx_3070.yaml)

3. Start the Docker container, specifying the required arguments. See example `docker run` command in [docker_run.bash](docker_run.bash) or run:
```
$ ./docker_run.bash -c <config_file> -e <email_address> -r <relay_ip_address>
```

## How it works

The general idea is if you can get notified as soon as a product becomes in stock, you might have a chance to purchase it before scalpers clear out inventory. This script continually refreshes a set of URLs, looking for the "add to cart" phrase. Once detected, an automated email is sent, giving you an opportunity to react.

## FAQ

### How is this different from existing online inventory trackers?

Before developing inventory-hunter, I used several existing services without any luck. By the time I received an alert, the product had already been scalped. This bot alerts faster than existing trackers for several reasons:
- it runs on your own hardware, so no processing time is spent servicing other users
- you get to choose which products you want to track
- you are in control of the refresh frequency

### What if inventory-hunter gets used by scalpers?

I sure hope this doesn't happen... 2020 is bad enough already. My hope is that inventory-hunter levels the playing field a bit by giving real customers a better opportunity than they had previously. Serious scalpers will continue using automated checkout bots, and it is up to online retailers to combat this malarkey.

### Do I really need Docker?

No (but YMMV). If you know your way around python and pip/conda, then you should be able to replicate the environment I created using Docker.
