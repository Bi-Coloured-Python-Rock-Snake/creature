# greenhack

## Intro

This library demonstrates the use of **greenlet as a bridge to async 
code**. It can make code written for blocking I/O to work with async I/O.
An example can be an ORM that previously used blocking 
database drivers and 
starts using an async database driver.

Actually, it was not intended as a demo from the start - it was intended to be
used in production, therefore the code quality is good. Actually, I have 
written an 
async 
django database [backend](https://github.com/Bi-Coloured-Python-Rock-Snake/pgbackend) using it.

The same approach is used by sqlalchemy to provide its async features, however, 
this library is more advanced in terms of features as it provides support 
for REPL, context managers, iterators, context vars.

However, I decided to discontinue it. The thing is there are two approaches to 
async programming: one uses 
the "colored 
functions" (first made known by a [post](https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/) of Bob Nystrom)
and the other one does not. A vivid example is Python vs. Ruby: Python 
coroutines are colored and Ruby Fibers (appeared in 1.9) are not.

As you can 
see, this repository is placed in the "Bi-Coloured-Python-Rock-Snake" group. 
When I titled it that way, I considered function colors a bad thing, however I 
have come to a conclusion that the matter of things is far from 
unambiguity. There 
are many nuances to this but shortly speaking, I embraced the Python way of 
things.

Still, the library can be a nice demo of what sqlalchemy is doing under the 
hood.

## Description

This library makes it possible for the regular (sync-looking) functions to have 
async 
implementation under the hood.
It does that by using
[greenlet](https://github.com/python-greenlet/greenlet).

The main principle is to separate sync and async code by two different 
greenlets. Then, all async tasks are being sent to the async greenlet and 
executed there,
while the sync greenlet doesn't do any I/O itself.

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

**Note:** *start_loop() doesn't work in IPython REPL*

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

greenlet itself has support for contextvars: all greenlets have different 
contexts.
However, as you should know by now, we have two 
greenlets, sync and async, and it's natural for them to share the context.

The class intentionally is called context_var, not to import the standard 
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
