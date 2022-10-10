import asyncio
import sys
from functools import wraps

import greenlet

from greenbrew.base import Task


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
        target.other_g = None


def run(task):
    asyncio.run(main(task))


def green_async(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):
        other = greenlet.getcurrent().other_g
        task = Task(fn, args, kwargs)
        return other.switch(task)

    return wrapper


@green_async
async def sleep(x):
    await asyncio.sleep(x)
    return x


if __name__ == '__main__':
    current = greenlet.getcurrent()

    def run(task, current=current):
        asyncio.run(main(current, task))

    current.other_g = greenlet.greenlet(run)

    print(sleep(1.5))
