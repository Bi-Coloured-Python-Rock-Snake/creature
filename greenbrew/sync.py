"""
For comments see asyn.py
"""

import sys
import time
from functools import wraps

import greenlet

from greenbrew.base import green_async


def green_spawn(fn):
    @wraps(fn)
    def wrapper(*args, **kw):
        target = greenlet.greenlet(fn)
        target.other_greenlet = greenlet.getcurrent()

        target_return = target.switch(*args, **kw)

        try:
            while True:
                if not target:
                    return target_return

                try:
                    result = target_return()
                except:
                    target_return = target.throw(*sys.exc_info())
                else:
                    target_return = target.switch(result)
        finally:
            target.other_greenlet = None

    return wrapper


if __name__ == '__main__':
    @green_spawn
    def sleep(t):
        sleep_impl(t)

    @green_async
    def sleep_impl(t):
        time.sleep(t)
        print('Sync case is working too')

    sleep(2)