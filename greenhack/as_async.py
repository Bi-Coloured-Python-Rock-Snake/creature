import asyncio
import sys

from functools import wraps

import greenlet

from greenhack.exempt import exempt


def as_async(fn):
    """
    Make a coroutine function out of fn.

    Awaiting it will execute all the exempted tasks.
    """

    @wraps(fn)
    async def async_fn(*args, **kw):
        new_greenlet = greenlet.greenlet(fn)
        new_greenlet.other_greenlet = greenlet.getcurrent()

        task = new_greenlet.switch(*args, **kw)

        try:
            while True:
                if not new_greenlet:
                    # Then this is the final result
                    return task

                try:
                    result = await task()
                except:
                    task = new_greenlet.throw(*sys.exc_info())
                else:
                    task = new_greenlet.switch(result)
        finally:
            new_greenlet.other_greenlet = None

    return async_fn


if __name__ == '__main__':
    @as_async
    def sleep(t):
        sleep_impl(t)

    @exempt
    async def sleep_impl(t):
        await asyncio.sleep(t)
        print(f'Slept for {t} seconds')

    asyncio.run(sleep(2))