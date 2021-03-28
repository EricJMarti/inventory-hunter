import asyncio
import logging

import worker.worker_pb2 as spec


class Client:
    def __init__(self, endpoint):
        self._endpoint = endpoint
        self._request = spec.Request()

    def decode_response(self, data) -> spec.Response:
        response = spec.Response()
        response.ParseFromString(data)
        return response

    def encode_request(self, request_id: int, url: str, timeout: int) -> str:
        self._request.Clear()
        self._request.id = request_id
        self._request.url = url
        self._request.timeout = timeout
        return self._request.SerializeToString()

    async def get_impl(self, request_id: int, url: str, timeout: int) -> spec.Response:
        reader, writer = await asyncio.open_connection(self._endpoint.addr, self._endpoint.port)
        serialized_request = self.encode_request(request_id, url, timeout)
        writer.write(serialized_request)
        writer.write_eof()
        await writer.drain()

        response = self.decode_response(await reader.read())
        logging.debug(f'got response with id {response.id}, status_code: {response.status_code}, data: <{len(response.data)} bytes>')
        writer.close()
        await writer.wait_closed()

        return response

    async def get_async(self, request_id: int, url: str, timeout: int) -> spec.Response:
        return self.get_impl(request_id, url, timeout)

    def get(self, request_id: int, url: str, timeout: int) -> spec.Response:
        return asyncio.run(self.get_impl(request_id, url, timeout))
