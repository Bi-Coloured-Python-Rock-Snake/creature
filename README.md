# shadow

The package is responsible for the use of greenlets in the balrog project.
Be ready to the magic. Don't be surprised.

## Install

```
pip install balrog-shadow
```

## Usage

**"Hiding" (async) functions**

With shadow, async functions can be hidden:

```python
import shadow

@shadow.hide
async def sleep(secs):
    await asyncio.sleep(secs)
    return secs

@shadow.hide
async def download(url):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return await resp.aread()
```

Hidden async functions can be called like regular function (without `await`).

shadow has 2 modes of operation: **cast** and **reveal**. Actually, hidden functions
retain their magic only if one of these modes are activated. Otherwise, the `hide` decorator
is a no-op.

**1. Casting a shadow**

You cast a shadow. After that, you can use hidden functions as regular, as if they used sync I/O:

```python
import shadow
shadow.cast()

assert sleep(1) == 1
html = download('https://www.python.org/')
```

Magic, isn't it?

This mode of operation is the best fit for the REPL, when you don't have an event loop
running. Actually, `cast` is a wrapper around `asyncio.run`.

**2. Reveal a function**

If you don't want to cast a shadow, you have to reveal yourself at some point:

```python
import shadow

@shadow.reveal
def myfunc():
    sleep(0.1)
    return download('https://www.python.org/')
```

`reveal` makes a coroutine function out of a regular one, so it could be run in an event loop.

For example, you have written all your code in sync-style, using hidden functions. Now you
want to run the top-level function. You reveal it and pass to `asyncio.run`.

In the code snippet above, `myfunc` becomes a coroutine function after wrapping.
Actually, hide/reveal here don't make much sense, since we could use the initial `download` function.
Actually, we still can:

```python
async def myfunc():
    await sleep(0.1)
    return await download('https://www.python.org/')
```

This is the equivalent snippet of the previous one. As was said,
`shadow.hide` is a no-op in this case.
