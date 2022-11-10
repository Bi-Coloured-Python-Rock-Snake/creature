from dataclasses import dataclass
from IPython.terminal.interactiveshell import TerminalInteractiveShell
import greenhack.ipy


@dataclass
class Desc:
    value: object

    def __get__(self, instance, owner):
        if instance:
            return self.value
        return self

    def __set__(self, instance, value):
        'Forbidden'


TerminalInteractiveShell.trio_runner = Desc(greenhack.loop_runner)
