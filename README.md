# greenhack

The package implements the greenlet hack that allows to use the async I/O
without the need to use the async/await keywords.

The hack is best known from its use in sqlalchemy for enabling
the async database drivers like asyncpg.

## Install

```
pip install greenhack
```

## Usage

**The exempt decorator**

Here is how the greenlet magic works: the code is split between two greenlets. The async
code goes in the second greenlet, the one where the event loop is being run.

The async coroutine function, decorated with @exempt,
makes the coroutine be exempted from the current greenlet and be executed in the
async greenlet. An example:

```python
from greenhack import exempt

@exempt
async def sleep(secs):
    await asyncio.sleep(secs)
    return secs
```

However, in order for exempted coroutine to be able to be executed as a regular
function, that should be enabled by the further code. There are 2 ways of doing that:

**1. start_loop**

Start an event loop to execute exempted coroutines in it. Suits cases when the loop
is not running already (for example, when you launched REPL):

```python
import greenhack

@greenhack.exempt
async def download(url):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return await resp.aread()

if __name__ = '__main__':
    greenhack.start_loop()
    
    assert sleep(1) == 1
    html = download('https://www.python.org/')
```

This code looks as if it is using sync I/O, but it isn't. Magic, isn't it?

**2. as_async decorator**

Another way is decorating the top function with `@as_async`.
In that case, awaiting the resultant coroutine will lead to
executing of the exempted coroutines as well:

```python
from greenhack import as_async

@as_async
def myfunc():
    sleep(0.1)
    html = download('https://www.python.org/')
    assert len(html) < 1024 * 1024

if __name__ == '__main__':
    asyncio.run(myfunc())
```

This is the most expected way of use: you write your code using sync-style calls,
then you wrap the top function and pass it to whatever async runner you have.