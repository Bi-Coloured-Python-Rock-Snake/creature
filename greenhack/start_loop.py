import asyncio
import sys
from contextlib import AsyncExitStack

import greenlet

from greenhack.cm import Cm
from greenhack.exempt import exempt
from greenhack.utils import pop_cm


async def _loop(out, task):
    try:
        async with AsyncExitStack() as aes:
            while True:
                try:
                    match task:
                        case Cm.ENTER, async_cm:
                            result = await aes.enter_async_context(async_cm)
                        case Cm.EXIT, async_cm:
                            _aes = pop_cm(aes, async_cm)
                            await _aes.aclose()
                            result = None
                        case _:
                            result = await task()  # FIXME
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
    current.other_greenlet._other_greenlet = current



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
            return len(resp.content)

    print(sleep(0.5))
    print(download('https://www.python.org/'))