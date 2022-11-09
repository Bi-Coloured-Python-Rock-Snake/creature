import asyncio

import IPython
import greenlet

from greenhack._loop import _loop


async def main():
    prepare_ipython_embed()
    task = greenlet.getcurrent().sync_greenlet.switch()
    await _loop(task)


def prepare_ipython_embed():
    g = greenlet.greenlet(IPython.embed)
    g.async_greenlet = (current := greenlet.getcurrent())
    current.sync_greenlet = g


def embed():
    asyncio.run(main())


if __name__ == '__main__':
    embed()
