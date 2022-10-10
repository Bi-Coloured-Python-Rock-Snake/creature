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


def hide(fn):
    """
    "Hide" the async implementation of fn.

    Turns a coroutine function `fn` into a regular function.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        current = greenlet.getcurrent()

        try:
            other = current.other_greenlet
        except AttributeError:
            # not running inside a greenlet, executing it as-is
            return fn(*args, **kwargs)
        task = Task(fn, args, kwargs)
        return other.switch(task)

    return wrapper