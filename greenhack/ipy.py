import greenlet
from IPython.core.async_helpers import _pseudo_sync_runner as sync_runner, _asyncio_runner

from greenhack._loop import _loop


def loop_runner(co):
    sync_greenlet = greenlet.greenlet(sync_runner)
    sync_greenlet.async_greenlet = (current := greenlet.getcurrent())
    current.sync_greenlet = sync_greenlet
    task = sync_greenlet.switch(co)
    return _asyncio_runner(_loop(task))


def enable():
    from IPython.terminal.interactiveshell import TerminalInteractiveShell
    # Sorry, trio runner!
    TerminalInteractiveShell.instance().trio_runner = loop_runner


def disable():
    from IPython.terminal.interactiveshell import TerminalInteractiveShell
    TerminalInteractiveShell.instance().trio_runner = None
