import socketserver
from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname
import config.configured_logger

logger = config.configured_logger.logger

def ServiceAnnouncement(HOST, PORT, MAGIC):
    s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
    s.bind(('', 0))
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #this is a broadcast socket
    my_ip= gethostbyname(gethostname()) #get our IP. Be careful if you have multiple network interfaces or IPs

    while 1:
        data = MAGIC+my_ip
        s.sendto(data, ('<broadcast>', PORT))
        print "sent service announcement"
        sleep(5)


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
    HOST, PORT, MAGIC = "localhost", 9999, "JellySERVER"

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), TCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
