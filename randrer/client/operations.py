from abc import ABC, abstractmethod
from argparse import Namespace
from logging import getLogger
from time import sleep

from Xlib.display import Display

from randrer.config import Configuration
from randrer.randr_adapter import RandrAdapter
from randrer.screen import ScreenManager


class OperationInterface(ABC):
    @abstractmethod
    def perform(self, namespace: Namespace):
        raise NotImplemented


class ConfigLoadingOperation(OperationInterface):
    def perform(self, namespace: Namespace):
        location = namespace.location
        config = Configuration(location)
        namespace.config = config


class ConfigApplicationOperation(OperationInterface):
    def __init__(self, display: Display):
        self._display = display

    def perform(self, namespace: Namespace):
        config: Configuration = namespace.config if hasattr(namespace, 'config') else None
        if config is None or not isinstance(config, Configuration):
            raise ValueError(f'config must be of type {Configuration.__module__}.{Configuration.__qualname__}')

        display = self._display
        try:
            display.grab_server()
            adapter = RandrAdapter(display)
            screen_manager = ScreenManager(adapter, config)
            namespace.screen_manager = screen_manager
            screen_manager.apply_config()
        except Exception as e:
            print(e)
        finally:
            display.ungrab_server()


class ConfigResetOperation(OperationInterface):
    def perform(self, namespace: Namespace):
        screen_manager: ScreenManager = namespace.screen_manager if hasattr(namespace, 'screen_manager') else None
        if screen_manager is None or not isinstance(screen_manager, ScreenManager):
            raise ValueError(f'screen_manager must be of type {ScreenManager.__module__}.{ScreenManager.__qualname__}')

        sleep(15)
        screen_manager.reset()


class PrintOutputsOperation(OperationInterface):
    def __init__(self, display: Display):
        self._display = display

    def perform(self, namespace: Namespace):
        display = self._display
        adapter = RandrAdapter(display)
        screen_manager = ScreenManager(adapter, None)
        namespace.screen_manager = screen_manager
        for output in screen_manager.get_active_outputs():
            print(output.name)
