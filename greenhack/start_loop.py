import asyncio
import sys

import greenlet

from greenhack.exempt import exempt


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


def start_loop():
    """
    Start an event loop in a new greenlet that will execute
    the exempted coroutines.
    """
    current = greenlet.getcurrent()

    def run(task, current=current):
        asyncio.run(_loop(current, task))

    current.other_greenlet = greenlet.greenlet(run)



if __name__ == '__main__':
    start_loop()

    @exempt
    async def sleep(x):
        await asyncio.sleep(x)
        return x

    @exempt
    async def download(url):
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            return len(resp.aread())

    print(sleep(0.5))
    print(download('https://www.python.org/'))
