import typing
from functools import wraps

import greenlet


def exempt(fn=None):
    """
    A coroutine produced by `fn` is exempted from the current greenlet
    and will be executed in another greenlet (the one with an event loop).

    After decorating, a coroutine function `fn` is turned into a regular function.
    """

    def decorate(fn):
        @wraps(fn)
        def replace_fn(*args, **kwargs):
            current = greenlet.getcurrent()
            co = fn(*args, **kwargs)
            assert isinstance(co, typing.Awaitable)
            try:
                other = current.async_greenlet
            except AttributeError:
                # Not called from a sync greenlet, returning as-is
                return co

            return other.switch(co)

        return replace_fn

    # This makes the decorator usable as both @exempt and @exempt()
    return decorate(fn) if fn else decorate

