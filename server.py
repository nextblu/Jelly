import socketserver
from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname
from .config import configured_logger

logger = configured_logger.logger


def service_announcement(port, magic):
    # create UDP socket
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('', 0))

    # this is a broadcast socket
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    # get our IP. Be careful if you have multiple network interfaces or IPs
    my_ip = gethostbyname(gethostname())

    while 1:
        announcement_data = magic+my_ip
        s.sendto(announcement_data, ('<broadcast>', port))
        logger.debug("Sent service announcement")
        sleep(5)


class TCPHandler(socketserver.BaseRequestHandler):
    """
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    # Instantiation of class fields
    data = None

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        logger.debug("{} wrote:".format(self.client_address[0]))
        logger.debug(self.data)
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

    def intent_broker(self):
        # TODO: Read intent file and define a well-structured api endpoint
        pass


if __name__ == "__main__":
    HOST, PORT, MAGIC = "localhost", 9999, "JellySERVER"

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), TCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
