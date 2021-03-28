import logging
import pathlib


class Endpoint:
    def __init__(self, source_file, addr, port):
        self.name = pathlib.Path(source_file).stem
        self.addr = addr
        self.port = port

    def __repr__(self):
        return f'{self.name}@{self.addr}:{self.port}'


class EndpointRegistry:
    registry = dict()

    @classmethod
    def get(cls, name):
        if name not in cls.registry:
            raise Exception(f'the "{name}" endpoint does not exist in the registry')
        return cls.registry[name]

    @classmethod
    def register(cls, server):
        endpoint = server._endpoint
        logging.debug(f'registering endpoint: {endpoint}')
        cls.registry[endpoint.name] = endpoint
        return server
