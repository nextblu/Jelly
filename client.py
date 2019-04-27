from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from config import configured_logger

# TODO:
"""
+ Implement headers
+ Implement an ID system
+ Implement a send_forever directive
+ Implement an intent broker
+ Implement a master-watchdogs
"""
logger = configured_logger.logger


class SlaveHandler(object):
    """docstring for SlaveHandler."""
    def __init__(self, arg, port, magic):
        super(SlaveHandler, self).__init__()
        self.arg = arg
        self.port = port
        self.magic = magic
        # The following line is commented due to an unresolved reference error. What is that method meant to do?
        # master_discovery()

    def master_discovery(self):
        # create UDP socket
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind(('', self.port))

        while 1:
            # wait for a packet
            data, address = s.recvfrom(1024)
            if data.startswith(self.magic):
                logger.info("got service announcement from", data[len(self.magic):])

    def intent_broker(self):
        pass


if __name__ == "__main__":
    HOST, PORT, MAGIC = "localhost", 9999, "JellySERVER"

    # create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
    client = socket(AF_INET, SOCK_STREAM)

    # connect the client
    client.connect((HOST, PORT))

    # send some data
    client.send('dummy data'.encode('utf-8'))

    # receive the response data (4096 is recommended buffer size for incoming commands)
    response = client.recv(4096)
    logger.debug(response)
