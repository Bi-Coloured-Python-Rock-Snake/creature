# greenbrew

The name is a tribute to sqlalchemy.

## Install

```
pip install greenbrew
```

## Usage

Here is how you can get from a sync API

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