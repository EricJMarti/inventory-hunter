import datetime
import logging
import yaml


class Config:
    def __init__(self, refresh_interval, urls):
        self.refresh_interval = refresh_interval
        self.urls = urls


def parse_config(f):
    data = yaml.safe_load(f)
    refresh_interval = data['refresh_interval'] if 'refresh_interval' in data else 1

    if 'urls' not in data:
        raise Exception('config missing urls section')

    return Config(refresh_interval, data['urls'])
