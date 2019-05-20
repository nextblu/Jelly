"""
transport module tests

MIT License

Copyright (c) 2019 Marco De Paoli

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
import logging.config
import os
import time
import threading
import unittest
import unittest.mock

from transport import Client, ThreadingServer

DIR_PATH = os.path.dirname(__file__)
LOG_PATH = os.path.join(DIR_PATH, "tmp", "log.out")
CER_PATH = os.path.join(DIR_PATH, 'demo_ssl', 'server.crt')
KEY_PATH = os.path.join(DIR_PATH, 'demo_ssl', 'server.key')

logger = logging.getLogger(__name__)
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(filename)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'log_stdout': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'log_file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': LOG_PATH,
        },
    },
    'loggers': {
        '': {
            'handlers': ['log_stdout', 'log_file'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
})


def log_read():
    with open(LOG_PATH) as f:
        return f.read()


class TestTransport(unittest.TestCase):
    SERVER_CLASS = ThreadingServer
    SERVER_ADDRESS = "localhost", 9999

    def setUp(self):
        open(LOG_PATH, "w").close()  # reset log
        self.SERVER_CLASS.allow_reuse_address = True
        self.server = self.SERVER_CLASS(CER_PATH, KEY_PATH, self.SERVER_ADDRESS, None)
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

    @unittest.mock.patch("transport.Envelops.MIDDLEWARE", [])
    def test_echo_upper(self):
        self.server.action = lambda data: data.upper()
        with Client(CER_PATH, self.SERVER_ADDRESS) as client:
            response = client.exchange('dummy data'.encode('utf-8'))
        self.assertEqual(response, b'DUMMY DATA')

    @unittest.mock.patch("transport.Envelops.MIDDLEWARE", [])
    def test_exception_is_logged(self):
        class MyException(Exception):
            pass

        def mock_action(data):
            raise MyException("BOOM!!!")

        self.server.action = mock_action
        self.assertNotIn("MyException: BOOM!!!", log_read())
        with Client(CER_PATH, self.SERVER_ADDRESS) as client:
            response = client.exchange(b'BOOM!!!')
        self.assertEqual(response, b'')
        self.assertIn("MyException: BOOM!!!", log_read())

    @unittest.mock.patch("transport.Envelops.MIDDLEWARE", [])
    def test_medium_request(self):
        self.server.action = lambda data: data
        with Client(CER_PATH, self.SERVER_ADDRESS) as client:
            response = client.exchange((b'#' * 2048))
        self.assertEqual(response, b'#' * 2048)

    @unittest.mock.patch("transport.Envelops.MIDDLEWARE", [])
    def test_huge_request(self):
        self.server.action = lambda data: data
        with Client(CER_PATH, self.SERVER_ADDRESS) as client:
            response = client.exchange((b'#' * 10000))
        self.assertEqual(response, b'#' * 10000)

    @unittest.mock.patch("transport.Envelops.MIDDLEWARE", [])
    def test_no_terminator_in_data(self):
        self.server.action = None
        with Client(CER_PATH, self.SERVER_ADDRESS) as client:
            with self.assertRaises(Exception) as ex:
                client.exchange(b'12345\n67890')
            self.assertIn("Terminator found", str(ex.exception))

    def test_exchange_json_utf8_data(self):
        def mock_json_action(request):
            def transform(value):
                return value.upper() if isinstance(value, str) else value

            return {k: transform(v) for k, v in request.items()}

        self.server.action = mock_json_action
        with Client(CER_PATH, self.SERVER_ADDRESS) as client:
            response = client.exchange({
                "field_a": "value_a_àì", "field_b": ["value_b_1", "value_b_2"]})
        self.assertEqual(
            response, {'field_a': 'VALUE_A_ÀÌ', 'field_b': ['value_b_1', 'value_b_2']})

    def test_no_terminator_in_json(self):
        self.server.action = lambda request: request
        with Client(CER_PATH, self.SERVER_ADDRESS) as client:
            response = client.exchange({"field_a": "value \n with newline"})
        self.assertEqual(response, {"field_a": "value \n with newline"})

    def test_two_clients(self):
        self.server.action = lambda request: request
        with Client(CER_PATH, self.SERVER_ADDRESS) as c1:
            with Client(CER_PATH, self.SERVER_ADDRESS) as c2:
                response = c1.exchange({"field_1": "value_a"})
                self.assertEqual(response, {"field_1": "value_a"})
                response = c2.exchange({"field_1": "value_b"})
                self.assertEqual(response, {"field_1": "value_b"})
