# greenhack

This package allows you to mix sync and async code by means of using
[greenlet](https://github.com/python-greenlet/greenlet).

Its practical uses are [this](https://github.com/Bi-Coloured-Python-Rock-Snake/pgbackend)
async django backend and the async support in
sqlalchemy (the latter uses its own code, which this library was based upon).

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

**2. start_loop**

```python
import greenhack; greenhack.start_loop()

sleep(0.5)
download('https://www.python.org')
```

Which will print the same.


You can read more about the "mixed I/O" approach [here]().