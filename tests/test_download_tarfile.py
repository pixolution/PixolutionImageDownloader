import unittest
import os
import shutil
import tempfile
import imghdr
import subprocess
from urllib.parse import urlparse

from downloader.Downloader import Downloader

class DownloadTestTarfile(unittest.TestCase):

    def setUp(self):
        # create temp output directory, return absolute path
        self.__downloads_temp_folder__=tempfile.mkdtemp()
        print("created ",self.__downloads_temp_folder__," to store downloads")
        # create a downloader with default params
        number_threads=12
        ratelimit_downloads=60
        ratelimit_interval=1
        verbose=True
        store_into_tar=True
        progressbar=False
        self.__downloader__ = Downloader(self.__downloads_temp_folder__, number_threads, ratelimit_downloads, ratelimit_interval,verbose,store_into_tar,progressbar)
        # test image urls file
        self.__test_urls_file="tests/test_image_urls_800.txt"
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

    def test_simple_download_list_into_tar(self):
        # let the downloader read the urls file and download the files
        self.__downloader__.download_list(self.__test_urls_file)
        # now there should be a tar file in the download folder
        tarfile=os.path.join(self.__downloads_temp_folder__,os.path.basename(self.__test_urls_file))+"_files.tar"
        assert os.path.isfile(tarfile), "Expected tar file "+tarfile+" exists but it is missing."
        # extract the content using linux OS tools
        subprocess.call(["tar", "xf", tarfile,"-C",self.__downloads_temp_folder__])
        files_missing=0
        files_corrupt=0
        files_ok=0
        number_urls=len(self.__test_urls_image_context_path_list)
        # now we assert that each file has been downloaded and properly named
        for file in self.__test_urls_image_context_path_list:
            expected_outfile=os.path.join(self.__downloads_temp_folder__,file)
            if not os.path.isfile(expected_outfile):
                # assert the file exists
                print("Expected that file "+expected_outfile+" exists, but it is missing.")
                files_missing+=1
                continue
            if not (imghdr.what(expected_outfile) == "jpeg" or imghdr.what(expected_outfile) == "jpg" or imghdr.what(expected_outfile) == "png" or imghdr.what(expected_outfile) == "gif"):
                # and it is a real image file
                print("Expected that file "+expected_outfile+" is a image, but it is of type "+str(imghdr.what(expected_outfile)))
                files_corrupt+=1
                continue
            files_ok+=1
        assert files_missing == 0 and files_corrupt == 0 and files_ok == number_urls, "Expected that "+str(number_urls)+" has been downloaded. "+str(files_missing)+" files are missing, "+str(files_corrupt)+" images are corrupt. Only "+str(files_ok)+" has been succesfully downloaded."
