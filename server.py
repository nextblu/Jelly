import socketserver
import ssl
import json
import threading
import time
from pickle import loads, dumps
from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname, IPPROTO_UDP
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
    server = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    server.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    # Set a timeout so the socket does not block
    # indefinitely when trying to receive data.
    server.settimeout(0.2)
    server.bind(("", 44444))


    serverdict = {
      "ServerName": "JellySERVER",
      "ServerVersion": "0.001",
      "ServerPort": port
    }
    message = dumps(serverdict)
    #message = str.encode(message)

    logger.info("Broadcast address transmission started!")
    while True:
        server.sendto(message, ('<broadcast>', 37020))
        sleep(0.2)


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.StreamRequestHandler):
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
        self.data = loads(self.data) # Pickle utility
        logger.debug("The client ID: {} also known as {} wrote: {}".format(self.data["ClientID"], self.data["ClientAlias"], self.data["ClientMessage"]))
        # just sending back the ACK 
        self.request.sendall("k".encode())

    def intent_broker(self, query):
        # TODO: Read intent file and define a well-structured api endpoint
        pass


class VerboseTCPServer(socketserver.TCPServer):
    def __init__(self, address, handler):
        self.address = address[0]
        self.handler = handler
        socketserver.ThreadingTCPServer.__init__(self, address, handler)

    def server_activate(self):
        logger.info("Starting Threaded server at address: {}".format(self.address))
        socketserver.ThreadingTCPServer.server_activate(self)
        logger.info("Server started")

    def server_close(self):
        logger.info("Shutting down server at address {}".format(self.address))
        socketserver.ThreadingTCPServer.server_close(self)
        logger.info("Server stopped")


if __name__ == "__main__":

    HOST, MAGIC = "0.0.0.0", "JellySERVER"

    # Allowing to reuse same address
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    # keep the server alive
    socketserver.ThreadingTCPServer.terminate = False
    # Create the server, binding to localhost on default port 9999
    server = VerboseTCPServer((HOST, 0), ThreadingTCPServer)
    IP, PORT = server.server_address
    logger.info("This server is running on port: {}".format(PORT))


    #Starting service_announcement deamon
    service_announcement_thread = threading.Thread(target=service_announcement, args=(PORT, MAGIC))
    service_announcement_thread.daemon = True
    service_announcement_thread.start()

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
