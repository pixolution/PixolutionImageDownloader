import sys
import urllib.request
import argparse
import sys
import os
from downloader.Downloader import Downloader

# we need python 3
if sys.version_info < (3, 0):
    sys.stderr.write("\nSorry, requires Python 3.x, not Python 2.x\n\n")
    sys.exit(1)

# constants
PATH_SCRIPT = os.path.dirname(os.path.realpath(__file__))

"""
Parse the command line arguments.
"""
def parse_parameters():
    parser = argparse.ArgumentParser(description="")
    parser.prog = "pxl_downloader"
    parser.description = "Lightweight mass image downloader written in Python3."
    parser.epilog = u"  \u2665  Crafted with love in Berlin by pixolution.org \u2665"
    subparsers = parser.add_subparsers(help="available commands")
    subparsers.required = True
    subparsers.dest = "command"
    parser.add_argument("--threads",help="Number of threads to download or status check in parallel",type=int, dest="threads", default=8,required=False)
    parser.add_argument("--verbose",help="Show each image url to download in stdout instead of default progress bar", dest="verbose", default=False,required=False,action="store_true")
    parser_download = subparsers.add_parser("download", help="Download a list of images")
    parser_download.add_argument("--tarfile",help="Store downloaded images directly into tarfile instead of file structure", dest="tarfile", default=False,required=False,action="store_true")
    parser_download.add_argument("--ratelimit-interval",type=int,help="Interval in seconds (minimum 1.0) for the rate limiter. Default is 1.0 seconds.", dest="ratelimit_interval", default=1.0,required=False)
    parser_download.add_argument("--ratelimit-downloads",type=int,help="Number of downloads per interval (default interval 1 second). If negative no rate limit is applied. Default is -1", dest="ratelimit_downloads", default=-1,required=False)
    parser_status = subparsers.add_parser("status", help="Check the download folder and the given image list file and print some stats about that")
    parser.add_argument("image_list_file",help="A file with urls defered by newlines")
    parser.add_argument("download_folder",help="A folder to download the images to.")
    try:
        args = parser.parse_args()
    except:
        raise
    return args

"""
program entry point
"""
def main(args=None):
    args = parse_parameters()
    if os.path.isabs(args.image_list_file):
        image_list_file=args.image_list_file
    else:
        image_list_file = os.path.join(os.getcwd(),args.image_list_file)
    if os.path.isabs(args.download_folder):
        download_folder = args.download_folder
    else:
        download_folder = os.path.join(os.getcwd(),args.download_folder)
    if not os.path.isfile(image_list_file):
        print("The given path "+image_list_file+" is not a file. Abort.")
        sys.exit(1)
    if (args.command == "download"):
        downloader=Downloader(download_folder,args.threads,args.ratelimit_downloads,args.ratelimit_interval,args.verbose,args.tarfile)
        downloader.download_list(image_list_file)
    elif (args.command == "status"):
        downloader=Downloader(download_folder,args.threads,args.ratelimit_downloads,args.ratelimit_interval,args.verbose)
        downloader.check_status(image_list_file,download_folder,args.threads)
    else:
        print("Command not known: "+args.command)


if __name__ == "__main__":
    main()
