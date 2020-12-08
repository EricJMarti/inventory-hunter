import locale
import logging
import pathlib
import html

# required for price parsing logic
locale.setlocale(locale.LC_ALL, '')

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup


class ScrapeResult(ABC):
    def __init__(self, logger, r, last_result):
        self.alert_subject = None
        self.alert_content = None
        self.logger = logger
        self.previously_in_stock = bool(last_result)
        self.price = None
        self.last_price = last_result.price if last_result is not None else None
        self.soup = BeautifulSoup(r.text, 'lxml')
        self.content = self.soup.body.text.lower()  # lower for case-insensitive searches
        self.url = r.url
        self.parse()

    def __bool__(self):
        return bool(self.alert_content)

    def has_phrase(self, phrase):
        return phrase in self.content

    def set_price(self, tag):
        if not tag:
            return

        price_str = tag if isinstance(tag, str) else tag.text.strip()
        price_str = html.unescape(price_str).strip()
        if not price_str:
            return

        try:
            currency_symbol = locale.localeconv()['currency_symbol']
            self.price = locale.atof(price_str.replace(currency_symbol, '').strip())
            return price_str if price_str else None
        except Exception as e:
            self.logger.warning(f'unable to convert "{price_str}" to float... caught exception: {e}')

    @abstractmethod
    def parse(self):
        pass


class GenericScrapeResult(ScrapeResult):
    def parse(self):
        # not perfect but usually good enough
        if self.has_phrase('add to cart') or self.has_phrase('add to basket'):
            self.alert_subject = 'In Stock'
            self.alert_content = self.url


class Scraper(ABC):
    def __init__(self, drivers, url):
        self.driver = getattr(drivers, self.get_driver_type())
        self.logger = logging.getLogger(url.nickname)
        self.url = url
        self.last_result = None

        data_dir = pathlib.Path('data').resolve()
        data_dir.mkdir(exist_ok=True)
        self.filename = data_dir / f'{url.nickname}.txt'
        self.logger.info(f'scraper initialized for {self.url}')

    @staticmethod
    @abstractmethod
    def get_domain():
        pass

    @staticmethod
    @abstractmethod
    def get_driver_type():
        pass

    @staticmethod
    @abstractmethod
    def get_result_type():
        pass

    def scrape(self):
        try:
            url = str(self.url)
            self.logger.debug('starting new scrape')
            r = self.driver.get(url)
            with self.filename.open('w') as f:
                f.write(r.text)
            result_type = self.get_result_type()
            this_result = result_type(self.logger, r, self.last_result)
            self.last_result = this_result
            return this_result

        except Exception as e:
            self.logger.error(f'caught exception during request: {e}')


class GenericScraper(Scraper):
    @staticmethod
    def get_domain():
        return 'generic'

    @staticmethod
    def get_driver_type():
        return 'requests'

    @staticmethod
    def get_result_type():
        return GenericScrapeResult


class ScraperFactory:
    registry = dict()

    @classmethod
    def create(cls, drivers, url):
        for domain, scraper_type in cls.registry.items():
            if domain in url.netloc:
                return scraper_type(drivers, url)
        logging.warning(f'warning: using generic scraper for url: {url}')
        return GenericScraper(drivers, url)

    @classmethod
    def register(cls, scraper_type):
        domain = scraper_type.get_domain()
        logging.debug(f'registering custom scraper for domain: {domain}')
        cls.registry[domain] = scraper_type
        return scraper_type
