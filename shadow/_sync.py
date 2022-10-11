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
        new_greenlet = greenlet.greenlet(fn)
        new_greenlet.other_greenlet = greenlet.getcurrent()

        task = new_greenlet.switch(*args, **kw)

        try:
            while True:
                if not new_greenlet:
                    return task

                try:
                    result = task()
                except:
                    task = new_greenlet.throw(*sys.exc_info())
                else:
                    task = new_greenlet.switch(result)
        finally:
            new_greenlet.other_greenlet = None

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