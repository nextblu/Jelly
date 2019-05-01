from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SO_BROADCAST, SOL_SOCKET
import ssl
from time import sleep
from pickle import loads, dumps
import threading
from config import configured_logger

logger = configured_logger.logger


def master_discovery():
    # BUG -> OSERROR 98
    # WORKAROUND: I try again until the port is free 
    try:
        client = socket(AF_INET, SOCK_DGRAM) # UDP
        client.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        client.bind(("", 37020))
        while True:
            data, addr = client.recvfrom(1024)
            if data:
                #data = data.decode()
                data = loads(data)
                # extracting server name
                ServerName = data["ServerName"]
                ServerVersion = data["ServerVersion"]
                ServerPort = data["ServerPort"]
                logger.info("Got service announcement from '{0}' version '{1}' on port '{2}'".format(ServerName, ServerVersion, ServerPort))
                #extracting the server's port number
                return ServerPort
    except Exception as e:
        logger.debug("Got an error while searching for the server: '{0}'".format(e))
        master_discovery()
    

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


class SlaveHandler(object):
    """docstring for SlaveHandler."""
    def __init__(self, arg, port, magic):
        super(SlaveHandler, self).__init__()
        self.arg = arg
        self.port = port
        self.magic = magic
        # The following line is commented due to an unresolved reference error. What is that method meant to do?
        # master_discovery()




if __name__ == "__main__":
    PORT = master_discovery()

    HOST, PORT, MAGIC = "localhost", 9999, "JellySERVER"

    # create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
    client = socket(AF_INET, SOCK_STREAM)

    # connect the client
    client.connect((HOST, PORT))


    message = "dummy data"
    # Creating the dict
    data = {
      "ClientID": "44ad4456a4d65s",     # Yo, we should add client ID here
      "ClientVersion": "0.001",         # :)
      "ClientMessage": message
    }

    client.send(dumps(data))

    # receive the response data (4096 is recommended buffer size for incoming commands)
    response = client.recv(4096)
    logger.debug(response)
