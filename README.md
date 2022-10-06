# greenbrew

The title is a tribute to sqlalchemy.

## Install

```
pip install greenbrew
```

## Usage

Suppose you have a function that is a part of your top-level API that at some point in time calls
some deeply nested function:

```python
import time

def top_API_func():
    ...
    deeply_nested_func()
    ...

def deeply_nested_func():
    time.sleep(1)
```

Now suppose we want to replace that deeply nested function with an async one, and are ready to use the greenlet hack for it.
What we do:

```python
import asyncio
from greenbrew.asyn import green_spawn, green_async

@green_spawn
def top_API_func():
    ...
    deeply_nested_func()
    ...

@green_async
async def deeply_nested_func():
    await asyncio.sleep(1)
```

That's it: you just decorate your function at the top-level and the one you replaced. Your code remains "synchronous" 
(it just gets split between two greenlets: the sync part is executed in one greenlet and the async one in the other).
