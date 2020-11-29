import locale
import logging
import pathlib
import random
import re

from bs4 import BeautifulSoup
from driver import get_driver


class ScrapeResult:
    def __init__(self, r):
        self.alert_subject = None
        self.alert_content = None
        self.price = None
        self.soup = BeautifulSoup(r.text, 'lxml')
        self.content = self.soup.body.text.lower()  # lower for case-insensitive searches
        self.url = r.url

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


class GenericScrapeResult(ScrapeResult):
    def __init__(self, r):
        super().__init__(r)

        # not perfect but usually good enough
        if self.has_phrase('add to cart'):
            self.alert_subject = 'In Stock'
            self.alert_content = self.url


class BestBuyScrapeResult(ScrapeResult):
    def __init__(self, r):
        raise Exception('Best Buy is not supported yet :(')


class BHPhotoScrapeResult(ScrapeResult):
    def __init__(self, r):
        super().__init__(r)
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.find('div', class_=re.compile('title_.*'))
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            logging.warning(f'missing title: {self.url}')

        # get listed price
        tag = self.soup.body.find('div', class_=re.compile('pricesContainer_.*'))
        price_str = self.set_price(tag)
        if price_str:
            alert_subject = f'In Stock for {price_str}'
        else:
            logging.warning(f'missing price: {self.url}')

        # check for add to cart button
        tag = self.soup.body.find('button', class_=re.compile('toCartBtn.*'))
        if tag and 'add to cart' in tag.text.lower():
            self.alert_subject = alert_subject
            self.alert_content = f'{alert_content.strip()}\n{self.url}'


class MicroCenterScrapeResult(ScrapeResult):
    def __init__(self, r):
        super().__init__(r)
        alert_subject = 'In Stock'
        alert_content = ''

        details = self.soup.body.find('div', id='details', class_='inline')
        if details:

            # get name of product
            tag = details.select_one('h1 span')
            if tag:
                alert_content += tag.text.strip() + '\n'
            else:
                logging.warning(f'missing title: {self.url}')

            # get listed price
            tag = details.find('div', id='options-pricing')
            price_str = self.set_price(tag)
            if price_str:
                alert_subject = f'In Stock for {price_str}'
            else:
                logging.warning(f'missing price: {self.url}')

            # check for add to cart button
            tag = details.select_one('aside#cart-options form')
            if tag and 'add to cart' in str(tag).lower():
                self.alert_subject = alert_subject
                self.alert_content = f'{alert_content.strip()}\n{self.url}'

        else:
            logging.warning(f'missing details div: {self.url}')


class NeweggScrapeResult(ScrapeResult):
    def __init__(self, r):
        super().__init__(r)
        alert_subject = 'In Stock'
        alert_content = ''

        # get name of product
        tag = self.soup.body.find('h1', class_='product-title')
        if tag:
            alert_content += tag.text.strip() + '\n'
        else:
            logging.warning(f'missing title: {self.url}')

        buy_box = self.soup.body.find('div', class_='product-buy-box')
        if buy_box:

            # get listed price
            tag = buy_box.find('li', class_='price-current')
            price_str = self.set_price(tag)
            if price_str:
                alert_subject = f'In Stock for {price_str}'
            else:
                logging.warning(f'missing price: {self.url}')

            # check for add to cart button
            tag = buy_box.find('div', class_='product-buy')
            if tag:
                if 'add to cart' in tag.text.lower():
                    self.alert_subject = alert_subject
                    self.alert_content = f'{alert_content.strip()}\n{self.url}'
            else:
                logging.warning(f'missing add to cart button: {self.url}')

        else:
            logging.warning(f'missing buy box: {self.url}')


def get_result_type(url):
    if 'bestbuy' in url.netloc:
        return BestBuyScrapeResult
    elif 'bhphoto' in url.netloc:
        return BHPhotoScrapeResult
    elif 'microcenter' in url.netloc:
        return MicroCenterScrapeResult
    elif 'newegg' in url.netloc:
        return NeweggScrapeResult
    return GenericScrapeResult


def get_short_name(url):
    parts = [i for i in url.path.split('/') if i]
    if parts:
        if 'bestbuy' in url.netloc:
            return parts[1]
        elif 'bhphoto' in url.netloc:
            return parts[-1].replace('.html', '')
        elif 'microcenter' in url.netloc:
            return parts[-1]
        elif 'newegg' in url.netloc:
            return parts[0]
        return '_'.join(parts)
    random.seed()
    return f'unknown{random.randrange(100)}'


class Scraper:
    def __init__(self, url, timeout):
        self.driver = get_driver(timeout)
        self.name = get_short_name(url)
        self.result_type = get_result_type(url)
        self.url = url
        self.timeout = timeout
        self.in_stock_on_last_scrape = False
        self.price_on_last_scrape = None

        data_dir = pathlib.Path('data').resolve()
        data_dir.mkdir(exist_ok=True)
        self.filename = data_dir / f'{self.name}.txt'
        logging.info(f'scraper initialized for {self.url}')

    def scrape(self):
        try:
            url = str(self.url)
            r = self.driver.get(url)

            if r.ok:
                with self.filename.open('w') as f:
                    f.write(r.text)
                return self.result_type(r)
            else:
                logging.error(f'got response with status code {r.status_code} from {self.url}')

        except Exception as e:
            logging.error(f'{self.name}: caught exception during request: {e}')
