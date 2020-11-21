import logging
import pathlib
import requests
import urllib


class Scraper:
    def __init__(self, url):
        self.content = None
        self.name = None
        self.url = url

        # generate pretty name
        netloc = url.netloc
        path = url.path
        if 'newegg' in netloc:
            start = 1
            end = path.find('/', start)
            if end != -1:
                self.name = path[start:end]
        elif 'bhphoto' in netloc:
            begin = path.rfind('/')
            if begin != -1:
                begin += 1
                end = path.find('.', begin)
                self.name = path[begin:] if end == -1 else path[begin:end]
        elif 'microcenter' in netloc:
            begin = path.rfind('/')
            if begin != -1:
                begin += 1
                self.name = path[begin:]

        if self.name is None:
            self.name = str(url)

        data_dir = pathlib.Path('data').resolve()
        data_dir.mkdir(exist_ok=True)
        self.filename = data_dir / f'{self.name.replace("/", "_")}.txt'
        logging.info(f'scraper initialized for {self.url}')

    def has_phrase(self, phrase):
        return phrase in self.content

    def scrape(self):
        try:
            r = requests.get(self.url)
            if r.ok:
                self.content = r.content.decode('utf-8')
                with self.filename.open('w') as f:
                    f.write(self.content)
                self.content = self.content.lower()
                return True
        except Exception as e:
            logging.exception(f'{self.name}: caught exception during request: {e}')
