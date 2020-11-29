import getpass
import logging
import os
import requests
import subprocess

from selenium import webdriver


class SeleniumDriver:
    def __init__(self, timeout):
        self.chromium = None

        chromium_path = '/usr/bin/chromium'
        if not os.path.exists(chromium_path):
            raise Exception(f'not found: {chromium_path}')

        chromium_cmd = [chromium_path]
        if getpass.getuser() == 'root':
            chromium_cmd.append('--no-sandbox')  # required if root

        self.chromium = subprocess.Popen(chromium_cmd)
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(self.timeout)

    def __del__(self):
        if self.chromium is None:
            return
        if self.chromium.poll() is not None:
            return
        self.chromium.terminate()
        try:
            self.chromium.wait(1)
        except subprocess.TimeoutExpired:
            self.chromium.kill()

    def get(self, url):
        return self.driver.get(url)


class RequestsDriver:
    def __init__(self, timeout):
        self.timeout = timeout

    def get(self, url):
        return requests.get(url, timeout=self.timeout)


def get_driver(timeout):
    try:
        return SeleniumDriver(timeout)
    except Exception as e:
        logging.error(f'caught exception during selenium driver init: {e}')
        logging.warning('falling back to requests module')
        return RequestsDriver(timeout)
