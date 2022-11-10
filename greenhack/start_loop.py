import asyncio

import greenlet

from greenhack._loop import _loop
from greenhack.exempt import exempt


#spawn_loop
def start_loop():
    """
    Start an event loop in a new greenlet that will execute
    the exempted coroutines.
    """
    current = greenlet.getcurrent()

    def run(task):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_loop(task))

    current.async_greenlet = greenlet.greenlet(run)
    current.async_greenlet.sync_greenlet = current
    return current.async_greenlet



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