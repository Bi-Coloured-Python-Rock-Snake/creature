import sys
from typing import Awaitable

import greenlet

from creature.context_managers import AsyncExitCm


async def _loop(task):
    """
    This is the loop the async greenlet executes.
    It returns when the sync greenlet dies.
    """
    sync_greenlet = greenlet.getcurrent().sync_greenlet

    while True:
        if not sync_greenlet:
            return task
        try:
            match task:
                case cm if isinstance(cm, AsyncExitCm):
                    async with cm:
                        pass
                    result = None
                case task if isinstance(task, Awaitable):
                    result = await task
                case _obj:
                    assert False
        except:
            task = sync_greenlet.throw(*sys.exc_info())
        else:
            task = sync_greenlet.switch(result)