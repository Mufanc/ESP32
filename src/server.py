import asyncio
import re


class HttpRequest(object):
    @classmethod
    def findall(cls, pattern, string) -> list:
        match = re.search(pattern, string)
        index, groups = 1, []

        while True:
            try:
                groups.append(match.group(index))
            except IndexError:
                break

            index += 1

        return groups

    @classmethod
    async def from_stream(cls, stream: asyncio.StreamReader):
        method, path = cls.findall('^(.+) (.+) HTTP/[\\d.]+\r?\n$', (await stream.readline()).decode())
        headers = {}

        while True:
            line = (await stream.readline()).decode()

            if not line.strip():
                break
            else:
                key, value = cls.findall('^(\\S+?): ?(.+)\r?\n$', line)
                headers[key.lower()] = value.strip()

        body = await stream.read(int(headers['content-length']))

        return HttpRequest(method, path, headers, body)

    def __init__(self, method: str, path: str, headers: dict[str, str], body=b''):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body

    def __str__(self):
        return f'HttpRequest(method={self.method}, path={self.path}, headers={self.headers}, body={self.body})'


class HttpResponse(object):
    def __init__(self, body: bytes = b''):
        self.code = 200
        self.body = body
        self.headers = {
            'Content-Length': str(len(body)),
            'Access-Control-Allow-Origin': '*'
        }

    def add_header(self, key, value):
        self.headers[key] = value

    def write_to_stream(self, stream: asyncio.StreamWriter):
        stream.write(b'HTTP/1.1 ' + str(self.code).encode() + b'\r\n')

        for key in self.headers:
            stream.write(key.encode() + b': ' + self.headers[key].encode() + b'\r\n')

        stream.write(b'\r\n')
        stream.write(self.body)


class HttpServer(object):
    def __init__(self):
        self.server = None
        self.port = -1
        self.handler = None

    async def _handler(self, rx, tx):
        if self.handler:
            resp = self.handler(await HttpRequest.from_stream(rx))
            HttpResponse(resp).write_to_stream(tx)
        else:
            HttpResponse().write_to_stream(tx)
        rx.close()
        tx.close()

    async def bind(self, port: int):
        self.port = port

    async def serve_forever(self, handler):
        self.handler = handler
        self.server = await asyncio.start_server(self._handler, '0.0.0.0', self.port)
        await self.server.wait_closed()
