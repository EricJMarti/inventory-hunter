import logging
import pathlib
import unittest

from driver import HttpGetResponse
from scraper.adorama import AdoramaScrapeResult as ScrapeResult


def load_result(filename):
    this_dir = pathlib.Path(__file__).parent.absolute()
    with open(this_dir / filename, 'r') as f:
        response = HttpGetResponse(f.read(), None)
        return ScrapeResult(logging.getLogger(), response, None)


class InStockFixture(unittest.TestCase):
    def setUp(self):
        self.result = load_result('in_stock.html')

    def test_in_stock(self):
        self.assertTrue(self.result)

    def test_price(self):
        self.assertEqual(self.result.price, 1455.00)


class OutOfStockFixture(unittest.TestCase):
    def setUp(self):
        self.result = load_result('out_of_stock.html')

    def test_in_stock(self):
        self.assertFalse(self.result)
