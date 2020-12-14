import logging
import yaml

from abc import ABC, abstractmethod
from collections.abc import Callable


class Alerter(ABC, Callable):
    def __init__(self, **kwargs):
        pretty_kwargs = ' '.join([f'{k}={v}' for k, v in kwargs.items()])
        logging.info(f'{self.get_alerter_type()} alerter initialized with kwargs: {pretty_kwargs}')

    @classmethod
    @abstractmethod
    def from_args(cls, args):
        pass

    @classmethod
    @abstractmethod
    def from_config(cls, config):
        pass

    @staticmethod
    @abstractmethod
    def get_alerter_type():
        pass


class AlertEngine:
    def __init__(self, alerters):
        self.alerters = alerters
        if not self.alerters:
            raise Exception('no alerters loaded')

    def __call__(self, **kwargs):
        for alerter in self.alerters:
            try:
                alerter(**kwargs)
            except Exception:
                logging.exception(f'{alerter.get_alerter_type()} alerter failed to alert')


class AlerterFactory:
    registry = dict()

    @classmethod
    def create(cls, args):
        if args.alerter_config is None:
            return cls.create_from_args(args)
        else:
            return cls.create_from_config(args.alerter_config)

    @classmethod
    def create_from_args(cls, args):
        alerter = cls.get_alerter(args.alerter_type)
        return AlertEngine([alerter.from_args(args)])

    @classmethod
    def create_from_config(cls, config):
        data = yaml.safe_load(config)
        alerters = []
        for alerter_type, alerter_config in data['alerters'].items():
            alerter = cls.get_alerter(alerter_type)
            alerters.append(alerter.from_config(alerter_config))
        return AlertEngine(alerters)

    @classmethod
    def get_alerter(cls, alerter_type):
        if alerter_type not in cls.registry:
            raise Exception(f'the "{alerter_type}" alerter type does not exist in the registry')
        return cls.registry[alerter_type]

    @classmethod
    def register(cls, alerter):
        alerter_type = alerter.get_alerter_type()
        logging.debug(f'registering alerter type: {alerter_type}')
        cls.registry[alerter_type] = alerter
        return alerter
