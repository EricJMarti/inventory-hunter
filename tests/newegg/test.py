import logging
import pathlib
import sys
import unittest

sys.path.append('/src')

from driver import HttpGetResponse
from scraper.newegg import NeweggScrapeResult as ScrapeResult


def load_result(filename):
    this_dir = pathlib.Path(__file__).parent.absolute()
    with open(this_dir / filename, 'r') as f:
        response = HttpGetResponse(f.read(), None)
        return ScrapeResult(logging.getLogger(), response, None)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.result = load_result('in_stock.html')

    def test_in_stock(self):
        self.assertTrue(self.result)

    def test_price(self):
        self.assertEqual(self.result.price, 154.99)
