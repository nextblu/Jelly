import time
import threading
import unittest

from client import SecureTCPClient
from server import SecureTCPServer, BaseRequestHandler

from config import configured_logger

logger = configured_logger.logger


class MyException(Exception):
    pass


class TCPHandler(BaseRequestHandler):
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

        # simulate error
        if self.data == b'BOOM!!!':
            raise MyException("BOOM!!!")

        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())


class TestLog:
    LOGFILE = "logs/log.out"

    @classmethod
    def reset(cls):
        open(cls.LOGFILE, "w").close()

    @classmethod
    def read(cls):
        with open(cls.LOGFILE) as f:
            return f.read()


class Test(unittest.TestCase):
    SERVER_ADDRESS = "localhost", 9999
    CERFILE = 'test/demo_ssl/server.crt'
    KEYFILE = 'test/demo_ssl/server.key'

    def setUp(self):
        TestLog.reset()
        SecureTCPServer.allow_reuse_address = True
        self.server = SecureTCPServer(self.CERFILE, self.KEYFILE, self.SERVER_ADDRESS, TCPHandler)
        self.proc = threading.Thread(target=self.server.serve_forever)
        self.proc.start()
        logger.info("wait server...")
        time.sleep(.1)

    def tearDown(self):
        logger.info("shutdown...")
        self.server.shutdown()
        logger.info("close...")
        self.server.server_close()
        logger.info("join...")
        self.proc.join()

    def test_echo(self):
        with SecureTCPClient(self.SERVER_ADDRESS, self.CERFILE) as client:
            response = client.exchange('dummy data'.encode('utf-8'))
        self.assertEqual(response, b'DUMMY DATA')

    def test_exception_is_logged(self):
        self.assertNotIn("tests.MyException: BOOM!!!", TestLog.read())
        with SecureTCPClient(self.SERVER_ADDRESS, self.CERFILE) as client:
            response = client.exchange(b'BOOM!!!')
        self.assertEqual(response, b'')
        self.assertIn("tests.MyException: BOOM!!!", TestLog.read())
