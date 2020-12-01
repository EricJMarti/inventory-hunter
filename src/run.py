import argparse
import locale
import logging
import sys


# required for price parsing logic
locale.setlocale(locale.LC_ALL, '')

# logging must be configured before the next few imports
logging.basicConfig(level=logging.DEBUG, format='{levelname:.1s}{asctime} {message}', style='{')
logging.debug(f'starting with args: {" ".join(sys.argv)}')


from config import parse_config
from driver import init_driver
from hunter import hunt


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=argparse.FileType('r'), default='/config.yaml', help='YAML config file')
    parser.add_argument('-e', '--email', nargs='+', help='recipient email address(es)')
    parser.add_argument('-r', '--relay', required=True, help='IP address of SMTP relay')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose logging')
    return parser.parse_args()


def main():
    args = parse_args()
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else logging.INFO)

    try:
        config = parse_config(args.config)
        driver = init_driver(config)
        hunt(args, config, driver)
    except Exception:
        logging.exception('caught exception')
        sys.exit(1)


if __name__ == '__main__':
    main()
