#!bin/python3
# -*- coding: utf-8 -*-1
import threading
import functools
import time

"""
A thread safe way to access a singleton
see https://gist.github.com/werediver/4396488
"""
# Based on tornado.ioloop.IOLoop.instance() approach.
# See https://github.com/facebook/tornado
class SingletonMixin(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None
    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance

"""
Method to wrap method so they are thread safe per function
see http://theorangeduck.com/page/synchronized-python
"""
def synchronized(method):
    outer_lock = threading.Lock()
    lock_name = "__"+method.__name__+"_lock"+"__"
    def sync_method(self, *args, **kws):
        with outer_lock:
            if not hasattr(self, lock_name): setattr(self, lock_name, threading.Lock())
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)
    return sync_method
