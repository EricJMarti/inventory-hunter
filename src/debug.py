import argparse

from bs4 import BeautifulSoup


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('datafile', type=argparse.FileType('r'))
    return parser.parse_args()


args = parse_args()
soup = BeautifulSoup(args.datafile.read(), 'lxml')
