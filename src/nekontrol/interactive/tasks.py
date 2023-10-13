from rich.progress import Progress, SpinnerColumn, TaskID, TextColumn, TimeElapsedColumn


class TaskContext:
    def __init__(self):
        self.p = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
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


class Task:
    def __init__(self, task_id: TaskID, ctx: TaskContext, msg: str):
        self._task_id = task_id
        self._ctx = ctx
        self._msg = msg

    def finish(self, message: str | None = None, icon: str | None = None):
        self._ctx._finish_task(
            self._task_id, self._msg if message is None else message, icon=icon
        )

    def ok(self, message: str | None = None):
        self.finish(message, icon="[green]✓[/green]")

    def fail(self, message: str | None = None):
        self.finish(message, icon="[red]✗[/red]")
