import argparse
import logging
import pathlib
import sys


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', type=argparse.FileType('r'), default='/config.yaml', help='YAML config file for web scrapers')
    parser.add_argument('-a', '--alerter', required=True, help="Alert system to be used", default="email", dest="alerter_type")
    parser.add_argument('-q', '--alerter-config', type=argparse.FileType('r'), help='YAML config file for alerters (required if using multiple)')
    parser.add_argument('-l', '--log', default='/log.txt', help='log file')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose logging')

    parser.add_argument('-e', '--email', nargs='+', help='recipient email address(es)')
    parser.add_argument('-r', '--relay', help='IP address of SMTP relay')

    # discord (or any other webhook based alerter) - related arguments
    parser.add_argument("-w", "--webhook", help="A valid HTTP url for a POST request.", dest="webhook_url")
    parser.add_argument("-i", "--chat-id", help="Telegram ID number for the chat room", dest="chat_id")

    return parser.parse_args()


# get version
version = 'v0.0.1'
version_path = pathlib.Path(__file__).resolve().parent / 'version.txt'
if version_path.is_file():
    with open(version_path, 'r') as f:
        version = f.read().strip()


# logging must be configured before the next few imports
args = parse_args()
log_format = '{levelname:.1s}{asctime} [{name}] {message}'
log_level = logging.DEBUG if args.verbose else logging.INFO
logging.basicConfig(level=log_level, format=log_format, style='{')
if args.log:
    logger = logging.getLogger()
    handler = logging.FileHandler(args.log)
    handler.setFormatter(logging.Formatter(log_format, style='{'))
    logger.addHandler(handler)
logging.info(f'starting {version} with args: {" ".join(sys.argv)}')


from alerter import init_alerters
from config import parse_config
from driver import init_drivers
from scraper import init_scrapers
from hunter import hunt


def main():
    try:
        alerters = init_alerters(args)
        config = parse_config(args.config)
        drivers = init_drivers(config)
        scrapers = init_scrapers(config, drivers)
        hunt(alerters, config, scrapers)
    except Exception:
        logging.exception('caught exception')
        sys.exit(1)


if __name__ == '__main__':
    main()
