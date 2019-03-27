#!bin/python3
# -*- coding: utf-8 -*-1
from downloader.ThreadSafe import synchronized

class Stats:

    def __init__(self):
        self.numInvalid=0
        self.numSuccess=0
        self.numFailure=0
        self.numSkipped=0

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
        print("\nSuccess: %s  Failure: %s  Invalid lines in file: %s  Skipped existing: %s Total: %s\n" % (self.numSuccess,self.numFailure,self.numInvalid,self.numSkipped,numTotal))
