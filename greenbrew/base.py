import typing
from functools import wraps

import greenlet


class Task(typing.NamedTuple):
    fn: object
    args: tuple
    kwargs: dict

    def __call__(self):
        fn, args, kw = self
        return fn(*args, **kw)


def green_async(fn):
    """
    Turns a coroutine function `fn` into a regular function
    by making a task out of it and sending it to the parent greenlet for execution.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        current = greenlet.getcurrent()

        try:
            spawning = current.spawning_greenlet
        except AttributeError:
            # not running inside a greenlet, executing it as-is
            return fn(*args, **kwargs)
        task = Task(fn, args, kwargs)
        return spawning.switch(task)

    return wrapper