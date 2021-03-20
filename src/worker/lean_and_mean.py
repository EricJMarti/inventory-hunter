import aiohttp
import argparse
import asyncio
import logging
import urllib.parse


from worker_pb2 import Request, Response


async def handle(reader, writer):
    try:
        request = Request()
        request.ParseFromString(await reader.read())
        logging.info(f'received request: id: {request.id}, url: {request.url}, timeout: {request.timeout}')

        headers = {
            'authority': urllib.parse.urlparse(request.url).netloc,
            'accept': 'text/html',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'dnt': '1',
            'pragma': 'no-cache',
            'referer': 'https://google.com',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4427.0 Safari/537.36',
        }

        timeout = request.timeout if request.timeout else 30

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(request.url, timeout=timeout) as r:
                response = Response()
                response.id = request.id
                response.status_code = r.status
                response.data = await r.text()
                writer.write(response.SerializeToString())
                writer.write_eof()
                logging.info(
                    f'sent response: id: {response.id}, status_code: {response.status_code}, data: <{len(response.data)} bytes>'
                )

    except Exception as e:
        logging.error(f'something went wrong during request: {e}')
        pass

    writer.close()
    await writer.wait_closed()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=3080)
    parser.add_argument('--log', default='/lean_and_mean.txt')
    return parser.parse_args()


async def main():
    args = parse_args()
    log_format = '{levelname:.1s}{asctime} [lean_and_mean] {message}'
    logging.basicConfig(level=logging.ERROR, format=log_format, style='{')
    if args.log:
        logger = logging.getLogger()
        handler = logging.FileHandler(args.log)
        handler.setFormatter(logging.Formatter(log_format, style='{'))
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    server = await asyncio.start_server(handle, args.host, args.port)
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
