import logging
import pathlib
import random
import requests
import urllib

from bs4 import BeautifulSoup


def get_short_name(url):
    parts = [i for i in url.path.split('/') if i]
    if parts:
        if 'newegg' in url.netloc:
            return parts[0]
        elif 'bhphoto' in url.netloc:
            return parts[-1].replace('.html', '')
        elif 'microcenter' in url.netloc:
            return parts[-1]
        return '_'.join(parts)
    random.seed()
    return f'unknown{random.randrange(100)}'


class ScrapeResult:
    def __init__(self, r):
        self.response = r
        self.content = self.response.text.lower()
        self.soup = BeautifulSoup(self.response.text, 'lxml')

    def has_add_to_cart(self):
        phrase = 'add to cart'

        if 'newegg' in self.response.url:
            tag = self.soup.body.find(class_='product-buy-box')
            if tag:
                return phrase in str(tag).lower()

        return self.has_phrase(phrase)

    def has_phrase(self, phrase):
        return phrase in self.content


class Scraper:
    def __init__(self, url):
        self.content = None
        self.name = get_short_name(url)
        self.url = url

        data_dir = pathlib.Path('data').resolve()
        data_dir.mkdir(exist_ok=True)
        self.filename = data_dir / f'{self.name}.txt'
        logging.info(f'scraper initialized for {self.url}')

    def scrape(self):
        try:
            r = requests.get(str(self.url))

            if r.ok:
                result = ScrapeResult(r)
                with self.filename.open('w') as f:
                    f.write(result.soup.prettify())
                return result
            else:
                logging.error(f'got response with status code {r.status_code} from {self.url}')

        except Exception as e:
            logging.exception(f'{self.name}: caught exception during request: {e}')
