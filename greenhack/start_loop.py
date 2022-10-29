import asyncio
import sys

import greenlet

from greenhack import context
from greenhack.exempt import exempt


async def _loop(out, task, *, context_var):
    token = context.var.set(context_var)
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
        context.var.reset(token)


def start_loop():
    """
    Start an event loop in a new greenlet that will execute
    the exempted coroutines.
    """
    current = greenlet.getcurrent()

    context_var = context.Var()
    _token = context.var.set(context_var)

    def run(task, current=current, context_var=context_var):
        asyncio.run(_loop(current, task, context_var=context_var))

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
            return len(resp.content)

    print(sleep(0.5))
    print(download('https://www.python.org/'))