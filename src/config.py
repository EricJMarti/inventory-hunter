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
    def __init__(self, refresh_interval, urls):
        self.refresh_interval = refresh_interval
        self.urls = [URL(url) for url in sorted(set(urls))]


def parse_config(f):
    data = yaml.safe_load(f)
    refresh_interval = data['refresh_interval'] if 'refresh_interval' in data else 1

    if 'urls' not in data:
        raise Exception('config missing urls section')

    return Config(refresh_interval, data['urls'])
