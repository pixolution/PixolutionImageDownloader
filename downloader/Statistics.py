#!bin/python3
# -*- coding: utf-8 -*-1
from downloader.ThreadSafe import synchronized
import time

class Stats:

    def __init__(self):
        self.numInvalid=0
        self.numSuccess=0
        self.numFailure=0
        self.numSkipped=0
        self.start_time=None

    @synchronized
    def start(self):
        self.start_time=time.time()

    @synchronized
    def registerSkipped(self):
        self.numSkipped+=1

    @synchronized
    def registerInvalid(self):
        self.numInvalid+=1

    @synchronized
    def registerFailure(self):
        self.numFailure+=1

    @synchronized
    def registerSuccess(self):
        self.numSuccess+=1

    @synchronized
    def printSumUpEvery(self,count):
        numTotal=self.numSuccess+self.numFailure+self.numInvalid+self.numSkipped
        if numTotal % count == 0:
            self.printSumUp()

    @synchronized
    def printSumUp(self):
        numTotal=self.numSuccess+self.numFailure+self.numInvalid+self.numSkipped
        duration=time.time() - self.start_time
        rate=round(float(numTotal)/float(duration))
        print("Ok: %s  Fail: %s  Empty lines: %s  Skipped: %s Total: %s Running=%ss Rate=%s #/s\n" % (self.numSuccess,self.numFailure,self.numInvalid,self.numSkipped,numTotal,round(duration),rate))
        print("")

    def printStatus(self, num_total):
        print("Total: %s   Already downloaded: %s  Downloads remaining: %s\n" % (num_total,self.numSkipped,num_total-self.numSkipped))
