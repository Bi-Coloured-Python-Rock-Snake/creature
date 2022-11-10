import asyncio
from concurrent.futures import ThreadPoolExecutor

from greenhack import start_loop


def make_pool():
    return ThreadPoolExecutor(max_workers=1, initializer=create_loop)


def evaluate(co):
    return start_loop().switch(co)


def create_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


def loop_runner(co, pool=make_pool()):
    return pool.submit(evaluate, co).result()
