import argparse
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname, IPPROTO_UDP
import ssl
from time import sleep
from pickle import loads, dumps
import threading
from config import configured_logger
import uuid

import socketserver

logger = configured_logger.logger


class SecureTCPServer(socketserver.TCPServer):
    __CLIENT_ID_KEY = "ClientID"
    __client_map = {}

    __client_data = {}

    def __init__(self, cerfile, keyfile, server_address, request_handler_class):
        self.cerfile = cerfile
        self.keyfile = keyfile
        self.server_address = server_address
        super().__init__(server_address, request_handler_class)

    def verify_request(self, request, client_address):
        request_data = request.recv(4096).strip()
        request_data = loads(request_data)
        self.__client_data[client_address] = request_data
        if self.__CLIENT_ID_KEY in request_data and request_data[self.__CLIENT_ID_KEY] is not None:
            logger.debug("client_data: {}".format(request_data[self.__CLIENT_ID_KEY]))
            try:
                # logger.debug((client_data[self.__CLIENT_ID_KEY]))
                val = uuid.UUID(hex=request_data[self.__CLIENT_ID_KEY], version=4)
                return True
            except ValueError as e:
                logger.warn("Received request from {} without a valid ClientId".format(client_address), e)
                return False
        else:
            logger.warn("Received request from {} without a ClientId".format(client_address))
            return False

    def server_activate(self):
        self.ip,self.port = self.server_address
        logger.info("Starting server at address {} on port {}".format(self.ip, self.port))
        super().server_activate()
        # secure context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(self.cerfile, self.keyfile)
        self.socket = context.wrap_socket(self.socket, server_side=True)
        logger.info("Server started. Waiting for clients.")

    def handle_error(self, request, client_address):
        logger.error('-'*40)
        logger.exception('Exception happened during processing of request from %s', client_address)
        logger.error('-'*40)

    def server_close(self):
        logger.info("Shutting down server at address {}".format(self.server_address))
        super().server_close()
        logger.info("Server stopped")

    def add_client(self, client_address, uuid_string):
        logger.debug("Adding client " + client_address)
        self.__client_map[client_address] = uuid_string

    def get_request_data(self, client_address):
        logger.debug("Returning request data for address "+str(client_address))
        return self.__client_data[client_address]


class ThreadingTCPHandler(socketserver.ThreadingMixIn, socketserver.StreamRequestHandler):
    """
       It is instantiated once per connection to the server, and must
       override the handle() method to implement communication to the
       client.
    """

    def __init__(self, request, client_address, server):
        self.server = server
        self.data = None
        socketserver.StreamRequestHandler.__init__(self, request, client_address, server)

    # Instantiation of class fields
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.server.get_request_data(self.client_address)
        # self.data = loads(self.data)  # Pickle utility
        logger.debug("The client ID: {} also known as {} wrote: {}".format(self.data["ClientID"],
            self.data["ClientAlias"], self.data["ClientMessage"]))
        # just sending back the ACK
        self.request.sendall("k".encode())

    def intent_broker(self, query):
        # TODO: Read intent file and define a well-structured api endpoint
        pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog='Jserver.py',
        description=('''\
            Hey!
            With Jelly you can simply create a socket messaging system in Python.
            You can use this program to host a server which will handle all the clients.'''),
        epilog='''Please note: Jelly is currently in Alpha version.''')
    parser.add_argument('--port', nargs='?', const=5233, type=int, required=False, metavar="[1025-49150]", help='Select the port (1025-49150) address. Default is 5233.', default=5233)
    args = parser.parse_args()
    #PORT = 5233 # jcdf  =   5233 (jelly-cavuti-De Paoli-Failla)
    if args.port:
        PORT = int(args.port)
        if PORT<1025 or PORT>49150:
            logger.error("You can't bind this port: {}. Now binding the default port".format(PORT))
            PORT = 5233
            
    

    HOST, MAGIC = "0.0.0.0", "JellySERVER"
    CERFILE = 'test/demo_ssl/server.crt'
    KEYFILE = 'test/demo_ssl/server.key'

    # Allowing to reuse same address
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    # keep the server alive
    socketserver.ThreadingTCPServer.terminate = False
    # Create the server, binding to localhost on default port 9999
    server = SecureTCPServer(CERFILE, KEYFILE, (HOST, PORT), ThreadingTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
