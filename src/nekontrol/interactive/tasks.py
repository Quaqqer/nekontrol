from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TaskID, TextColumn


class TaskContext:
    def __init__(self, console: Console = Console()):
        self.p = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        )

    def __enter__(self, *args, **kwargs):
        self.p.__enter__(*args, **kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        self.p.__exit__(*args, **kwargs)

    def _finish_task(self, t: TaskID, msg: str, icon: str | None = None):
        self.p.print(("  " if icon is None else icon + " ") + msg, highlight=False)
        self.p.remove_task(t)
        self.p.refresh()

    def add_task(self, msg: str) -> "Task":
        t_id = self.p.add_task(msg)
        return Task(t_id, self, msg)

    def update_task(self, task_id: TaskID, *args, **kwargs):
        self.p.update(task_id, *args, **kwargs)

    @property
    def console(self) -> Console:
        return self.p.console


class Task:
    def __init__(self, task_id: TaskID, ctx: TaskContext, msg: str):
        self._task_id = task_id
        self._ctx = ctx
        self._msg = msg
        self._finished = False

    @property
    def msg(self):
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value
        self._ctx.update_task(self._task_id, description=value)

    def finish(self, message: str | None = None, icon: str | None = None):
        if self._finished:
            return

        if message is not None:
            self._msg = message

        self._ctx._finish_task(self._task_id, self._msg, icon=icon)
        self._finished = True

    def ok(self, message: str | None = None):
        self.finish(message, icon="[green]✓[/green]")

    def fail(self, message: str | None = None):
        self.finish(message, icon="[red]✗[/red]")
