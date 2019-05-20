"""
command line interface tests

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

import os
import subprocess
import sys
import time
import uuid
import unittest
import unittest.mock


PYTHON_EXE = sys.executable
DIR_PATH = os.path.dirname(__file__)
CLI_CMD = os.path.join(os.path.dirname(DIR_PATH), "cli.py")
LOG_INI = os.path.join(DIR_PATH, "mock_logging.ini")
SRV_CRT = os.path.join(DIR_PATH, 'demo_ssl', 'server.crt')
SRV_KEY = os.path.join(DIR_PATH, 'demo_ssl', 'server.key')


class TestCli(unittest.TestCase):

    def setUp(self):
        self.server_proc = subprocess.Popen(args=(
            PYTHON_EXE, CLI_CMD, "server", "--cafile", SRV_CRT, "--keyfile", SRV_KEY,
            "tests.mock_commands"
        ))
        time.sleep(.2)

    def tearDown(self):
        self.server_proc.kill()
        self.server_proc.wait()
        time.sleep(.2)

    def test_echo(self):
        proc = subprocess.run(stdout=subprocess.PIPE, args=(
            PYTHON_EXE, CLI_CMD, "client", "--cafile", SRV_CRT, "echo", "Hi! It's me!"))
        self.assertEqual(b"Hi! It's me!\n", proc.stdout)

    def test_no_arguments(self):
        proc = subprocess.run(stdout=subprocess.PIPE, args=(
            PYTHON_EXE, CLI_CMD, "client", "--cafile", SRV_CRT, "uuid"))
        uuid_str = str(proc.stdout[:-1], "utf8")
        # check if it is a valid uuid4
        uuid.UUID(uuid_str, version=4)

    def test_many_arguments(self):
        proc = subprocess.run(stdout=subprocess.PIPE, args=(
            PYTHON_EXE, CLI_CMD, "client", "--cafile", SRV_CRT, "maximum", "23", "12", "987", "99"))
        self.assertEqual(b"99\n", proc.stdout)

    def test_automatic_cast_to_string(self):
        proc = subprocess.run(stdout=subprocess.PIPE, args=(
            PYTHON_EXE, CLI_CMD, "client", "--cafile", SRV_CRT, "maxsize"))
        self.assertEqual(b"9223372036854775807\n", proc.stdout)

    def test_hackinggggggggg(self):
        proc = subprocess.run(stderr=subprocess.PIPE, args=(
            PYTHON_EXE, CLI_CMD, "client", "--cafile", SRV_CRT, "exit"), )
        self.assertIn(b"JSONDecodeError", proc.stderr)

    def test_optional_port_and_logging(self):
        proc = subprocess.run(stdout=subprocess.PIPE, args=(
            PYTHON_EXE, CLI_CMD, "client", "--cafile", SRV_CRT, "echo", "Hi! It's me!",
            "--logging", LOG_INI))
        self.assertIn(b"Hi! It's me!", proc.stdout)
        self.assertIn(b"CLIENT received: Hi!", proc.stdout)

