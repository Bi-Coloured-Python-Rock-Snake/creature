"""
Adapted from https://gist.github.com/zzzeek/a63254eedac043b3c233a0de5352f9c5
"""


import asyncio
import sys

from functools import wraps

import greenlet

from shadow.hide import hide, shadow


def reveal(fn):
    """
    Reveal the "async nature" of `fn` by returning a coroutine function.

    We make a new greenlet out of `fn`, the event loop being left outside,
    in "current" greenlet.
    """

    @wraps(fn)
    async def revealed_fn(*args, **kw):
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

    return revealed_fn


if __name__ == '__main__':
    @reveal
    def sleep(t):
        sleep_impl(t)

    @shadow()
    async def sleep_impl(t):
        await asyncio.sleep(t)
        print(f'Slept for {t} seconds')

    asyncio.run(sleep(2))