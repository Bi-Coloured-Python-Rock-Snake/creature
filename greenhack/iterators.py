import asyncio
import typing
from functools import wraps

from greenhack import exempt


class ExemptIt(typing.NamedTuple):
    async_it: object

    def __next__(self):
        try:
            next = exempt(self.async_it.__anext__)
            return next()
        except StopAsyncIteration:
            raise StopIteration

    def __iter__(self):
        return self


def exempt_it(fn=None):
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            async_it = fn(*args, **kwargs)
            assert isinstance(async_it, typing.AsyncIterator)
            return ExemptIt(async_it)

        return wrapper

    return decorate(fn) if fn else decorate


if __name__ == '__main__':
    import greenhack; greenhack.start_loop()

    @exempt_it
    async def counter():
        for i in range(3):
            await asyncio.sleep(0.1 * i)
            yield i

    assert list(counter()) == list(range(3))