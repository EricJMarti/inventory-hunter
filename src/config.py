import urllib
import yaml


class URL:
    def __init__(self, url):
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
        self.refresh_interval = refresh_interval
        self.max_price = max_price
        self.urls = [URL(url) for url in sorted(set(urls))]


def parse_config(f):
    data = yaml.safe_load(f)
    refresh_interval = data['refresh_interval'] if 'refresh_interval' in data else 1

    max_price = data['max_price'] if 'max_price' in data else None
    if max_price is not None and max_price <= 0:
        raise Exception('max_price must be positive')

    if 'urls' not in data:
        raise Exception('config missing urls section')

    return Config(refresh_interval, max_price, data['urls'])
