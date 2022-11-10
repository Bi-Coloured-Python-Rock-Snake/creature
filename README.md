# greenhack

This package lets you make a bridge between yor sync and async code.
It allows for sync-looking API to have async implementation under the hood.
It does that by using
[greenlet](https://github.com/python-greenlet/greenlet).

The main principle is to separate sync and async code by two different 
greenlets. Then, all async tasks are being sent to the async greenlet and 
executed there,
while the sync greenlet doesn't do any I/O itself.

Its practical uses are
[this]((https://github.com/Bi-Coloured-Python-Rock-Snake/pgbackend))
async database backend for django, as well as
the async support in
sqlalchemy. The latter uses its own code however, which this library was based 
upon.

## Install

```
pip install greenhack
```

## Usage

You can turn an async function into a sync one by using `exempt` decorator:

```python
from greenhack import exempt

@exempt
async def sleep(secs):
    await asyncio.sleep(secs)
    print(f'Slept for {secs} seconds')

@exempt
async def download(url):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        print(f'Downloaded {len(resp.content)} bytes')
```

"Exempt" means that coroutines are exempted from the current greenlet, and 
sent to another.

Now, to call those functions you have two options: 

**1. as_async decorator**

You can use `as_async` decorator to make the main function async again and 
run it with an event loop:

```python
from greenhack import as_async

@as_async
def main():
    sleep(0.5)
    download('https://www.python.org')

asyncio.run(main())
```

Which will print

```commandline
Slept for 0.5 seconds
Downloaded 50856 bytes
```

**2. start_loop()**

You can also start an event loop yourself - this may be useful for interactive 
use or scripts.


```python
import greenhack; greenhack.start_loop()

sleep(0.5)
download('https://www.python.org')
```

Which will print the same.

**Note: start_loop() doesn't work in IPython REPL**

The reason is that IPython starts the asyncio loop itself. The 
prompt_toolkit used by IPython, also needs one. So, for IPython there is a 
different solution

```python
import greenhack; greenhack.ipy.enable()
```

This works in both PyCharm Console and IPython, while start_loop() - only in 
the PyCharm Console (even if it uses IPython).

**Context vars**

asyncio has `contextvars` module that gives coroutines access to their 
"context". greenhack has its own contextvars for the very same purpose.

Greenlet itself has support for contextvars: all greenlets have different 
contexts.
However, as you should know by now, we have two 
greenlets, sync and async, and it's natural for them to share the context.

The class intentionally is called CtxVar, not to import the standard 
ContextVar by mistake.

```python
greenhack.start_loop()

var = greenhack.context_var(__name__, 'var', default=-1)


@exempt
async def f1():
    # set() returns the previous value
    assert var.set(1) == -1


def f2():
    assert var.get() == 1


f1()
f2()
```

As you can see, sync and async functions can use shared context.

**Context managers**

Functions are not the only thing you can come across, sometimes you have to 
deal with context managers too. greenhack can map async context managers to the 
sync ones. Here is how it is done:

```python
@exempt_cm
@asynccontextmanager
async def have_rest(before, after):
    await asyncio.sleep(before)
    try:
        yield
    finally:
        await asyncio.sleep(after)

with have_rest(1, 3):
    print('Party!')
```

`exempt_cm` stays for "exempt the context manager", of course. This feature 
had been 
useful when I 
was working on the async backend for django, because the psycopg3 driver 
uses context managers extensively.

**Iterators**

You get the principle, don't you? Similarly, we have `exempt_it` for iterators.

```python
@exempt_it
async def counter():
    for i in range(3):
        await asyncio.sleep(0.1 * i)
        yield i

assert list(counter()) == [0, 1, 2]
```

Good luck with greenhack! You can read more on the "mixed I/O" approach 
[here](https://github.com/Bi-Coloured-Python-Rock-Snake/pgbackend/blob/main/mixed-io.md).