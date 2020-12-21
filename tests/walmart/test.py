import logging
import pathlib
import unittest

from driver import HttpGetResponse
from scraper.walmart import WalmartScrapeResult as ScrapeResult


def load_result(filename):
    this_dir = pathlib.Path(__file__).parent.absolute()
    with open(this_dir / filename, 'r') as f:
        response = HttpGetResponse(f.read(), None)
        return ScrapeResult(logging.getLogger(), response, None)


class CAPTCHAFixture(unittest.TestCase):
    def setUp(self):
        self.result = load_result('captcha.html')

    def test_captcha(self):
        self.assertTrue(self.result.captcha)

    def test_in_stock(self):
        self.assertFalse(self.result)


class InStockFixture(unittest.TestCase):
    def setUp(self):
        self.result = load_result('in_stock.html')

    def test_captcha(self):
        self.assertFalse(self.result.captcha)

    def test_in_stock(self):
        self.assertTrue(self.result)

    def test_price(self):
        self.assertEqual(self.result.price, 499.99)
