import socket
from socket import socket, AF_INET, SOCK_DGRAM
import config.configured_logger

# TODO:
"""
+ Implement headers
+ Implement an ID system
+ Implement a send_forever directive
+ Implement an intent broker
+ Implement a master-watchdogs
"""
logger = config.configured_logger.logger


class SlaveHandler(object):
    """docstring for SlaveHandler."""
    def __init__(self, arg):
        super(SlaveHandler, self).__init__()
        self.arg = arg
        MasterDiscovery()

    def MasterDiscovery(self):
        s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
        s.bind(('', PORT))

        while 1:
            data, addr = s.recvfrom(1024) #wait for a packet
            if data.startswith(MAGIC):
                print "got service announcement from", data[len(MAGIC):]

    def intentBroker(self):
        pass


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect the client
    client.connect((HOST, PORT))

    # send some data
    client.send('dummy data'.encode('utf-8'))

    # receive the response data (4096 is recommended buffer size for incoming commands)
    response = client.recv(4096)

    logger.debug (response)
