#!bin/python3
# -*- coding: utf-8 -*-1
import threading
import functools
import time
from downloader.ThreadSafe import SingletonMixin
from downloader.ThreadSafe import synchronized


"""
A rate limiter to ensure that only a given number of call are made
per given time interval
"""
class RateLimiter(SingletonMixin):
    """
    Constructor with 50 actions per second as default. Call setup to reconfigure
    """
    def __init__(self):
        self.rate=50.0
        self.per=1.0
        self.allowance = self.rate
        self.last_check = self.now()

    """
    Set up the rate limiter with the given number of actions in the given
    interval in seconds.
    You need to call this method first to configure the RateLimiter
    """
    def setup(self, number_actions, interval):
        if number_actions > 0.0 and number_actions < 1.0:
            raise Exception("number_actions needs to be greater or equal 1.0")
        self.rate=float(number_actions)
        self.per=float(interval)
        self.allowance = self.rate
        self.last_check = self.now()
        if self.rate < 0:
            print("set up RateLimiter: disabled (no rate limiting)")
        else:
            print("set up RateLimiter: ",self.rate," actions per ",self.per," seconds")

    def now(self):
        return time.time()

    """
    Call this method before you call your action that should respect the rate
    limit. In case the rate limit is exceeded this method blocks until the given
    number of actions per interval is fulfiled again.

    This method is thread safe. For algorithm used see:
    https://stackoverflow.com/questions/667508/whats-a-good-rate-limiting-algorithm

    This is a token bucket algorithm without queue. The bucket is allowance.
    The bucket size is rate. The allowance += … line is an optimization of adding
    a token every rate per seconds.
    """
    @synchronized
    def acquire(self):
        # return immediately if rate limit is disabled
        if self.rate<0:
            return
        # else process the acquire request, and block until token is available
        current = self.now()
        time_passed = current - self.last_check
        self.allowance += time_passed * (self.rate / self.per)
        if (self.allowance > self.rate):
            self.allowance = self.rate
        if (self.allowance < 1.0):
            # wait until next bucket is available
            time.sleep( (1-self.allowance) * (self.per/self.rate))
            # correct the last_check variable
            self.last_check+=((1-self.allowance) * (self.per/self.rate))
        else:
            self.allowance -= 1.0;
            self.last_check = current
