from typing import NamedTuple, List, Dict

from Xlib.ext.randr import GetOutputInfo


class Mode(NamedTuple):
    id: int
    name: str
    width: int
    height: int
    dot_clock: int
    h_sync_start: int
    h_sync_end: int
    h_total: int
    h_skew: int
    v_sync_start: int
    v_sync_end: int
    v_total: int
    name_length: int
    flags: int


class Output:
    id: int
    _name: str
    _modes: List[Mode]
    _current_crtc: int
    _crtcs: List[int]
    _mm_width: int
    _mm_height: int
    _num_preferred: int
    _connection: int
    _selected_mode: Mode

    def __init__(self, output_id: int, info: GetOutputInfo, available_modes: Dict[int, Mode]):
        self.id = output_id
        self._name = info.name
        self._modes = [available_modes.get(mode) for mode in info.modes]
        self._current_crtc = info.crtc
        self._crtcs = info.crtcs
        self._connection = info.connection
        self._mm_height = info.mm_height
        self._mm_width = info.mm_width
        self._num_preferred = info.num_preferred
        self._selected_mode = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def modes(self) -> List[Mode]:
        return self._modes

    @property
    def current_crtc(self) -> int:
        return self._current_crtc

    @property
    def crtcs(self) -> List[int]:
        return self._crtcs

    @property
    def mm_width(self) -> int:
        return self._mm_width

    @property
    def mm_height(self) -> int:
        return self._mm_height

    @property
    def num_preferred(self) -> int:
        return self._num_preferred

    @property
    def connection(self) -> int:
        return self._connection

    @property
    def selected_mode(self) -> Mode:
        if self._selected_mode is None:
            raise ValueError('No mode has been selected')
        return self._selected_mode

    @property
    def is_connected(self) -> bool:
        return self.connection == 0

    def get_mode_by_name(self, name: str) -> Mode:
        for mode in self.modes:
            if name == mode.name:
                return mode
        raise ValueError(f'No mode named {name}')

    def get_preferred_mode(self) -> Mode:
        return self.modes[self.num_preferred - 1]

    def set_mode(self, mode: Mode):
        if mode not in self.modes:
            raise ValueError(f'Invalid mode for output {self.name}')
        self._selected_mode = mode


class Crtc(NamedTuple):
    id: int
    mode: int
    possible_outputs: int
    outputs: List[int]
    rotation: int
    width: int
    height: int
    x: int
    y: int
