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

    @hide
    async def download(url):
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            return len(resp.aread())

    print(sleep(0.5))
    # print(download('https://www.python.org/'))
