# greenhack

This package allows you to mix sync and async code by means of using
[greenlet](https://github.com/python-greenlet/greenlet).

The uses of this are this async [databasebackend](https://github.
com/Bi-Coloured-Python-Rock-Snake/pgbackend)
and the async support in
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

Or you can start an event loop yourself (intended for interactive use or 
scripts).

**2. start_loop()**

```python
import greenhack; greenhack.start_loop()

sleep(0.5)
download('https://www.python.org')
```

Which will print the same.

How this is implemented: we make two greenlets, a sync and an async one. 
Whenever we meet an async operation, we switch to the async greenlet, 
execute it there, and then switch back with the result. When the sync 
greenlet dies, the async one returns the result. Simple, isn't it?

**Context vars**

asyncio has `contextvars` module that gives coroutines access to their 
"context". greenhack has its own contextvars for the very same purpose.

Actually, greenlet itself has support for contextvars: all greenlets have 
different contexts. The thing is, that is not enough for us: we have two 
greenlets, sync and async one, and it's natural for them to share the context.

```python
greenhack.start_loop()

var = greenhack.ContextVar(__name__, 'var')

@exempt
async def f1():
    # var.set returns its previous value
    assert var.set(1) == var.NONE

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

Good luck with greenhack! You can read more on the "mixed I/O" approach 
[here](https://github.com/Bi-Coloured-Python-Rock-Snake/pgbackend/blob/main/mixed-io.md).