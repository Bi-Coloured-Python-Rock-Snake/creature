import typing
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import wraps

import greenlet

import greenhack


class Cm(typing.NamedTuple):
    type: int
    obj: object

    ENTER = 0
    EXIT = 1


@dataclass
class ExemptCm:
    async_cm: object

    def __enter__(self):
        other = greenlet.getcurrent().async_greenlet
        cm = Cm(Cm.ENTER, self.async_cm)
        return other.switch(cm)

    def __exit__(self, exc_type, exc_val, exc_tb):
        other = greenlet.getcurrent().async_greenlet
        if exc_type:
            other.throw(exc_type, exc_val, exc_tb)
            return True
        cm = Cm(Cm.EXIT, self.async_cm)
        assert other.switch(cm) is None


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
    @exempt_cm
    @asynccontextmanager
    async def cm():
        print('<', end='')
        yield
        print('>', end='')

    greenhack.start_loop()

    with cm():
        pass
