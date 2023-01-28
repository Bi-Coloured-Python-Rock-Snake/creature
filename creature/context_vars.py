import greenlet


class NOT_PROVIDED:
    def __bool__(self):
        return False


NOT_PROVIDED = NOT_PROVIDED()


def get_contextvars():
    current = greenlet.getcurrent()
    if hasattr(current, 'async_greenlet'):
        g = current
    elif hasattr(current, 'sync_greenlet'):
        g = current.sync_greenlet
    else:
        assert False
    if not hasattr(g, '_contextvars'):
        g._contextvars = {}
    return g._contextvars


class ContextVariable:

    def __init__(self, *args, default=NOT_PROVIDED):
        assert all(isinstance(arg, str) for arg in args)
        self.name = '.'.join(args)
        self.default = default

    def get(self):
        vars = get_contextvars()
        if self.default is NOT_PROVIDED:
            return vars[self.name]
        return vars.get(self.name, self.default)

    def set(self, value):
        vars = get_contextvars()
        old_value = vars.pop(self.name, self.default)
        if value is not NOT_PROVIDED:
            vars[self.name] = value
        return old_value


context_var = ContextVariable


if __name__ == '__main__':
    from creature import exempt, start_loop, as_async

    start_loop()

    var = context_var(__name__, 'var', default=-1)

    def get_var():
        return var.get()

    @exempt
    async def f1():
        assert var.set(1) == -1

    def f2():
        assert var.get() == 1
        var.set(2)

    @exempt
    async def f3():
        value = await as_async(get_var)()
        assert value == 2

    f1()
    f2()
    f3()
