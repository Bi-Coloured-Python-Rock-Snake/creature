# shadow

The package is responsible for the use of greenlets in the balrog project.
Be ready to the magic. Don't be surprised.

## Install

```
pip install balrog-shadow
```

## Usage

**"Hiding" async functions**

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

You cast a shadow. After that all hidden functions remain hidden, that means,
you can call them as regular functions:

```python
import shadow
shadow.cast()

assert 1 == sleep(1)
assert len(download('https://www.python.org/')) > 10 * 1024
```

Magic, isn't it?

**2. Reveal a function**

Sometimes you might want to

```python
import time

def top_API_func():
    ...
    deeply_nested_func()
    ...

def deeply_nested_func():
    time.sleep(1)

if __name__ == '__main__':
    top_API_func()
```

to an async API

```python
import asyncio
from shadow import reveal, hide


@reveal
def top_API_func():
    ...
    deeply_nested_func()
    ...


@hide
async def deeply_nested_func():
    await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(top_API_func())
```

By using two decorators! You just decorate the function at the top-level and the one you made async. Your code gets split between
two greenlets: the sync part is executed in one greenlet and the async one in the other.