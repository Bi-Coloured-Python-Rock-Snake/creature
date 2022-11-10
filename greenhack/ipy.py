import asyncio
from concurrent.futures import ThreadPoolExecutor

from IPython.core.async_helpers import _pseudo_sync_runner as sync_runner
from IPython.terminal.interactiveshell import TerminalInteractiveShell

from greenhack import start_loop


def thread_pool(max_workers):
    return ThreadPoolExecutor(max_workers=max_workers, initializer=init_thread)


def init_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_loop()


def loop_runner(co, pool=thread_pool(1)):
    return pool.submit(sync_runner, co).result()


def enable():
    # Sorry, trio runner!
    TerminalInteractiveShell.instance().trio_runner = loop_runner


def disable():
    TerminalInteractiveShell.instance().trio_runner = None
