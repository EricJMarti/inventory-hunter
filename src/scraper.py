import logging
import requests


class Scraper:
    def __init__(self, url):
        self.content = None
        self.name = url
        self.url = url

        # generate pretty name
        if 'newegg' in url:
            token = '.com/'
            begin = url.find(token)
            if begin != -1:
                begin += len(token)
                end = url.find('/', begin)
                self.name = url[begin:] if end == -1 else url[begin:end]
        elif 'bhphoto' in url:
            begin = url.rfind('/')
            if begin != -1:
                begin += 1
                end = url.find('.', begin)
                self.name = url[begin:] if end == -1 else url[begin:end]
        elif 'microcenter' in url:
            begin = url.rfind('/')
            if begin != -1:
                begin += 1
                self.name = url[begin:]

        logging.info(f'scraper initialized for {self.url}')

    def has_phrase(self, phrase):
        return phrase in self.content

    def scrape(self):
        try:
            r = requests.get(self.url)
            if r.ok:
                self.content = r.content.decode('utf-8').lower()
                return True
        except Exception as e:
            logging.exception(f'{self.name}: caught exception during request: {e}')
