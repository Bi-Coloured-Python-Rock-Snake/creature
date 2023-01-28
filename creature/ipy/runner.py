import greenlet
from IPython.core.async_helpers import _pseudo_sync_runner as sync_runner, _asyncio_runner
from IPython.terminal.interactiveshell import TerminalInteractiveShell

from creature._loop import _loop
from creature.ipy.descriptor import Overridable


def loop_runner(coro):
    sync_greenlet = greenlet.greenlet(sync_runner)
    sync_greenlet.async_greenlet = (current := greenlet.getcurrent())
    current.sync_greenlet = sync_greenlet
    task = sync_greenlet.switch(coro)
    return _asyncio_runner(_loop(task))


TerminalInteractiveShell.trio_runner = Overridable(name='trio_runner')


def enable():
    TerminalInteractiveShell.trio_runner.value = loop_runner


def disable():
    TerminalInteractiveShell.trio_runner.value = None