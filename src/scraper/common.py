import locale
import logging
import pathlib
import random

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup


try:
    import lxml  # noqa: F401
    parser = 'lxml'
except ImportError:
    parser = 'html.parser'
finally:
    logging.debug(f'using parser: {parser}')


class ScrapeResult(ABC):
    def __init__(self, r, last_result):
        self.alert_subject = None
        self.alert_content = None
        self.previously_in_stock = bool(last_result)
        self.price = None
        self.last_price = last_result.price if last_result is not None else None
        self.soup = BeautifulSoup(r.text, parser)
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

        price_str = tag.text.strip()
        if not price_str:
            return

        try:
            currency_symbol = locale.localeconv()['currency_symbol']
            self.price = locale.atof(price_str.replace(currency_symbol, '').strip())
            return price_str if price_str else None
        except Exception as e:
            logging.warning(f'unable to convert "{price_str}" to float... caught exception: {e}')

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
        self.url = url
        self.last_result = None

        self.name = self.generate_short_name(url)
        if not self.name:
            random.seed()
            return f'{self.get_domain()}{random.randrange(100)}'

        data_dir = pathlib.Path('data').resolve()
        data_dir.mkdir(exist_ok=True)
        self.filename = data_dir / f'{self.name}.txt'
        logging.info(f'scraper initialized for {self.url}')

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

    @staticmethod
    @abstractmethod
    def generate_short_name(url):
        pass

    def scrape(self):
        try:
            url = str(self.url)
            logging.debug(f'{self.name}: starting new scrape')
            r = self.driver.get(url)
            with self.filename.open('w') as f:
                f.write(r.text)
            result_type = self.get_result_type()
            this_result = result_type(r, self.last_result)
            self.last_result = this_result
            return this_result

        except Exception as e:
            logging.error(f'{self.name}: caught exception during request: {e}')


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

    @staticmethod
    def generate_short_name(url):
        parts = [i for i in url.path.split('/') if i]
        if parts:
            return '_'.join(parts)


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
