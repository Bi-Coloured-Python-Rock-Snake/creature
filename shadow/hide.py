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


def shadow(fn=None, *, cb=None):
    """
    Make fn a shadowed function.
    (turns a coroutine function `fn` into a regular function)
    """

    def decorate(fn):
        @wraps(fn)
        def shadow_fn(*args, **kwargs):
            current = greenlet.getcurrent()

            try:
                other = current.other_greenlet
            except AttributeError:
                # not running inside a greenlet, executing it as-is
                return fn(*args, **kwargs)
            if cb:
                cb(*args, **kwargs)
            task = Task(fn, args, kwargs)
            return other.switch(task)

        return shadow_fn

    return decorate(fn) if fn else decorate


hide = shadow()