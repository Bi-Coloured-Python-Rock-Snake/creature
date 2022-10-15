# greenhack

The package allows you to use the async I/O
without the need for async/await keywords. In other words,
it lets you write the code as if it was synchronous,
when in fact, it is not.

This is done via the greenlet hack,
that is best known from its use in sqlalchemy.



## Install

```
pip install greenhack
```

## Usage

**Greenlets**

[greenlets](https://greenlet.readthedocs.io)
can be created from python functions, the first switch to a greenlet
calls that function.
You can explicitly switch from one
greenlet to another: in that case, the execution of the first greenlet is paused,
until some greenlet switches back into it. Greenlets are like python generators,
but don't require the yield statement.

In order to do our trick, we will require 2 greenlets, a sync one and an async one.
The event loop will be running in the async greenlet.
We will be switching to the async greenlet every time we encounter a coroutine.
For that purpose, every async coroutine function should be decorated with
`exempt`:

```python
from greenhack import exempt

@exempt
async def sleep(secs):
    await asyncio.sleep(secs)
    return secs

@exempt
async def download(url):
    async with httpx.AsyncClient() as client:
        return await client.get(url)

```

A coroutine is "exempted" from the current greenlet, and put into another,
where it is executed. While a regular function takes its place.
However, you should also provide a way for exempted coroutines to execute.
There are 2 ways how you can do that.

**1. as_async wrapper**

One option is placing the `as_async` decorator over some top-level function.
This way, executing that function in an event loop will lead to the
exempted coroutines being executed upon the calls of their sync counterparts
(which they were replaced with).

```python
from greenhack import as_async

@as_async
def myfunc():
    sleep(0.1)
    resp = download('https://www.python.org/')
    assert len(resp.content) < 1024 * 1024

if __name__ == '__main__':
    asyncio.run(myfunc())
```

Here is the equivalent code:

```python
async def myfunc():
    await sleep(0.1)
    resp = await download('https://www.python.org/')
    assert len(resp.content) < 1024 * 1024

if __name__ == '__main__':
    asyncio.run(myfunc())
```

A thing to mention is that this snippet is working too:
the `exempt` decorator is a no-op without `as_async` (or the
alternative to it that is shown below).

**2. start_loop**

You can also start an event loop yourself, the one that will run the
exempted coroutines. An example, when that may be useful, is the Python REPL:

```python
import greenhack
greenhack.start_loop()

assert sleep(1) == 1
resp = download('https://www.python.org/')
```

Also, this may help to work with existing/legacy code. For example, adding the
`start_loop()` line to `manage.py` (a django-specific script) makes all of the
django cli work like a charm (with an async database driver!)

Happy hacking!