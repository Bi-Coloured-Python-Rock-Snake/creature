import asyncio
from functools import wraps

import greenlet

from creature._loop import _loop
from creature.context_vars import get_contextvars
from creature.exempt import exempt


def as_async(fn=None):
    """
    Make a coroutine function out of fn.

    Awaiting it will execute all the exempted tasks.
    """
    def decorate(fn):
        @wraps(fn)
        async def async_fn(*args, **kw):
            # spawn a child (sync) greenlet, binding it to the current one (async)
            current = greenlet.getcurrent()
            sync_greenlet = greenlet.greenlet(fn)
            try:
                prev_sync_greenlet = current.sync_greenlet
                sync_greenlet._contextvars = dict(get_contextvars())
            except AttributeError:
                prev_sync_greenlet = None
            sync_greenlet.async_greenlet = current
            current.sync_greenlet = sync_greenlet
            # run the new greenlet
            task = sync_greenlet.switch(*args, **kw)
            try:
                return await _loop(task)
            finally:
                sync_greenlet.async_greenlet = None
                current.sync_greenlet = prev_sync_greenlet

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