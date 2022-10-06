"""
Adapted from https://gist.github.com/zzzeek/a63254eedac043b3c233a0de5352f9c5
"""


import asyncio
import sys

from functools import wraps

import greenlet

from greenbrew.base import green_async


def green_spawn(fn):
    """
    Spawn function `fn` in a new greenlet.
    The current greenlet becomes parent to the new one.
    Async tasks are executed in the parent greenlet, and the results are sent to the child one.
    """

    @wraps(fn)
    async def wrapper(*args, **kw):
        target = greenlet.greenlet(fn)
        target.spawning_greenlet = greenlet.getcurrent()

        # this may be either a task or the final result
        target_return = target.switch(*args, **kw)

        try:
            while True:
                if not target:
                    return target_return

                try:
                    result = await target_return()
                except:
                    target_return = target.throw(*sys.exc_info())
                else:
                    target_return = target.switch(result)
        finally:
            target.spawning_greenlet = None

    return wrapper


if __name__ == '__main__':
    """
    Here you can see how the legacy codebase using sync I/O
    can be put to work in async context without a rewrite.
    
    In the example below `sleep` directly calls `sleep_impl`,
    but `sleep_impl` actually can be any function that gets called at some time
    that we want to replace with an async one.
    """

    class Legacy:

        @green_spawn
        def sleep(self, t):
            self.sleep_impl(t)

        # def sleep_impl(self, t):
        #     time.sleep(t)
        #     print(f'Slept for {t} seconds')

        @green_async
        async def sleep_impl(self, t):
            await asyncio.sleep(t)
            print(f'Slept for {t} seconds')


    asyncio.run(
        Legacy().sleep(2)
    )