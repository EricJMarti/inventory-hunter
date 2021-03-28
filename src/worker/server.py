import asyncio
import logging

from abc import ABC, abstractmethod

import worker.worker_pb2 as spec


class Server(ABC):
    def __init__(self, endpoint):
        self._response = spec.Response()

    def decode_request(self, data) -> spec.Request:
        request = spec.Request()
        request.ParseFromString(data)
        return request

    def encode_response(self, response_id: int, data: str, status_code: int) -> str:
        self._response.Clear()
        self._response.id = response_id
        self._response.data = data
        self._response.status_code = status_code
        return self._response.SerializeToString()

    async def handle(self, reader, writer):
        try:
            request = self.decode_request(await reader.read())
            logging.info(f'received request: id: {request.id}, url: {request.url}, timeout: {request.timeout}')
            await self.handle_request(request, writer)
        except Exception as e:
            logging.error(f'something went wrong during request: {e}')

        writer.close()
        await writer.wait_closed()

    @abstractmethod
    async def handle_request(self, request, writer):
        pass

    async def run_impl(self):
        server = await asyncio.start_server(self.handle, self._endpoint.addr, self._endpoint.port)
        async with server:
            await server.serve_forever()

    def run(self):
        asyncio.run(self.run_impl())
