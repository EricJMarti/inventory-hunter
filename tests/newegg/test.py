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


class BundleInStockFixture(unittest.TestCase):
    def setUp(self):
        self.result = load_result('bundle_in_stock.html')

    def test_in_stock(self):
        self.assertTrue(self.result)

    def test_price(self):
        self.assertEqual(self.result.price, 541.98)


class BundleOutOfStockFixture(unittest.TestCase):
    def setUp(self):
        self.result = load_result('bundle_out_of_stock.html')

    def test_in_stock(self):
        self.assertFalse(self.result)


class InStockFixture(unittest.TestCase):
    def setUp(self):
        self.result = load_result('in_stock.html')

    def test_in_stock(self):
        self.assertTrue(self.result)

    def test_price(self):
        self.assertEqual(self.result.price, 154.99)


class OutOfStockFixture(unittest.TestCase):
    def setUp(self):
        self.result = load_result('out_of_stock.html')

    def test_in_stock(self):
        self.assertFalse(self.result)
