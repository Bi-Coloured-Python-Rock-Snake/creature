import asyncio
import code

import greenlet

from greenhack._loop import _loop


async def main():
    prepare_repl()
    task = greenlet.getcurrent().sync_greenlet.switch()
    await _loop(task)


def prepare_repl():
    console = code.InteractiveConsole(locals=globals())
    g = greenlet.greenlet(console.interact)
    g.async_greenlet = (current := greenlet.getcurrent())
    current.sync_greenlet = g


def repl():
    asyncio.run(main())


if __name__ == '__main__':
    repl()
