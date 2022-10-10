"""
A sync variant of shadow.reveal

May be used for testing purposes.
"""

import sys
import time
from functools import wraps

import greenlet

from shadow.hide import hide


def reveal(fn):
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
    @reveal
    def sleep(t):
        sleep_impl(t)

    @hide
    def sleep_impl(t):
        time.sleep(t)
        print('Sync case is working too')

    sleep(2)