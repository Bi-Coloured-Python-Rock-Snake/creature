import typing
from contextlib import asynccontextmanager
from functools import wraps
from typing import AsyncContextManager

import greenlet

import greenhack


class Cm(typing.NamedTuple):
    type: int
    obj: object

    ENTER = 0
    EXIT = 1


class ExemptCm(typing.NamedTuple):
    async_cm: AsyncContextManager

    def __enter__(self):
        other = greenlet.getcurrent().async_greenlet
        task = self.async_cm.__aenter__()
        return other.switch(task)

    def __exit__(self, exc_type, exc_val, exc_tb):
        other = greenlet.getcurrent().async_greenlet
        if exc_type:
            other.throw(exc_type, exc_val, exc_tb)
            return True
        cm = AsyncExitCm(self.async_cm)
        assert other.switch(cm) is None


class AsyncExitCm(typing.NamedTuple):
    async_cm: AsyncContextManager

    async def __aenter__(self):
        pass

    @property
    def __aexit__(self):
        return self.async_cm.__aexit__


def exempt_cm(fn=None):
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            async_cm = fn(*args, **kwargs)
            assert isinstance(async_cm, typing.AsyncContextManager)
            return ExemptCm(async_cm)

        return wrapper

    return decorate(fn) if fn else decorate


if __name__ == '__main__':
    from greenhack import exempt_cm

    @exempt_cm
    @asynccontextmanager
    async def cm():
        print('<', end='')
        yield
        print('>', end='')

    greenhack.start_loop()

    with cm():
        pass
