import getpass
import logging
import os
import requests

from selenium import webdriver


class HttpGetResponse:
    def __init__(self, text, url):
        self.text = text
        self.url = url


class SeleniumDriver:
    def __init__(self, timeout):
        self.timeout = timeout

        self.driver_path = '/usr/bin/chromedriver'
        if not os.path.exists(self.driver_path):
            raise Exception(f'not found: {self.driver_path}')

        self.options = webdriver.ChromeOptions()
        self.options.headless = True
        if getpass.getuser() == 'root':
            self.options.add_argument('--no-sandbox')  # required if root

    def get(self, url):
        # headless chromium crashes somewhat regularly...
        # for now, we will start a fresh instance every time
        driver = webdriver.Chrome(self.driver_path, options=self.options)
        try:
            driver.get(url)
            return HttpGetResponse(driver.page_source, url)
        finally:
            driver.close()
            driver.quit()


class RequestsDriver:
    def __init__(self, timeout):
        self.timeout = timeout

    def get(self, url):
        r = requests.get(url, timeout=self.timeout)
        if not r.ok:
            raise Exception(f'got response with status code {r.status_code} for {url}')
        return HttpGetResponse(r.text, r.url)


def try_init_selenium_driver(timeout):
    logging.warning('warning: using selenium webdriver for scraping... this feature is under active development')
    try:
        return SeleniumDriver(timeout)
    except Exception as e:
        logging.error(f'caught exception during selenium driver init: {e}')
        logging.warning('falling back to requests module')
        return RequestsDriver(timeout)


def init_driver(config):
    timeout = config.refresh_interval
    for url in config.urls:
        if 'bestbuy' in url.netloc:
            return try_init_selenium_driver(timeout)
    return RequestsDriver(timeout)
