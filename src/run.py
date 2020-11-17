import argparse
import logging
import sys

from config import parse_config
from hunter import hunt


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=argparse.FileType('r'), required=True, help='YAML config file')
    parser.add_argument('-e', '--email', required=True, help='recipient email address')
    parser.add_argument('-r', '--relay', required=True, help='IP address of SMTP relay')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose logging')
    return parser.parse_args()


def main():
    args = parse_args()
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='{levelname:.1s}{asctime} {message}', style='{')

    try:
        config = parse_config(args.config)
        hunt(args, config)
    except Exception as e:
        logging.exception('caught exception')
        sys.exit(1)


if __name__ == "__main__":
    main()
