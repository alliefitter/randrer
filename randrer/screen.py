from typing import List, Dict, Iterator, Type

from Xlib.ext.randr import Rotate_0
from Xlib.protocol.rq import DictWrapper

from randrer.config import Configuration
from randrer.layout import Layout, LinearLayout, LayoutInterface, LaptopLidLayoutDecorator, Arrangement
from randrer.randr_adapter import RandrAdapter
from randrer.screen_resources import Crtc, Output, Mode


class ScreenManager:
    _adapter: RandrAdapter
    _available_modes: Dict[int, Mode]
    _config: Configuration
    _crtcs: Dict[int, Crtc]
    _outputs: Dict[int, Output]
    _pending_arrangements: List[Arrangement]
    _layout_managers: Dict[str, Type[Layout]]

    def __init__(self, adapter: RandrAdapter, config: Configuration):
        self._adapter = adapter
        self._config = config
        resources = adapter.get_screen_resources()
        self._available_modes = dict(self._parse_modes(resources.modes, resources.mode_names))
        self._crtcs = dict(self._parse_crtcs(resources.crtcs))
        self._outputs = dict(self._parse_outputs(resources.outputs))
        self._layout_managers = {
            'linear': LinearLayout
        }

    @property
    def adapter(self) -> RandrAdapter:
        return self._adapter

    @property
    def available_modes(self) -> Dict[int, Mode]:
        return self._available_modes

    @property
    def config(self) -> Configuration:
        return self._config

    @property
    def crtcs(self) -> Dict[int, Crtc]:
        return self._crtcs

    @property
    def outputs(self) -> Dict[int, Output]:
        return self._outputs

    def apply_config(self):
        self._apply_to_outputs(list(self.get_connected_outputs()))

    def get_active_outputs(self) -> Iterator[Output]:
        return filter(lambda output: output.is_connected and output.current_crtc != 0, self.outputs.values())

    def get_connected_outputs(self) -> Iterator[Output]:
        return filter(lambda output: output.is_connected, self.outputs.values())

    def get_layout(self, outputs: List[Output], crtcs: Dict[int, Crtc]) -> LayoutInterface:
        layout_type = self._config.get('layout') \
            .get('type')
        layout_class = self._layout_managers[layout_type]
        layout = layout_class(
            self.config,
            outputs,
            crtcs
        )
        if any(output.get('off_on_lid_close') for output in self._config.get('outputs').values()):
            layout = LaptopLidLayoutDecorator(layout)
        return layout

    def reset(self):
        adapter = self.adapter
        resources = adapter.get_screen_resources()
        crtcs = dict(self._parse_crtcs(resources.crtcs))
        x, y = adapter.screen_size
        x_mm, y_mm = adapter.screen_size_mm
        for crtc in crtcs.values():
            self._disable_crtc_if_does_not_fit_screen(crtc, x, y)
        adapter.set_screen_size(x, y, x_mm, y_mm)
        for crtc in self.crtcs.values():
            adapter.set_crtc_config(
                crtc.id,
                crtc.x,
                crtc.y,
                crtc.mode,
                crtc.rotation,
                crtc.outputs
            )

    def _apply_to_outputs(self, outputs: List[Output]):
        adapter = self.adapter
        layout = self.get_layout(outputs, self.crtcs)
        layout.arrange()
        x, y = layout.screen_size
        x_mm, y_mm = layout.screen_size_mm
        for crtc in self.crtcs.values():
            self._disable_crtc_if_does_not_fit_screen(crtc, x, y)
        adapter.set_screen_size(x, y, x_mm, y_mm)
        arrangements = layout.arrangements
        for arrangement in arrangements:
            adapter.set_crtc_config(
                arrangement.crtc.id,
                arrangement.x,
                arrangement.y,
                arrangement.mode.id if arrangement.mode is not None else 0,
                arrangement.rotation,
                [arrangement.output.id] if arrangement.output is not None else []
            )

    def _disable_crtc(self, crtc_id: int):
        adapter = self.adapter
        adapter.set_crtc_config(
            crtc_id,
            0,
            0,
            0,
            Rotate_0,
            []
        )

    def _disable_crtc_if_does_not_fit_screen(self, crtc: Crtc, x: int, y: int):
        if crtc.mode != 0:
            mode = self.available_modes.get(crtc.mode)
            if crtc.x + mode.width > x or crtc.y + mode.height > y:
                self._disable_crtc(crtc.id)

    def _parse_crtcs(self, crtcs: List[int]):
        for crtc in crtcs:
            info = self._adapter.get_crtc_info(crtc)
            yield crtc, Crtc(
                crtc,
                info.mode,
                info.possible_outputs,
                info.outputs,
                info.rotation,
                info.width,
                info.height,
                info.x,
                info.y
            )

    def _parse_modes(self, modes: List[DictWrapper], mode_names: str):
        name_index = 0
        for mode in modes:
            name = mode_names[name_index: name_index + mode.name_length]
            name_index += mode.name_length
            yield mode.id, Mode(
                mode.id,
                name,
                mode.width,
                mode.height,
                mode.dot_clock,
                mode.h_sync_start,
                mode.h_sync_end,
                mode.h_total,
                mode.h_skew,
                mode.v_sync_start,
                mode.v_sync_end,
                mode.v_total,
                mode.name_length,
                mode.flags
            )

    def _parse_outputs(self, outputs: List[int]):
        for output in outputs:
            info = self._adapter.get_output_info(output)
            yield output, Output(
                output,
                info,
                self._available_modes
            )
