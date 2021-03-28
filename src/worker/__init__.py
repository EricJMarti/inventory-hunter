import worker.lean_and_mean  # noqa: F401

from worker.client import Client
from worker.registry import EndpointRegistry


def init_client(endpoint):
    endpoint = EndpointRegistry.get(endpoint)
    return Client(endpoint)
