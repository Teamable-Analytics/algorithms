from threading import Thread


class ThreadWithReturnValue(Thread):
    def __init__(
        self, *args, **kwargs
    ):
        Thread.__init__(self, *args, **kwargs)
        self._return = None

    def run(self):
        try:
            if self._target:
                self._return = self._target(*self._args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs

    def join(self, *args) -> any:
        Thread.join(self, *args)
        return self._return
