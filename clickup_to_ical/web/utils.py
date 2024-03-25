import threading
import time
from typing import Tuple, Callable
from threading import Lock


class ThreadingDict:
    def __init__(self, auto_update: Tuple[Callable[[], dict], int] = None):
        self._lock = Lock()
        self._data = {}
        if auto_update is not None:
            fn = auto_update[0]
            freq = auto_update[1]

            def _tmp():
                while True:
                    _v = fn()
                    if _v is not None:
                        self.set(_v)
                    time.sleep(freq)

            threading.Thread(target=_tmp, daemon=True).start()

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
