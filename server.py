import socketserver
import ssl
from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname
from config import configured_logger

logger = configured_logger.logger

from socketserver import BaseRequestHandler


class SecureTCPServer(socketserver.TCPServer):
    def __init__(self, cerfile, keyfile, server_address, RequestHandlerClass):
        self.cerfile = cerfile
        self.keyfile = keyfile
        self.server_address = server_address
        super().__init__(server_address, RequestHandlerClass)

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
        logger.debug("{} wrote: {}".format(self.client_address[0], self.data))
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

    def intent_broker(self):
        # TODO: Read intent file and define a well-structured api endpoint
        pass


class VerboseTCPServer(socketserver.TCPServer):
    def __init__(self, address, handler):
        self.address = address
        self.handler = handler
        socketserver.TCPServer.__init__(self, address, handler)

    def server_activate(self):
        logger.info("Starting server at address {}".format(self.address))
        socketserver.TCPServer.server_activate(self)
        logger.info("Server started")

    def server_close(self):
        logger.info("Shutting down server at address {}".format(self.address))
        socketserver.TCPServer.server_close(self)
        logger.info("Server stopped")


if __name__ == "__main__":

    HOST, PORT, MAGIC = "localhost", 9999, "JellySERVER"

    # Allowing to reuse same address
    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 9999
    server = VerboseTCPServer((HOST, PORT), TCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
