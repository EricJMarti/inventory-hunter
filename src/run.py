import argparse
import locale
import logging
import pathlib
import sys


# required for price parsing logic
locale.setlocale(locale.LC_ALL, '')

# get version
version = 'v0.0.1'
version_path = pathlib.Path(__file__).resolve().parent / 'version.txt'
if version_path.is_file():
    with open(version_path, 'r') as f:
        version = f.read().strip()

# logging must be configured before the next few imports
logging.basicConfig(level=logging.DEBUG, format='{levelname:.1s}{asctime} [{name}] {message}', style='{')
logging.debug(f'starting {version} with args: {" ".join(sys.argv)}')


from config import parse_config
from driver import init_drivers
from scraper import init_scrapers
from hunter import hunt


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', type=argparse.FileType('r'), default='/config.yaml', help='YAML config file')
    parser.add_argument('-a', '--alerter', required=True, help="Alert system to be used", default="email", dest="alerter_type")
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose logging')

    parser.add_argument('-e', '--email', nargs='+', help='recipient email address(es)')
    parser.add_argument('-r', '--relay', help='IP address of SMTP relay')

    # discord (or any other webhook based alerter) - related arguments
    parser.add_argument("-w", "--webhook", help="A valid HTTP url for a POST request.", dest="webhook_url")
    parser.add_argument("-i", "--chat-id", help="Telegram ID number for the chat room", dest="chat_id")
    return parser.parse_args()


def main():
    args = parse_args()
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else logging.INFO)

    try:
        config = parse_config(args.config)
        drivers = init_drivers(config)
        scrapers = init_scrapers(config, drivers)
        hunt(args, config, scrapers)
    except Exception:
        logging.exception('caught exception')
        sys.exit(1)


if __name__ == '__main__':
    main()
