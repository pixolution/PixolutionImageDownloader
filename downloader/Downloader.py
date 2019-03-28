#!bin/python3
# -*- coding: utf-8 -*-1
import os
import concurrent.futures
from threading import current_thread
from urllib.parse import urlparse
import urllib.request
import threading
from tqdm import tqdm
import logging
import tempfile

from downloader.RateLimiter import RateLimiter
from downloader.Statistics import Stats
from downloader.TarStorage import TarStorage


class Downloader:

    def __init__(self,downloads_folder, number_threads, ratelimit_downloads, ratelimit_interval,verbose,store_into_tar=False):
        self.downloads_folder=downloads_folder
        self.number_threads=number_threads
        self.ratelimit_downloads=ratelimit_downloads
        self.ratelimit_interval=ratelimit_interval
        self.verbose=verbose
        self.stats=Stats()
        self.store_into_tar=store_into_tar

    """
    Download the given list of urls
    """
    def download_list(self,list_file):
        self.__init_error_url_list(list_file)
        # configure RateLimier (number_of_actions, interval)
        RateLimiter.instance().setup(self.ratelimit_downloads,self.ratelimit_interval)
        print("start downloading of list "+list_file+" with "+str(self.number_threads)+" threads")
        if self.store_into_tar:
            # tarfile storage
            with TarStorage(list_file,self.downloads_folder) as tar:
                self.tarfile=tar
                self.__download_list(list_file)
        else:
            print("store downloads into file tree: "+self.downloads_folder)
            self.__download_list(list_file)
        print("Processing finished:")
        self.stats.printSumUp()

    """
    Open a output file for the failed urls using logger (thread safe)
    """
    def __init_error_url_list(self,list_file):
        logpath=list_file+"_errors.log"
        # emtpy file
        open(logpath, 'w').close()
        self.logger = logging.getLogger('log')
        self.logger.setLevel(logging.INFO)
        ch = logging.FileHandler(logpath)
        ch.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(ch)

    """
    Download an image and pass it to the file handler that decides
    if it is stored in filetree or tarfile
    """
    def __download_image(self,url):
    #    print("download_image",url)
        img_contextpath=urlparse(url).path[1:]
        # define outdir and outfile name
        outdir=os.path.join(self.downloads_folder,os.path.dirname(img_contextpath))
        outfile=os.path.join(self.downloads_folder,img_contextpath)
        # check if it already exists
        if os.path.isfile(outfile):
            self.stats.registerSkipped()
            if self.verbose:
                print("\t<"+threading.current_thread().name+" skip existing ",url)
                self.stats.printSumUpEvery(25)
            return
        # respect the rate limit
        RateLimiter.instance().acquire()
        if self.verbose:
            print("\t<"+threading.current_thread().name+"> download ",url)
        # download the file and put into outdir
        try:
            if self.store_into_tar:
                tmp_file=tempfile.NamedTemporaryFile().name
                urllib.request.urlretrieve(url,tmp_file)
                self.tarfile.add(tmp_file,img_contextpath)
                os.remove(tmp_file)
            else:
                # make sure the outfolder exists
                if not os.path.exists(outdir):
                    os.makedirs(outdir)
                urllib.request.urlretrieve(url,outfile)
            self.stats.registerSuccess()
        except:
            self.stats.registerFailure()
            self.logger.info(url)
            if self.verbose:
                print("\t<"+threading.current_thread().name+" download failed: ",url)
        finally:
            if self.verbose:
                self.stats.printSumUpEvery(25)
            else:
                self.stats.printSumUpEvery(100)


    """
    Download the given list of urls into the outfolder as filetree or tar_file
    """
    def __download_list(self,list_file):
        # open url file
        with open(list_file,'r') as lf:
            # show tqdm progress bar (not verbose)
            urls=list()
            for line in lf:
                line=line.rstrip('\n').strip()
                if len(line)>0:
                    # create tuples list with params so we can use executor.map(funct,iteratable)
                    urls.append(line)
                else:
                    self.stats.registerInvalid()
            # start thread pool as iterateable with progress bar
            with concurrent.futures.ThreadPoolExecutor(self.number_threads) as executor:
                list(tqdm(iterable=executor.map(self.__download_image,urls), total=len(urls),disable=self.verbose))


    """
    Read the url list, extract all image download pathes and
    check how many of them are already downloaded. Return statistics
    to stdout.
    """
    def check_status(self,list_file, downloads_folder):
        print("Check status (NOT IMPLEMENTED YET)")
