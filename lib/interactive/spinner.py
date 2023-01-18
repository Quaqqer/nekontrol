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
        self.message = message
        self.sequence = sequence if isinstance(sequence, list) else list(sequence)
        self.stream = stream
        self.final_ok = final
        self.final_fail = final_fail

        self.result: bool | None = None
        self.thread: threading.Thread | None = None

    def __enter__(self):
        def spin():
            i = 0

            while not self.stop_running.is_set():
                self.stream.write(colored(self.sequence[i], "yellow"))
                self.stream.flush()
                self.stop_running.wait(0.25)
                n = len(self.sequence[i])
                self.stream.write("\b" * n + " " * n + "\b" * n)
                self.stream.flush()

                i = i + 1
                if len(self.sequence) <= i:
                    i = 0

        if self.message is not None:
            self.stream.write(self.message)

        if os.isatty(self.stream.fileno()):
            self.stop_running = threading.Event()
            self.thread = threading.Thread(target=spin)
            self.thread.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.thread is not None:
            self.stop_running.set()
            self.thread.join()

        if self.result is not None:
            if self.result:
                self.stream.write(colored(self.final_ok, "green"))
            else:
                self.stream.write(colored(self.final_fail, "red"))
            self.stream.flush()

        if self.message is not None:
            self.stream.write("\n")
            self.stream.flush()

    def ok(self, result=True):
        self.result = result

    def fail(self):
        self.result = False
