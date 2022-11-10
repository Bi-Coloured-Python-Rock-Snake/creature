import greenlet
from IPython.core.async_helpers import _pseudo_sync_runner as sync_runner, _asyncio_runner

from greenhack._loop import _loop


def loop_runner(coro):
    sync_greenlet = greenlet.greenlet(sync_runner)
    sync_greenlet.async_greenlet = (current := greenlet.getcurrent())
    current.sync_greenlet = sync_greenlet
    task = sync_greenlet.switch(coro)
    return _asyncio_runner(_loop(task))


def enable():
    from IPython.terminal.interactiveshell import TerminalInteractiveShell
    # Sorry, trio runner!
    TerminalInteractiveShell.instance().trio_runner = loop_runner


def disable():
    from IPython.terminal.interactiveshell import TerminalInteractiveShell
    TerminalInteractiveShell.instance().trio_runner = None



if __name__ == '__main__':
    from greenhack import exempt
    import asyncio

    enable()

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