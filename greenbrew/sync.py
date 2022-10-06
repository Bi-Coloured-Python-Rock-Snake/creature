"""
For comments see asyn.py
"""

import sys
import time
from functools import wraps

import greenlet

from greenbrew.base import green_await


def green_spawn(fn):
    @wraps(fn)
    def wrapper(*args, **kw):
        target = greenlet.greenlet(fn)
        target.spawning_greenlet = greenlet.getcurrent()

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
            target.spawning_greenlet = None

    return wrapper


if __name__ == '__main__':

    class Legacy:

        @green_spawn
        def sleep(self, t):
            self.sleep_impl(t)

        @green_await
        def sleep_impl(self, t):
            time.sleep(t)
            print('The sync case is supported too')


    Legacy().sleep(2)