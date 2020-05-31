from abc import ABC, abstractmethod
from os.path import isfile
from typing import List, Tuple, Dict, NamedTuple, Optional

from Xlib.ext.randr import Rotate_0, Rotate_90, Rotate_180, Rotate_270

from randrer.config import Configuration
from randrer.screen_resources import Mode, Output, Crtc


class Arrangement(NamedTuple):
    crtc: Crtc
    x: int
    y: int
    mode: Optional[Mode]
    rotation: int
    output: Optional[Output]
    config: Dict


class LayoutInterface(ABC):
    @property
    @abstractmethod
    def arrangements(self) -> List[Arrangement]:
        raise NotImplemented

    @property
    @abstractmethod
    def is_contiguous(self):
        raise NotImplemented

    @property
    @abstractmethod
    def screen_size(self) -> Tuple[int, int]:
        raise NotImplemented

    @property
    @abstractmethod
    def screen_size_mm(self) -> Tuple[int, int]:
        raise NotImplemented

    @abstractmethod
    def arrange(self, outputs: List[Output] = None):
        raise NotImplemented


class Layout(LayoutInterface, ABC):
    _arrangements: List[Arrangement]
    _screen_x: int
    _screen_y: int
    _screen_x_mm: int
    _screen_y_mm: int

    def __init__(self, config: Configuration, outputs: List[Output], crtcs: Dict[int, Crtc]):
        self._config = config
        self._outputs = outputs
        self._crtcs = crtcs
        self._screen_x = 0
        self._screen_y = 0
        self._screen_x_mm = 0
        self._screen_y_mm = 0
        self._arrangements = []
        self._available_rotations = {
            0: Rotate_0,
            90: Rotate_90,
            180: Rotate_180,
            270: Rotate_270
        }

    @property
    def arrangements(self) -> List[Arrangement]:
        return self._arrangements

    @property
    def screen_size(self) -> Tuple[int, int]:
        return self._screen_x, self._screen_y

    @property
    def screen_size_mm(self) -> Tuple[int, int]:
        return self._screen_x_mm, self._screen_y_mm

    def _find_output(self, output_type: str, number: int):
        available_outputs = self._outputs
        output = None
        for available_output in available_outputs:
            if available_output.name.startswith(output_type) and available_output.name.endswith(str(number)):
                output = available_output
        return output

    def _find_crtc(self, output: Output):
        available_crtcs = self._crtcs
        if output.current_crtc != 0:
            crtc = available_crtcs.get(output.current_crtc)
        else:
            crtc = self._find_unused_crtc()
        return crtc

    def _find_unused_crtc(self):
        available_crtcs = self._crtcs
        for crtc_id, available_crtc in available_crtcs.items():
            if not available_crtc.outputs and available_crtc.mode == 0:
                return available_crtc
        raise ValueError('No unused crtcs')


class LinearLayout(Layout):
    _config: Configuration
    _outputs: List[Output]
    _crtcs: Dict[int, Crtc]

    @property
    def is_contiguous(self):
        x = 0
        is_contiguous = []
        for arrangement in self.arrangements:
            is_contiguous.append(x == arrangement.x)
            x += arrangement.x
        return all(is_contiguous)

    def arrange(self, outputs: List[Output] = None):
        self._arrangements = []
        self._outputs = outputs or self._outputs
        config = self._config
        output_configs = config.get('outputs')
        layout_config = config.get('layout')
        total_x = 0
        total_y = 0
        total_x_mm = 0
        total_y_mm = 0
        for arrangement in layout_config.get('arrangements'):
            output_config = output_configs.get(arrangement)
            current_output = self._find_output(output_config.get('type'), output_config.get('number'))
            if current_output is not None:
                if 'use_preferred' in output_config:
                    current_output.set_mode(current_output.get_preferred_mode())
                else:
                    current_output.set_mode(current_output.get_mode_by_name(output_config.get('mode')))
                crtc = self._find_crtc(current_output)
                rotation = crtc.rotation
                if 'rotation' in output_config:
                    rotation = self._available_rotations.get(output_config.get('rotation'))
                self._arrangements.append(
                    Arrangement(
                        crtc,
                        total_x,
                        0,
                        current_output.selected_mode,
                        rotation,
                        current_output,
                        output_config
                    )
                )
                width = current_output.selected_mode.width
                height = current_output.selected_mode.height
                width_mm = current_output.mm_width
                height_mm = current_output.mm_height
                if rotation in (Rotate_90, Rotate_270):
                    width = current_output.selected_mode.height
                    height = current_output.selected_mode.width
                    width_mm = current_output.mm_height
                    height_mm = current_output.mm_width
                total_x += width
                total_y = height if height > total_y else total_y
                total_x_mm += width_mm
                total_y_mm = height_mm if width_mm > height_mm else total_y_mm
        self._screen_x = total_x
        self._screen_y = total_y
        self._screen_x_mm = total_x_mm
        self._screen_y_mm = total_y_mm


class LayoutDecorator(LayoutInterface, ABC):
    def __init__(self, layout: LayoutInterface):
        self._layout = layout

    @property
    def arrangements(self) -> List[Arrangement]:
        return self._layout.arrangements

    @property
    def is_contiguous(self):
        return self._layout.is_contiguous

    @property
    def screen_size(self) -> Tuple[int, int]:
        return self._layout.screen_size

    @property
    def screen_size_mm(self) -> Tuple[int, int]:
        return self._layout.screen_size_mm

    def arrange(self, outputs: List[Output] = None):
        self._layout.arrange(outputs)


class LaptopLidLayoutDecorator(LayoutDecorator):
    _disabled_arrangements: List[Arrangement]
    _lid_state: str

    def __init__(self, layout: LayoutInterface):
        self._lid_state = '/proc/acpi/button/lid/LID/state'
        self._disabled_arrangements = []
        super().__init__(layout)

    @property
    def arrangements(self):
        return self._layout.arrangements + self._disabled_arrangements

    def arrange(self, outputs: List[Output] = None):
        super().arrange(outputs)
        if self._is_lid_closed():
            valid_arrangements = list(filter(lambda a: not a.config.get('off_on_lid_close'), self.arrangements))
            invalid_arrangements = filter(lambda a: a.config.get('off_on_lid_close'), self.arrangements)
            valid_arrangements != self.arrangements and self._layout.arrange([a.output for a in valid_arrangements])
            for arrangement in invalid_arrangements:
                self._disabled_arrangements.append(
                    Arrangement(
                        arrangement.crtc,
                        0,
                        0,
                        None,
                        1,
                        None,
                        arrangement.config
                    )
                )

    def _is_lid_closed(self):
        is_closed = isfile(self._lid_state)
        if is_closed:
            with open(self._lid_state, 'r') as file_handle:
                is_closed = file_handle.read().split(':')[1].strip() == 'closed'
        return is_closed
