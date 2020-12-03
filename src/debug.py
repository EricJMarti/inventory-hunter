import argparse
import logging

from bs4 import BeautifulSoup


try:
    import lxml  # noqa: F401
    parser = 'lxml'
except ImportError:
    parser = 'html.parser'
finally:
    logging.debug(f'using parser: {parser}')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('datafile', type=argparse.FileType('r'))
    return parser.parse_args()


args = parse_args()
soup = BeautifulSoup(args.datafile.read(), parser)
