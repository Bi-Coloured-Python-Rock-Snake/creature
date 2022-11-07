import greenlet


def get_contextvars():
    current = greenlet.getcurrent()
    if hasattr(current, 'async_greenlet'):
        g = current
    else:
        g = current.sync_greenlet
    if not hasattr(g, '_contextvars'):
        g._contextvars = {}
    return g._contextvars


class ContextVar:
    class NONE:
        pass

    def __init__(self, *args, default=NONE):
        assert all(isinstance(arg, str) for arg in args)
        self.name = '.'.join(args)
        self.default = default

    def get(self):
        vars = get_contextvars()
        return vars.get(self.name, self.default)

    def set(self, value):
        vars = get_contextvars()
        old_value = vars.pop(self.name, self.NONE)
        vars[self.name] = value
        return old_value


if __name__ == '__main__':
    from greenhack import exempt, start_loop
    start_loop()

    var = ContextVar(__name__, 'var')

    @exempt
    async def f1():
        assert var.set(1) == var.NONE

    def f2():
        assert var.get() == 1
        var.set(2)

    @exempt
    async def f3():
        assert var.get() == 2

    f1()
    f2()
    f3()
