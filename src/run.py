import argparse
import locale
import logging
import sys

from config import parse_config
from driver import init_driver
from hunter import hunt


# required for price parsing logic
locale.setlocale(locale.LC_ALL, '')


def parse_args():
    parser = argparse.ArgumentParser()



    parser.add_argument('-c', '--config', type=argparse.FileType('r'), default='/config.yaml', help='YAML config file')
    parser.add_argument('-a', '--alerter', required=True, help="Alert system to be used", default="email", dest="alerter_type")
    
    parser.add_argument('-e', '--email', nargs='+', help='recipient email address(es)')
    parser.add_argument('-r', '--relay', help='IP address of SMTP relay')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose logging')
    
    
    # discord (or any other webhook based alerter) - related arguments
    parser.add_argument("-w", "--webhook", help="A valid HTTP url for a POST request.", dest="webhook_url")
    return parser.parse_args()
    


def main():
    args = parse_args()
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='{levelname:.1s}{asctime} {message}', style='{')

    try:
        config = parse_config(args.config)
        driver = init_driver(config)
        hunt(args, config, driver)
    except Exception:
        logging.exception('caught exception')
        sys.exit(1)


if __name__ == '__main__':
    main()
