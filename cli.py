"""
Command Line Interface

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

import argparse
import logging.config
import sys

import command
import transport

try:
    import coloredlogs
    coloredlogs_install = coloredlogs.install
except ModuleNotFoundError:
    coloredlogs_install = lambda *args, **kwargs: None


DEFAULT_PORT = 5233     # jcdf (Jelly-Cavuti-De Paoli-Failla)
LOG_DEFAULT_FMT = '%(asctime)s - %(filename)s - %(levelname)s - %(message)s'
LOG_DEFAULT_DICT = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {'format': LOG_DEFAULT_FMT},
    },
    'handlers': {
        'log_stdout': {'level': 'DEBUG', 'formatter': 'standard', 'class': 'logging.StreamHandler'},
    },
    'loggers': {
        '': {'handlers': ['log_stdout'], 'level': 'DEBUG', 'propagate': True},
    }
}


class BaseInstruction:
    @classmethod
    def main(cls, module, *args):
        instruction = globals()[module.capitalize() + "Instruction"]()
        instruction._setup_arguments()
        instruction._run(*args)

    def _setup_arguments(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--logging")
        self.add_arguments(self.parser)

    def _run(self, *args):
        cli_args = self.parser.parse_args(args)
        if cli_args.logging:
            logging.config.fileConfig(cli_args.logging, disable_existing_loggers=False)
        else:
            self.default_log()
        self.handle(cli_args)

    def default_log(self):
        """ overridable in descendants """
        pass

    def add_arguments(self, parser):
        """ overridable in descendants """
        pass

    def handle(self, cli_args):
        """ overridable in descendants """
        pass


class Instruction(BaseInstruction):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--cafile")
        parser.add_argument("--server", default="localhost")
        parser.add_argument("--port", type=int, default=DEFAULT_PORT)


class ServerInstruction(Instruction):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--keyfile")
        parser.add_argument("commands_module")

    def default_log(self):
        logging.config.dictConfig(LOG_DEFAULT_DICT)
        coloredlogs_install(
            level='DEBUG', fmt="%(asctime)s - %(filename)s - %(levelname)s - %(message)s")

    def handle(self, cli_args):
        super().handle(cli_args)
        commands = command.Commands(cli_args.commands_module)
        transport.ThreadingServer.allow_reuse_address = True
        server = transport.ThreadingServer(
            cli_args.cafile, cli_args.keyfile, (cli_args.server, int(cli_args.port)), commands.apply)
        server.serve_forever()


class ClientInstruction(Instruction):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("function")
        parser.add_argument("params", nargs='*')

    def handle(self, cli_args):
        super().handle(cli_args)
        with transport.Client(cli_args.cafile, (cli_args.server, cli_args.port)) as client:
            response = client.exchange({"function": cli_args.function, "params": cli_args.params})
        print(response)


if __name__ == '__main__':
    Instruction.main(*sys.argv[1:])
