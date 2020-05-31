from argparse import ArgumentParser
from sys import argv
from typing import Tuple, Dict

from Xlib.display import Display

from randrer.client.commands import CommandInterface, ApplyCommand, GetOutputsCommand
from randrer.client.operations import ConfigLoadingOperation, ConfigApplicationOperation, ConfigResetOperation, \
    PrintOutputsOperation


class Client:

    def __init__(
            self,
            global_options: Tuple[Dict, ...],
            commands: Tuple[CommandInterface, ...],
            parser: ArgumentParser
    ):
        self.global_options = global_options
        self.commands: Tuple[CommandInterface, ...] = commands
        self.parser: ArgumentParser = parser

    def run(self, *args):
        try:
            self._run(*args)
        except KeyboardInterrupt:
            exit(0)

    def _run(self, *args):
        self._set_global_options()
        self._set_commands()
        namespace = self.parser.parse_args(*args)
        command: CommandInterface = namespace.command
        command.execute(namespace)

    def _set_commands(self):
        subparsers = self.parser.add_subparsers(
            metavar='command',
            help='A command that facilitates uploading packaged code to AWS Lambda.'
        )
        for command in self.commands:
            command_parser = subparsers.add_parser(getattr(command, 'name'), help=getattr(command, 'help'))
            self._set_command_options(command, command_parser)
            command_parser.set_defaults(
                command=command,
                **getattr(command, 'defaults') if hasattr(command, 'defaults') else {}
            )

    def _set_command_options(self, command, command_parser):
        for option in getattr(command, 'options'):
            command_parser.add_argument(*option.get('args'), **option.get('kwargs'))

    def _set_global_options(self):
        for option in self.global_options:
            self.parser.add_argument(*option.get('args'), **option.get('kwargs'))


def main():
    Client(
        (),
        (
            ApplyCommand(
                ConfigLoadingOperation(),
                ConfigApplicationOperation(Display()),
                ConfigResetOperation()
            ),
            GetOutputsCommand(PrintOutputsOperation(Display()))
        ),
        ArgumentParser()
    ).run(argv[1:])


if __name__ == '__main__':
    main()
