import unittest
import os
import shutil
import tempfile
import imghdr
from urllib.parse import urlparse

from downloader.Downloader import Downloader

class DownloadTest(unittest.TestCase):

    def setUp(self):
        # create temp output directory, return absolute path
        self.__downloads_temp_folder__=tempfile.mkdtemp()
        print("created ",self.__downloads_temp_folder__," to store downloads")
        # create a downloader with default params
        number_threads=4
        ratelimit_downloads=10
        ratelimit_interval=1
        verbose=False
        store_into_tar=False
        progressbar=False
        self.__downloader__ = Downloader(self.__downloads_temp_folder__, number_threads, ratelimit_downloads, ratelimit_interval,verbose,store_into_tar,progressbar)
        # test image urls file
        self.__test_urls_file="tests/test_image_urls.txt"
        # read list of urls
        with open(self.__test_urls_file) as f:
            self.__test_urls_list=[line.strip().rstrip('\n') for line in f.readlines() if line.strip().rstrip('\n')]
        # create list of image context path from urls
        self.__test_urls_image_context_path_list=list()
        for url in self.__test_urls_list:
            # extract the image context path and store in list
            self.__test_urls_image_context_path_list.append(urlparse(url).path[1:])

    def tearDown(self):
        # delete temp output directory
        print("cleanup ",self.__downloads_temp_folder__)
        shutil.rmtree(self.__downloads_temp_folder__)

#    def test_foo(self):
#        for url in self.__test_urls_list:
#            print(">"+url+"<")

    def test_simple_download_list_into_filetree(self):
        print("Running test")
        # let the downloader read the urls file and download the files
        self.__downloader__.download_list(self.__test_urls_file)
        # now we assert that each file has been downloaded and properly named
        for file in self.__test_urls_image_context_path_list:
            expected_outfile=os.path.join(self.__downloads_temp_folder__,file)
            # assert the file exists
            assert os.path.isfile(expected_outfile), "Expected that file "+expected_outfile+" exists, but it is missing."
            # and it is a real image file
            assert imghdr.what(expected_outfile) == "jpeg" or imghdr.what(expected_outfile) == "jpg" or imghdr.what(expected_outfile) == "png" , "Expected that file "+expected_outfile+" is a image, but it is of type "+imghdr.what(expected_outfile)
