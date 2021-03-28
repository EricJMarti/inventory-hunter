import argparse
import importlib
import logging


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('worker')
    return parser.parse_args()


def main():
    args = parse_args()
    log_format = '{{levelname:.1s}}{{asctime}} [{args.worker}] {{message}}'
    logging.basicConfig(level=logging.ERROR, format=log_format, style='{')

    logger = logging.getLogger()
    handler = logging.FileHandler(f'/{args.worker}.txt')
    handler.setFormatter(logging.Formatter(log_format, style='{'))
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    pkg = importlib.import_module(f'worker.{args.worker}')
    pkg.run()


if __name__ == '__main__':
    main()
