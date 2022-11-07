import asyncio
import sys
from contextlib import AsyncExitStack

from functools import wraps

import greenlet

from greenhack._loop import _loop
from greenhack.cm import Cm
from greenhack.exempt import exempt
from greenhack.utils import pop_cm


def as_async(fn=None):
    """
    Make a coroutine function out of fn.

    Awaiting it will execute all the exempted tasks.
    """
    def decorate(fn):
        @wraps(fn)
        async def async_fn(*args, **kw):
            sync_greenlet = greenlet.greenlet(fn)
            sync_greenlet.async_greenlet = current = greenlet.getcurrent()
            current.sync_greenlet = sync_greenlet
            task = sync_greenlet.switch(*args, **kw)
            try:
                return await _loop(sync_greenlet, task)
            finally:
                sync_greenlet.async_greenlet = None
                current.sync_greenlet = None

        return async_fn

    return decorate(fn) if fn else decorate


if __name__ == '__main__':
    @as_async
    def sleep(t):
        sleep_impl(t)

    @exempt
    async def sleep_impl(t):
        await asyncio.sleep(t)
        print(f'Slept for {t} seconds')

    asyncio.run(sleep(2))