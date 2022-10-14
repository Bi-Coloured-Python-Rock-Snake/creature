# shadow

The package is responsible for the use of greenlets in the balrog project.
Be ready to the magic. Don't be surprised.

## Install

```
pip install balrog-shadow
```

## Usage

**Functions hiding in the shadow**

The story is as follows: there are functions with async implementations,
that want to hide their async nature. Why? To be called like regular functions,
without await.

How do we hide a function? By using a `hide` decorator:

```python
from greenhack import exempt


@exempt
async def sleep(secs):
    await asyncio.sleep(secs)
    return secs


@exempt
async def download(url):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return await resp.aread()
```

However, it is not enough to mark functions as hidden
(we must provide a shadow for them!)

*shadow* has 2 modes of operation: **cast** and **reveal**.

**1. Cast a shadow**

You can cast a shadow. The one your functions can be safely hidden in:

```python
import greenhack

greenhack.start_loop()

assert sleep(1) == 1
html = download('https://www.python.org/')
```

The code looks as if it was using sync I/O, but it isn't. Magic, isn't it?

This mode of operation fits best for the REPL, when you don't have
an event loop running.

**2. Reveal a function**

If you don't want to cast a shadow, you'll have to reveal your functions at some point:

```python
from greenhack import as_async


@as_async
def myfunc():
    sleep(0.1)
    html = download('https://www.python.org/')
    assert len(html) < 1024 * 1024
```

`myfunc` is a coroutine function now, so it can be run with `asyncio.run`.

This is the intended way of use, by the way: you write your code in sync style, using hidden functions.
Then you reveal the top-level function and run it:

```python
asyncio.run(myfunc())
```

Actually, hide/reveal doesn't make much sense for this snippet, since you could just use
the initial `download` function. Actually, you still can:

```python
async def myfunc():
    await sleep(0.1)
    return await download('https://www.python.org/')
```

This is the equivalent. Since we are not using neither `cast` nor `reveal`,
`shadow.hide` is a no-op in this case.
