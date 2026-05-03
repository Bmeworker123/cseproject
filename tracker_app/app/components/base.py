from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor


class Component(ABC):
    """Base UI component that renders itself immediately on creation."""

    _executor = ThreadPoolExecutor(max_workers=4)

    def __init__(self, parent):
        self.parent = parent
        self.render(parent)

    @abstractmethod
    def render(self, parent):
        raise NotImplementedError

    def ui(self, callback, *args, **kwargs):
        """Run callback safely on Tkinter UI thread."""
        self.parent.after(0, lambda: callback(*args, **kwargs))

    def run_in_background(self, func, on_success=None, on_error=None):
        """Run CPU/IO work off mainloop, then marshal result to UI thread."""

        def done(future):
            try:
                result = future.result()
            except Exception as error:
                if on_error:
                    self.ui(on_error, error)
                return

            if on_success:
                self.ui(on_success, result)

        future = self._executor.submit(func)
        future.add_done_callback(done)
        return future
