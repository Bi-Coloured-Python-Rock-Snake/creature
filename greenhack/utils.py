import asyncio
from collections import deque
from contextlib import AsyncExitStack, asynccontextmanager

import greenlet


def print_stack():
    # DEBUG: Print the stacktrace of the sync greenlet.
    frame = greenlet.getcurrent().sync_greenlet.gr_frame
    while frame:
        print(frame)
        frame = frame.f_back


def pop_cm(aes: AsyncExitStack, cm=None):
    new_stack = type(aes)()
    is_sync, cb = aes._exit_callbacks.pop()
    assert not is_sync
    if cm is not None:
        assert cb.__self__ is cm
    new_stack._exit_callbacks = deque([(False, cb)])
    return new_stack


if __name__ == '__main__':
    @asynccontextmanager
    async def cm(text):
        yield
        print(text)

    async def main():
        async with AsyncExitStack() as aes:
            await aes.enter_async_context(cm(1))
            await aes.enter_async_context(cm2 := cm(2))
            await pop_cm(aes, cm2).aclose()
            aes.pop_all()  # Won't print '1'

    asyncio.run(main())