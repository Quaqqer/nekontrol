import os
import sys
import threading
from enum import Enum

from ..util import cw


class SpinnerResult(Enum):
    OK = 0
    FAIL = 1
    NONE = 2


class Spinner:
    def __init__(
        self,
        message: str | None = None,
        color: bool = False,
        sequence: list[str] | str = "⠋⠙⠚⠞⠖⠦⠴⠲⠳⠓",
        stream=sys.stdout,
        final: str = "✓",
        final_fail: str = "✗",
        delay: float = 0.25,
        newline: bool | None = None,
    ):
        self._message = message
        self._newline = newline if newline is not None else message is not None
        self._sequence = sequence if isinstance(sequence, list) else list(sequence)
        self._stream = stream
        self._final_ok = final
        self._final_fail = final_fail
        self._delay = delay

        self._result: SpinnerResult = SpinnerResult.NONE
        self._thread: threading.Thread | None = None
        self._stopped = False

        self._c = cw(color)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop()

    def start(self):
        def spin():
            i = 0

            while not self.stop_running.is_set():
                self._stream.write(self._c(self._sequence[i], "yellow"))
                self._stream.flush()
                self.stop_running.wait(self._delay)
                n = len(self._sequence[i])
                self._stream.write("\b" * n + " " * n + "\b" * n)
                self._stream.flush()

                i = i + 1
                if len(self._sequence) <= i:
                    i = 0

        if self._message is not None:
            self._stream.write(self._message)

        if os.isatty(self._stream.fileno()):
            self.stop_running = threading.Event()
            self._thread = threading.Thread(target=spin)
            self._thread.start()

    def _stop(self, final: str | None = None):
        if final is None:
            final = (
                self._c(self._final_ok, "green")
                if self._result
                else self._c(self._final_fail, "red")
            )

        if not self._stopped:
            self._stopped = True

            if self._thread is not None:
                self.stop_running.set()
                self._thread.join()

            if self._result is not None:
                self._stream.write(final)
                self._stream.flush()

            if self._newline:
                self._stream.write("\n")
                self._stream.flush()

    def ok(self):
        self.stop(result=SpinnerResult.OK)

    def fail(self):
        self.stop(result=SpinnerResult.FAIL)

    def stop(self, result: SpinnerResult = SpinnerResult.OK, msg: str = ""):
        m = ""
        match result:
            case SpinnerResult.OK:
                m = self._final_ok
            case SpinnerResult.FAIL:
                m = self._final_fail

        m += msg

        self._stop(m)
