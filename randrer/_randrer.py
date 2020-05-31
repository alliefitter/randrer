import sys
import traceback
from sys import exc_info
from time import sleep

from Xlib.display import Display

from randrer.config import Configuration
from randrer.randr_adapter import RandrAdapter
from randrer.screen import ScreenManager

d = Display()
r = RandrAdapter(d)
# print(json.dumps(r.get_screen_info()._data, indent=2, default=lambda o: str(o)))
m = ScreenManager(r, Configuration())
try:
    try:
        m.apply_config()
    except Exception as e:
        error_type, error_value, error_traceback = exc_info()
        print(error_type.__name__)
        print(str(error_value))
        print(''.join(traceback.format_exception(error_type, error_value, error_traceback)))
    finally:
        sleep(15)
        m.reset()
except Exception:
    sleep(15)

    r.set_crtc_config(65, 0, 0, 0, 1, [])
    r.set_crtc_config(63, 1920, 0, 75, 1, [69])
    r.set_crtc_config(64, 0, 0, 75, 1, [70])
    t = r.set_screen_size(3840, 1080, 530, 300)
