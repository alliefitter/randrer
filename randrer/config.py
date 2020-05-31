from pathlib import Path
from typing import Dict

from yaml import safe_load


class Configuration:
    _config: Dict

    def __init__(self, config_location: str = None):
        self._config_location = config_location or f'{Path.home()}/.config/randrer/randrer.yaml'
        self._load_config()
        self._validate_config()

    def _load_config(self):
        config_location = self._config_location
        try:
            with open(config_location, 'r') as file_handle:
                self._config = safe_load(file_handle)
        except FileNotFoundError:
            raise FileNotFoundError(f'No configuration was found at {config_location}') from None

    def _validate_config(self):
        config = self._config
        for required in ['layout', 'outputs']:
            if required not in config:
                raise ValueError(f'Missing required configuration, {required}')
        layout = config.get('layout')
        if layout.get('type') not in ['linear']:
            raise ValueError(f'Invalid layout type {layout.get("type")}')
        if 'arrangements' not in layout:
            raise ValueError('Missing required configuration for layout, arrangements')
        outputs = config.get('outputs')
        for output, output_config in outputs.items():
            for required in ['type', 'number']:
                if required not in output_config:
                    raise ValueError(f'Missing required configuration for output {output}, {required}')
            if 'mode' not in output_config and 'use_preferred' not in output_config:
                raise ValueError(
                    f'Missing required configuration for output {output}, must select one of mode or use_preferred'
                )
            if 'mode' in output_config and 'use_preferred' in output_config:
                raise ValueError(
                    f'Invalid configuration for output {output}, may only select one of mode or use_preferred'
                )
            if 'rotation' in output_config and output_config.get('rotation') not in (0, 90, 180, 270):
                raise ValueError(f'Invalid configuration for output {output}, rotation must be one of 0, 90, 180, 270')

    def get(self, key: str):
        if key not in self._config:
            raise KeyError(f'Invalid configuration, {key}')
        return self._config.get(key)
