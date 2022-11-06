import asyncio
import sys
from contextlib import AsyncExitStack

from functools import wraps

import greenlet

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
            new_greenlet = greenlet.greenlet(fn)
            new_greenlet.other_greenlet = greenlet.getcurrent()

            task = new_greenlet.switch(*args, **kw)

            try:
                async with AsyncExitStack() as aes:
                    while True:
                        try:
                            if not new_greenlet:
                                # Then this is the final result
                                return task
                            # if isinstance(task, Cm):
                            match task:
                                case Cm.ENTER, async_cm:
                                    result = await aes.enter_async_context(async_cm)
                                case Cm.EXIT, async_cm:
                                    _aes = pop_cm(aes, async_cm)
                                    await _aes.aclose()
                                    result = None
                                case _:
                                    result = await task()
                        except:
                            task = new_greenlet.throw(*sys.exc_info())
                        else:
                            task = new_greenlet.switch(result)
            finally:
                new_greenlet.other_greenlet = None

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