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

from downloader.ThreadSafe import synchronized
from downloader.RateLimiter import RateLimiter
from downloader.Statistics import Stats
from downloader.TarStorage import TarStorage

from downloader.Errors import FileExists,DownloadFailed


class Downloader:

    def __init__(self,downloads_folder, number_threads, ratelimit_downloads, ratelimit_interval,verbose,store_into_tar,progressbar):
        self.downloads_folder=downloads_folder
        self.number_threads=number_threads
        self.ratelimit_downloads=ratelimit_downloads
        self.ratelimit_interval=ratelimit_interval
        self.verbose=verbose
        self.stats=Stats()
        self.store_into_tar=store_into_tar
        self.progressbar=progressbar

    """
    Download the given list of urls
    """
    def download_list(self,list_file):
        self.__init_error_url_list(list_file)
        # configure RateLimier (number_of_actions, interval)
        RateLimiter.instance().setup(self.ratelimit_downloads,self.ratelimit_interval)
        print("start downloading of list "+list_file+" with "+str(self.number_threads)+" threads")
        self.stats.start()
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
        logpath=os.path.join(self.downloads_folder,os.path.basename(list_file)+"_failed_urls.log")
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
        url=url.rstrip('\n').strip()
        if not len(url)>0:
            self.stats.registerInvalid()
            return
        if self.verbose:
            print("download_image",url)
        img_contextpath=urlparse(url).path[1:]
        try:
            if self.store_into_tar:
                self.__download_file_into_tar(img_contextpath,url)
            else:
                self.__download_file_into_filetree(img_contextpath,url)
            self.stats.registerSuccess()
        except FileExists:
            self.stats.registerSkipped()
            if self.verbose:
                print("\t<"+threading.current_thread().name+" skip existing ",url)
                self.stats.printSumUpEvery(15)
            else:
                self.stats.printSumUpEvery(100)
        except DownloadFailed:
            self.stats.registerFailure()
            self.logger.info(url)
            if self.verbose:
                print("\t<"+threading.current_thread().name+" download failed: ",url)
        except Exception as e:
            print(str(e))
            self.stats.registerFailure()
            self.logger.info(url)
            if self.verbose:
                print("\t<"+threading.current_thread().name+" unknown failure: ",url,str(e))
        finally:
            if self.verbose:
                self.stats.printSumUpEvery(25)
            else:
                if not self.progressbar:
                    self.stats.printSumUpEvery(100)

    """
    Download the given url into the tarfile
    """
    def __download_file_into_tar(self,img_contextpath,url):
        try:
            self.tarfile.getmember(img_contextpath)
            return true
        except KeyError:
            raise FileExists
        # respect the rate limit
        RateLimiter.instance().acquire()
        if self.verbose:
            print("\t<"+threading.current_thread().name+"> download ",url)
        tmp_file=tempfile.NamedTemporaryFile().name
        self.__download_file(url,tmp_file)
        self.tarfile.add(tmp_file,img_contextpath)
        os.remove(tmp_file)

    """
    Download the given url into the given outdir with context filetree structure
    """
    def __download_file_into_filetree(self,img_contextpath,url):
        # define outdir and outfile name
        outdir=os.path.join(self.downloads_folder,os.path.dirname(img_contextpath))
        outfile=os.path.join(self.downloads_folder,img_contextpath)
        if os.path.isfile(outfile):
            raise FileExists
        RateLimiter.instance().acquire()
        if self.verbose:
            print("\t<"+threading.current_thread().name+"> download ",url)
        # make sure the outfolder exists
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        self.__download_file_urlretrieve(url,outfile)

    """
    Download the given url to the given outfile using urlretrieve
    """
    def __download_file_urlretrieve(self,url,outfile):
        try:
            urllib.request.urlretrieve(url,outfile)
        except Exception as e:
            if self.verbose:
                print(str(e))
            raise DownloadFailed


    def __download_file_urlopen(self,url,outfile):
        # Download the file from `url` and save it locally under `file_name`:
        with urllib.request.urlopen(url) as response, open(outfile, 'wb') as out_file:
            data = response.read() # a `bytes` object
            out_file.write(data)


    """
    Download the given list of urls into the outfolder as filetree or tar_file
    """
    def __download_list(self,list_file):
        # open url file
        with open(list_file,'r') as urls:
            print("threadpool starts to download now")
            # start thread pool as iterateable with progress bar
            with concurrent.futures.ThreadPoolExecutor(self.number_threads) as executor:
                if self.progressbar:
                    # create list of all urls, skip emtpy lines
                    urls_list=[line.strip().rstrip('\n') for line in f.readlines() if line.strip().rstrip('\n')]
                    list(tqdm(iterable=executor.map(self.__download_image,urls_list), total=len(urls_list),disable=self.verbose))
                else:
                    for url in urls:
                        # skip emtpy lines
                        if url.strip().rstrip('\n'):
                            executor.submit(self.__download_image,url)

    """
    Read the url list, extract all image download pathes and
    check how many of them are already downloaded. Return statistics
    to stdout.
    """
    def check_status(self,list_file, downloads_folder):
        print("Check status (NOT IMPLEMENTED YET)")
