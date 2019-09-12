from concurrent.futures import ThreadPoolExecutor
from threading import BoundedSemaphore

"""
Thread pool that blocks on submit calls when the bound limit is reached. This
way we keep the memory footprint low even if a very large file is processed.

Implementation taken from:
- https://gist.github.com/frankcleary/f97fe244ef54cd75278e521ea52a697a#file-boundedexecutor-py
- https://www.bettercodebytes.com/theadpoolexecutor-with-a-bounded-queue-in-python/
"""

class BoundedExecutor:
    """
    BoundedExecutor behaves as a ThreadPoolExecutor which will block on
    calls to submit() once the limit given as "bound" work items are queued for
    execution.
    :param bound: Integer - the maximum number of items in the work queue
    :param max_workers: Integer - the size of the thread pool
    """
    def __init__(self, bound, max_workers):
        self.max_workers=max_workers
        self.bound=bound

    """
    Allows together with __exit__ to use this class in with statements.
    Open executor and semaphore
    """
    def __enter__(self):
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.semaphore = BoundedSemaphore(self.bound + self.max_workers)
        return self

    """
    Allows together with __enter__ to use this class in with statements
    Closes the thread pool
    """
    def __exit__(self, exc_type, exc_value, traceback):
        self.shutdown()

    """
    See concurrent.futures.Executor#submit
    """
    def submit(self, fn, *args, **kwargs):
        self.semaphore.acquire()
        try:
            future = self.executor.submit(fn, *args, **kwargs)
        except:
            self.semaphore.release()
            raise
        else:
            future.add_done_callback(lambda x: self.semaphore.release())
            return future

    """
    See concurrent.futures.Executor#shutdown
    """
    def shutdown(self, wait=True):
        self.executor.shutdown(wait)
