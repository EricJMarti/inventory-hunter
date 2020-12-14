import getpass
import logging
import os
import pathlib
import requests

from abc import ABC, abstractmethod
from selenium import webdriver


user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'


class HttpGetResponse:
    def __init__(self, text, url):
        self.text = text
        self.url = url


class Driver(ABC):
    def __init__(self, **kwargs):
        self.data_dir = kwargs.get('data_dir')
        self.timeout = kwargs.get('timeout')

    @abstractmethod
    def get(self, url) -> HttpGetResponse:
        pass


class SeleniumDriver(Driver):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        driver_paths = [
            '/usr/bin/chromedriver',
            '/usr/bin/local/chromedriver',
        ]
        self.driver_path = None
        for driver_path in driver_paths:
            if os.path.exists(driver_path):
                self.driver_path = driver_path
                break

        if not self.driver_path:
            raise Exception('Selenium Chrome driver not found at ' + ' or '.join(driver_paths))

        self.options = webdriver.ChromeOptions()
        self.options.headless = True
        self.options.page_load_strategy = 'eager'
        if getpass.getuser() == 'root':
            self.options.add_argument('--no-sandbox')  # required if root
        self.options.add_argument(f'--user-agent="{user_agent}"')
        self.options.add_argument('--user-data-dir=/selenium')
        self.options.add_argument('--window-size=1920,1080')

    def get(self, url) -> HttpGetResponse:
        # headless chromium crashes somewhat regularly...
        # for now, we will start a fresh instance every time
        with webdriver.Chrome(self.driver_path, options=self.options) as driver:
            driver.get(str(url))

            try:
                filename = self.data_dir / f'{url.nickname}.png'
                driver.save_screenshot(str(filename))
            except Exception as e:
                logging.warning(f'unable to save screenshot of webpage: {e}')

            return HttpGetResponse(driver.page_source, url)


class RequestsDriver(Driver):
    def get(self, url) -> HttpGetResponse:
        headers = {'user-agent': user_agent, 'referrer': 'https://google.com'}
        r = requests.get(str(url), headers=headers, timeout=self.timeout)
        if not r.ok:
            raise Exception(f'got response with status code {r.status_code} for {url}')
        return HttpGetResponse(r.text, r.url)


class DriverRepo:
    def __init__(self, timeout):
        self.data_dir = pathlib.Path('data').resolve()
        self.data_dir.mkdir(exist_ok=True)
        self.requests = RequestsDriver(data_dir=self.data_dir, timeout=timeout)
        self.selenium = SeleniumDriver(data_dir=self.data_dir, timeout=timeout)


def init_drivers(config):
    timeout = max(config.refresh_interval, 5)  # in seconds
    return DriverRepo(timeout)
