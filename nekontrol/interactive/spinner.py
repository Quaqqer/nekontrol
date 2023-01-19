import os
import sys
import threading

from termcolor import colored


class Spinner:
    def __init__(
        self,
        message: str | None = None,
        sequence: list[str] | str = "⠋⠙⠚⠞⠖⠦⠴⠲⠳⠓",
        stream=sys.stdout,
        final: str = "✓",
        final_fail: str = "✗",
    ):
        self._message = message
        self._sequence = sequence if isinstance(sequence, list) else list(sequence)
        self._stream = stream
        self._final_ok = final
        self._final_fail = final_fail

        self._result: bool | None = None
        self._thread: threading.Thread | None = None
        self._stopped = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop()

    def start(self):
        def spin():
            i = 0

            while not self.stop_running.is_set():
                self._stream.write(colored(self._sequence[i], "yellow"))
                self._stream.flush()
                self.stop_running.wait(0.25)
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

    def _stop(self):
        if not self._stopped:
            self._stopped = True

            if self._thread is not None:
                self.stop_running.set()
                self._thread.join()

            if self._result is not None:
                if self._result:
                    self._stream.write(colored(self._final_ok, "green"))
                else:
                    self._stream.write(colored(self._final_fail, "red"))
                self._stream.flush()

            if self._message is not None:
                self._stream.write("\n")
                self._stream.flush()

    def ok(self, result=True):
        self._result = result

    def fail(self):
        self._result = False

    def stop(self, result: bool | None = None):
        if result is not None:
            self._result = result
        self._stop()
