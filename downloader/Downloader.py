#!bin/python3
# -*- coding: utf-8 -*-1
import os
import concurrent.futures
from threading import current_thread
from urllib.parse import urlparse
import urllib.request
import requests
import threading
from tqdm import tqdm
import logging
import tempfile
import pathlib

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
        self.only_status=False

    """
    Download the given list of urls
    """
    def download_list(self,list_file):
        # make sure outdir exists
        if not os.path.isdir(self.downloads_folder):
            pathlib.Path(self.downloads_folder).mkdir(parents=True, exist_ok=True)
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
    def __download_file(self,url):
        url=url.rstrip('\n').strip()
        if not len(url)>0:
            self.stats.registerInvalid()
            return
        img_contextpath=urlparse(url).path[1:]
        try:
            if self.store_into_tar:
                self.__download_file_into_tar(img_contextpath,url)
            else:
                self.__download_file_into_filetree(img_contextpath,url)
            self.stats.registerSuccess()
        except FileExists:
            self.stats.registerSkipped()
            if not self.only_status:
                if self.verbose:
                    print("\t<"+threading.current_thread().name+" skip existing ",os.path.join(self.downloads_folder,img_contextpath))
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
            if not self.only_status:
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
            if self.verbose:
                print("\t<"+threading.current_thread().name+"Checking for file "+img_contextpath+" in tarfile "+self.tarfile.name)
            self.tarfile.getmember(img_contextpath)
            raise FileExists
        except KeyError as e:
            if self.verbose:
                print("\t<"+threading.current_thread().name+"> KeyError ",e,", guess the file does not exist")
        # if we only inspect the status we can skip here
        if self.only_status:
            return
        # respect the rate limit
        RateLimiter.instance().acquire()
        if self.verbose:
            print("\t<"+threading.current_thread().name+"> download ",url)
        tmp_file=tempfile.NamedTemporaryFile().name
        self.__download_file_using_requests(tmp_file,url)
        self.__add_image_to_tarfile(tmp_file,img_contextpath)
        os.remove(tmp_file)

    """
    The tarfile library is not thread safe. This method synchronizes the
    write access to the tarfile to get a not-corrupted tar file as result.
    """
    @synchronized
    def __add_image_to_tarfile(self,file,context_path):
        self.tarfile.add(file,context_path)

    """
    Download the given url into the given outdir with context filetree structure
    """
    def __download_file_into_filetree(self,img_contextpath,url):
        # define outdir and outfile name
        outdir=os.path.join(self.downloads_folder,os.path.dirname(img_contextpath))
        outfile=os.path.join(self.downloads_folder,img_contextpath)
        if os.path.isfile(outfile):
            raise FileExists
        # if we only inspect the status we can skip here
        if self.only_status:
            return
        RateLimiter.instance().acquire()
        if self.verbose:
            print("\t<"+threading.current_thread().name+"> download ",url)
        # make sure the outfolder exists
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        self.__download_file_using_requests(outfile,url)


    """
    Simply download the given url to the given file path using requests lib
    """
    def __download_file_using_requests(self,outfile,url):
        try:
            # get a HTTP response object
            r = requests.get(url)
            # open output file, store data into it
            with open(outfile,'wb') as f:
                f.write(r.content)
            r.close()
        except Exception as e:
            if self.verbose:
                print(str(e))
            raise DownloadFailed

    """
    Download the given list of urls into the outfolder as filetree or tar_file
    """
    def __download_list(self,list_file):
        # open url file
        with open(list_file,'r') as urls:
            if self.only_status:
                print("threadpool starts to check already existing files now")
            else:
                print("threadpool starts to download now")
            # start thread pool as iterateable with progress bar
            with concurrent.futures.ThreadPoolExecutor(self.number_threads) as executor:
                if self.progressbar:
                    # create list of all urls, skip emtpy lines
                    urls_list=[line.strip().rstrip('\n') for line in f.readlines() if line.strip().rstrip('\n')]
                    list(tqdm(iterable=executor.map(self.__download_file,urls_list), total=len(urls_list),disable=self.verbose))
                else:
                    for url in urls:
                        # skip emtpy lines
                        if url.strip().rstrip('\n'):
                            executor.submit(self.__download_file,url)

    """
    Read the url list, extract all image download pathes and
    check how many of them are already downloaded. Return statistics
    to stdout.
    """
    def check_status(self,list_file):
        self.only_status=True
        self.stats.start()
        if self.store_into_tar:
            # check if file even exists
            tar_name=os.path.join(self.downloads_folder,os.path.basename(list_file)+"_files.tar")
            if os.path.isfile(tar_name):
                print("Tarfile "+tar_name+" exists, open it.")
                # open tarfile
                with TarStorage(list_file,self.downloads_folder) as tar:
                    self.tarfile=tar
                    self.__download_list(list_file)
            else:
                print("Tarfile "+tar_name+" does not exist, skip checking files.")
        else:
            self.__download_list(list_file)
        # read list of urls
        with open(list_file) as f:
            num_total=len([line.strip().rstrip('\n') for line in f.readlines() if line.strip().rstrip('\n')])
        self.stats.printStatus(num_total)
