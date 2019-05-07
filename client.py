from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SO_BROADCAST, SOL_SOCKET
import argparse
import ssl
from time import sleep
from pickle import loads, dumps
import threading
from config import configured_logger
from uuid import uuid4

logger = configured_logger.logger

class SecureTCPClient:
    def __init__(self, server_address, cafile):
        # create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
        self._client = socket(AF_INET, SOCK_STREAM)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cafile)
        context.check_hostname = False
        self._client = context.wrap_socket(self._client)

        # connect the client
        self._client.connect(server_address)

    def client_close(self):
        self._client.close()

    def exchange(self, data):
        # send some data
        self._client.send(data)

        # receive the response data (4096 is recommended buffer size for incoming commands)
        response = self._client.recv(4096)
        return response

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.client_close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Jclient.py',
        description=('''\
            Hey!
            With Jelly you can simply create a socket messaging system in Python.
            You can use this program to run a client that will send data to the server.'''),
        epilog='''Please note: Jelly is currently in Alpha version.''')
    parser.add_argument('--port', help='[OPTIONAL] Select the server port number')
    args = parser.parse_args()
    PORT = 5233 # jcdf  =   5233 (jelly-cavuti-De Paoli-Failla)
    if args.port:
        PORT = int(args.port)

    HOST, UUID = "0.0.0.0", str(uuid4())
    CERFILE = 'test/demo_ssl/server.crt'
    # Create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
    client = socket(AF_INET, SOCK_STREAM)

    client = SecureTCPClient((HOST, PORT), CERFILE)

    message = "dummy data"
    # Creating the datagram
    datagram = {
      "ClientID": UUID,
      "ClientVersion": "0.001",
      "ClientAlias": "MyName",
      "ClientMessage": message
    }
    server_response = client.exchange(dumps(datagram))
    logger.debug(server_response)
