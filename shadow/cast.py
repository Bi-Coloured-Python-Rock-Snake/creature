import asyncio
import sys

import greenlet

from shadow.hide import hide


async def _loop(out, task):
    try:
        while True:
            try:
                result = await task()
            except:
                task = out.throw(*sys.exc_info())
            else:
                task = out.switch(result)
    finally:
        out.other_greenlet = None


def cast():
    """
    Cast a shadow.
    This is a magic call, after which synchronously-looking calls
    (having a "hidden" implementation)
    start to execute asynchronously.

    We make a greenlet and run the event loop in it.
    All the code after `cast()` stays on the outside, in "current" greenlet.
    """
    current = greenlet.getcurrent()

    def run(task, current=current):
        asyncio.run(_loop(current, task))

    current.other_greenlet = greenlet.greenlet(run)


if __name__ == '__main__':
    cast()

    @hide
    async def sleep(x):
        await asyncio.sleep(x)
        return x

    print(sleep(1.5))
