import socketserver
import config.configured_logger

logger = config.configured_logger.logger

class TCPHandler(socketserver.BaseRequestHandler):
    """
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        logger.debug ("{} wrote:".format(self.client_address[0]))
        logger.debug (self.data)
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

    def intentBroker(self):
        # TODO: Read intent file and define a well-structured api endpoint
        pass

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), TCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
