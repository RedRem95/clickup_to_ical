import threading
import time
from logging import getLogger
from typing import Tuple, Callable

_LOGGER = getLogger("clickup_to_ical")


class ThreadingDict:
    def __init__(self, auto_update: Tuple[Callable[[], dict], int] = None):
        self._lock = threading.Lock()
        self._data = {}
        if auto_update is not None:
            fn = auto_update[0]
            freq = auto_update[1]
            self._freq = freq

            def _tmp():
                while True:
                    try:
                        _v = fn()
                        if _v is not None:
                            self.set(_v)
                    except Exception as e:
                        _LOGGER.exception("Failed to update", e)
                    time.sleep(freq)

            threading.Thread(target=_tmp, daemon=True).start()
        else:
            self._freq = None

    @property
    def frequency(self) -> int:
        return self._freq

    def set(self, data: dict):
        with self._lock:
            self._data.clear()
            self._data.update(data)

    def __getitem__(self, k):
        r = self.get(k, None)
        if r is None:
            raise KeyError(f"Key {k} not found in dictionary")
        return r

    def get(self, k, default=None):
        with self._lock:
            return self._data.get(k, default)
