from abc import ABC, abstractmethod
from argparse import Namespace

from randrer.client.operations import OperationInterface


class CommandInterface(ABC):
    @abstractmethod
    def execute(self, namespace: Namespace):
        raise NotImplemented


class ApplyCommand(CommandInterface):
    help = 'Apply a configuration.'
    name = 'apply'
    options = (
        {
            'args': ('location',),
            'kwargs': {
                'default': None,
                'help': 'The location of a configuration file that should be applied. If location is not given, then '
                        '~/.config/randrer/randrer.config is used.',
                'nargs': '?',
                'type': str
            }
        },
        {
            'args': ('-r', '--reset'),
            'kwargs': {
                'action': 'store_true',
                'dest': 'reset',
                'help': 'After applying the configuration, reset to the previous settings after a fifteen second '
                        'timeout.'
            }
        },
        {
            'args': ('-t', '--test'),
            'kwargs': {
                'action': 'store_true',
                'dest': 'test',
                'help': 'Load the configuration without applying it to test for errors.'
            }
        },
        {
            'args': ('-d', '--do-not-reset-on-error'),
            'kwargs': {
                'action': 'store_false',
                'dest': 'reset_on_error',
                'help': 'By default, changes made by the configuration will be reset if there is an error. Use this '
                        'option to override that behavior.'
            }
        }
    )

    def __init__(
            self,
            config_loader: OperationInterface,
            config_applier: OperationInterface,
            config_reseter: OperationInterface
    ):
        self.config_loader = config_loader
        self.config_applier = config_applier
        self.config_reseter = config_reseter

    def execute(self, namespace: Namespace):
        try:
            self.config_loader.perform(namespace)
            if namespace.test is not True:
                self.config_applier.perform(namespace)
                namespace.reset is True and self.config_reseter.perform(namespace)
        except (ValueError, KeyError, FileNotFoundError) as e:
            print(e)
            namespace.reset_on_error and hasattr(namespace, 'screen_manager') and self.config_reseter.perform(namespace)


class GetOutputsCommand(CommandInterface):
    help = 'Get the names of the outputs currently connected.'
    name = 'get-outputs'
    options = ()

    def __init__(self, output_printer: OperationInterface):
        self._output_printer = output_printer

    def execute(self, namespace: Namespace):
        self._output_printer.perform(namespace)

