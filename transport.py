"""
Socket transport layer

MIT License

Copyright (c) 2019 Marco De Paoli

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import logging
import socket
import socketserver
import ssl

logger = logging.getLogger(__name__)


class EnvelopeException(Exception):
    pass


class StreamEnvelope:
    TERMINATOR = b"\n"
    MAX_CHUNK_SIZE = 4096

    def __init__(self, sock, terminator=None):
        self.sock = sock
        self.terminator = terminator or self.TERMINATOR

    def _exception_if_data_contains_terminator(self, binary_data):
        try:
            binary_data.index(self.terminator)
            raise EnvelopeException("Terminator found inside binary data")
        except ValueError:
            pass

    def _stream_retrieve(self, stream):
        data = b""

        while True:
            chunk = stream(self.MAX_CHUNK_SIZE)
            logger.debug("chunk received, length: %d, data: %s", len(chunk), chunk)
            if not chunk:
                # socket closed or end of stream
                break
            try:
                end = chunk.index(self.terminator)
                # terminator found, the stream is over
                data += chunk[:end]
                break
            except ValueError:
                # no terminator found, yet
                data += chunk

        return data

    def send(self, binary_data):
        self._exception_if_data_contains_terminator(binary_data)
        self.sock.sendall(binary_data + self.terminator)

    def receive(self):
        return self._stream_retrieve(self.sock.recv)


class JsonEnvelope:

    def __init__(self, channel):
        self.channel = channel

    def send(self, message):
        request = json.dumps(message).encode("utf8")
        self.channel.send(request)

    def receive(self):
        response = self.channel.receive()
        return json.loads(str(response, "utf8"))


class Envelops:
    BASE_ENVELOPE = StreamEnvelope
    MIDDLEWARE = [JsonEnvelope]

    @classmethod
    def build(cls, sock):
        envelope = cls.BASE_ENVELOPE(sock)
        for mw in cls.MIDDLEWARE:
            envelope = mw(envelope)
        return envelope


class RequestHandler(socketserver.BaseRequestHandler):
    """
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def setup(self):
        # self.request is the TCP socket connected to the client
        self.envelope = Envelops.build(self.request)

    def handle(self):
        data = self.envelope.receive()
        logger.debug("{} wrote: {}".format(self.client_address[0], data))
        response = self.server.action(data)
        self.envelope.send(response)


class Server(socketserver.TCPServer):
    def __init__(self, cerfile, keyfile, server_address, action):
        self.cerfile = cerfile
        self.keyfile = keyfile
        self.server_address = server_address
        self.action = action
        super().__init__(server_address, RequestHandler)

    def server_activate(self):
        logger.info("Starting server at address {}".format(self.server_address))
        super().server_activate()
        # secure context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(self.cerfile, self.keyfile)
        self.socket = context.wrap_socket(self.socket, server_side=True)
        logger.info("Server started")

    def handle_error(self, request, client_address):
        logger.error('-'*40)
        logger.exception('Exception happened during processing of request from %s', client_address)
        logger.error('-'*40)

    def server_close(self):
        logger.info("Shutting down server at address {}".format(self.server_address))
        super().server_close()
        logger.info("Server stopped")


class ThreadingServer(socketserver.ThreadingMixIn, Server):
    pass


class Client:
    def __init__(self, cafile, server_address):
        # create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cafile)
        context.check_hostname = False
        self._client = context.wrap_socket(self._client)
        self._client.connect(server_address)
        self.envelope = Envelops.build(self._client)

    def client_close(self):
        self._client.close()

    def exchange(self, data):
        self.envelope.send(data)
        logger.debug("CLIENT sent: %s", data)
        response = self.envelope.receive()
        logger.debug("CLIENT received: %s", response)
        return response

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.client_close()
