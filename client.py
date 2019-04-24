import socket
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
