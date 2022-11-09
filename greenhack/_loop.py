import sys
from contextlib import AsyncExitStack

import greenlet

from greenhack.context_managers import Cm
from greenhack.utils import pop_cm


async def _loop(task):
    """
    This is the loop the async greenlet executes.
    It returns when the sync greenlet dies.
    """
    sync_greenlet = greenlet.getcurrent().sync_greenlet

    async with AsyncExitStack() as aes:
        while True:
            if not sync_greenlet:
                return task
            try:
                match task:
                    case Cm.ENTER, async_cm:
                        result = await aes.enter_async_context(async_cm)
                    case Cm.EXIT, async_cm:
                        _aes = pop_cm(aes, async_cm)
                        await _aes.aclose()
                        result = None
                    case _:
                        result = await task
            except:
                task = sync_greenlet.throw(*sys.exc_info())
            else:
                task = sync_greenlet.switch(result)