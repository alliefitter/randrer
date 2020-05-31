from time import time
from typing import List

from Xlib.display import Display
from Xlib.ext.randr import extname, GetOutputPrimary, GetScreenInfo, GetScreenResources, GetScreenResourcesCurrent, \
    GetCrtcInfo, GetCrtcTransform, GetOutputInfo, GetPanning, ListOutputProperties, QueryOutputProperty, SetCrtcConfig, \
    SetPanning, _1_0SetScreenConfig, SetScreenSize
from Xlib.xobject.drawable import Window


class RandrAdapter:
    display: Display
    window: Window

    def __init__(self, display: Display):
        self.display = display
        screen = display.screen()
        self.window = screen.root

    @property
    def extension_name(self):
        return extname

    @property
    def screen_size(self):
        screen = self.display.screen()
        return screen.width_in_pixels, screen.height_in_pixels

    @property
    def screen_size_mm(self):
        screen = self.display.screen()
        return screen.width_in_mms, screen.height_in_mms

    def get_primary_output(self):
        return GetOutputPrimary(
            display=self.window.display,
            opcode=self.window.display.get_extension_major(self.extension_name),
            window=self.window
        )

    def get_screen_info(self):
        return GetScreenInfo(
            display=self.window.display,
            opcode=self.window.display.get_extension_major(self.extension_name),
            window=self.window
        )

    def get_screen_resources(self):
        return GetScreenResources(
            display=self.window.display,
            opcode=self.window.display.get_extension_major(self.extension_name),
            window=self.window
        )

    def get_screen_resources_current(self):
        return GetScreenResourcesCurrent(
            display=self.window.display,
            opcode=self.window.display.get_extension_major(extname),
            window=self.window,
        )

    def get_crtc_info(self, crtc_id: int):
        return GetCrtcInfo(
            display=self.window.display,
            opcode=self.window.display.get_extension_major(self.extension_name),
            crtc=crtc_id,
            config_timestamp=0
        )

    def get_crtc_transform(self, crtc_id: int):
        return GetCrtcTransform(
            display=self.display.display,
            opcode=self.display.display.get_extension_major(extname),
            crtc=crtc_id,
        )

    def get_output_info(self, output_id: int):
        return GetOutputInfo(
            display=self.window.display,
            opcode=self.window.display.get_extension_major(self.extension_name),
            output=output_id,
            config_timestamp=0
        )

    def get_panning(self, crtc_id: int):
        return GetPanning(
            display=self.display.display,
            opcode=self.display.display.get_extension_major(extname),
            crtc=crtc_id,
        )

    def list_output_properties(self, output_id: int):
        return ListOutputProperties(
            display=self.display.display,
            opcode=self.display.display.get_extension_major(extname),
            output=output_id,
        )

    def query_output_property(self, output_id, atom):
        return QueryOutputProperty(
            display=self.display.display,
            opcode=self.display.display.get_extension_major(extname),
            output=output_id,
            property=atom,
        )

    def set_crtc_config(self, crtc_id: int, x: int, y: int, mode: int, rotation: int, outputs: List[int]):
        current_info = self.get_crtc_info(crtc_id)
        return SetCrtcConfig(
            display=self.display.display,
            opcode=self.display.display.get_extension_major(extname),
            crtc=crtc_id,
            config_timestamp=current_info.timestamp,
            x=x,
            y=y,
            mode=mode,
            rotation=rotation,
            outputs=outputs,
            timestamp=int(time())
        )

    def set_panning(
            self,
            crtc_id: int,
            left: int = None,
            top: int = None,
            width: int = None,
            height: int = None,
            track_left: int = None,
            track_top: int = None,
            track_width: int = None,
            track_height: int = None,
            border_left: int = None,
            border_top: int = None,
            border_right: int = None,
            border_bottom: int = None
    ):
        current_panning = self.get_panning(crtc_id)
        return SetPanning(
            display=self.display.display,
            opcode=self.display.display.get_extension_major(extname),
            crtc=crtc_id,
            left=left if left is not None else current_panning.left,
            top=top if top is not None else current_panning.top,
            width=width if width is not None else current_panning.width,
            height=height if height is not None else current_panning.height,
            track_left=track_left if track_left is not None else current_panning.track_left,
            track_top=track_top if track_top is not None else current_panning.track_top,
            track_width=track_width if track_width is not None else current_panning.track_width,
            track_height=track_height if track_height is not None else current_panning.track_height,
            border_left=border_left if border_left is not None else current_panning.border_left,
            border_top=border_top if border_top is not None else current_panning.border_top,
            border_right=border_right if border_right is not None else current_panning.border_right,
            border_bottom=border_bottom if border_bottom is not None else current_panning.border_bottom,
            timestamp=int(time())
        )

    def set_screen_config(self, size_id: int, rotation: int, rate: int = 0):
        info = self.get_screen_info()
        return _1_0SetScreenConfig(
            display=self.window.display,
            opcode=self.window.display.get_extension_major(extname),
            drawable=self.window,
            timestamp=int(time()),
            config_timestamp=info.config_timestamp,
            size_id=size_id,
            rotation=rotation
        )

    def set_screen_size(
            self,
            width: int,
            height: int,
            width_in_millimeters: int = None,
            height_in_millimeters: int = None
    ):
        return SetScreenSize(
            display=self.window.display,
            opcode=self.window.display.get_extension_major(extname),
            window=self.window,
            width=width,
            height=height,
            width_in_millimeters=width_in_millimeters,
            height_in_millimeters=height_in_millimeters,
        )
