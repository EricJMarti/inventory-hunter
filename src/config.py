import urllib
import yaml

from collections import Counter


class URL:
    def __init__(self, url):
        self.nickname = 'covfefe'
        try:
            result = urllib.parse.urlparse(url)
            self.netloc = result.netloc
            self.path = result.path
            self.url = result.geturl()
        except Exception:
            raise Exception(f'invalid url: {url}')

    def __repr__(self):
        return self.url


class Config:
    def __init__(self, refresh_interval, max_price, urls):
        self.refresh_interval = float(refresh_interval)
        self.max_price = max_price
        self.urls = [URL(url) for url in urls]

        # generating nicknames
        netloc_counter = Counter()
        for url in self.urls:
            netloc = url.netloc.lower()
            if netloc.startswith('www.'):
                netloc = netloc.replace('www.', '')
            if netloc.endswith('.com'):
                netloc = netloc.replace('.com', '')
            for c in ('a', 'e', 'i', 'o', 'u'):
                netloc = netloc.replace(c, '')
            netloc = netloc.replace('.', '_')
            netloc_counter[netloc] += 1
            count = netloc_counter[netloc]
            nickname = f'{netloc}_{count}'
            url.nickname = nickname


def parse_config(f):
    data = yaml.safe_load(f)
    refresh_interval = data['refresh_interval'] if 'refresh_interval' in data else 1

    max_price = data['max_price'] if 'max_price' in data else None
    if max_price is not None and max_price <= 0:
        raise Exception('max_price must be positive')

    if 'urls' not in data:
        raise Exception('config missing urls section')

    urls = sorted(set([url for url in data['urls'] if url]))
    return Config(refresh_interval, max_price, urls)
