import asyncio
import sys

import greenlet

from greenbrew.base import green_async


async def main(target, target_return):
    try:
        while True:
            try:
                result = await target_return()
            except:
                target_return = target.throw(*sys.exc_info())
            else:
                target_return = target.switch(result)
    finally:
        target.other_greenlet = None


def run(task):
    asyncio.run(main(task))


@green_async
async def sleep(x):
    await asyncio.sleep(x)
    return x


if __name__ == '__main__':
    current = greenlet.getcurrent()

    def run(task, current=current):
        asyncio.run(main(current, task))

    current.other_greenlet = greenlet.greenlet(run)

    print(sleep(1.5))
