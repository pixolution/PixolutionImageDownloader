# Pixolution Image Downloader

Lightweight bulk image url list downloader written in Python3 by [pixolution.org](https://pixolution.org)

It provides the following features:
* RateLimiter with throttling max downloads per interval using a simple token bucket algorithm without queue
* Multithreaded downloads
* Preserves the context path of the images (http://foo.bar/imgs/abs/img.jpg is stored into **img/abs/img.jpg**)
* Creates a file **img_list_name.txt_errors.log** containing failed images
* Can store images into download folder tree or directly into a tar file
* Download progress bar with downloads/second (using tqdm)

## Develop

Install the project into your local system as symlinked source:
```bash
python3 setup.py develop
```
## virtual environment

You should use venv when working on the project.

### Run once in the project folder:
```bash
python3 -mvenv .
source bin/activate
pip3 install -r requirements.txt
```

### Run before working:
```bash
source bin/activate

[ DO YOUR DEVELOPMENT WORK ]

deactivate
```

## Install

Install requirements:
```bash
sudo apt install python3-setuptools python3-pip
```

Install the project into your local system:
```bash
cd PixolutionImageDownloader/
python3 setup.py install
```

After install it is available as **pxl_downloader** in your systems CLI. Use it like this:
```bash
pxl_downloader --threads=8 download --tarfile --ratelimit-interval=2 --ratelimit-downloads=50 samples.csv downloads/
```

Deinstall it with:
```bash
python3 setup.py uninstall
```

## Tests

To run a single test use:
```bash
python3 -m unittest tests/DownloadTest.py
```

To run all available tests use:
```bash
python3 -m unittest discover tests/
```


## Use it via **run.sh** script in project root or with **pxl_downloader** command after install
```bash
user@pixolution:~$ pxl_downloader --help
usage: pxl_downloader [-h] [--threads THREADS] [--verbose]
                      {download,status} ... image_list_file download_folder

Lightweight mass image downloader written in Python3.

positional arguments:
  {download,status}  available commands
    download         Download a list of images
    status           Check the download folder and the given image list file
                     and print some stats about that
  image_list_file    A file with urls defered by newlines
  download_folder    A folder to download the images to.

optional arguments:
  -h, --help         show this help message and exit
  --threads THREADS  Number of threads to download or status check in parallel
  --verbose          Show each image url to download in stdout instead of
                     default progress bar

♥ Crafted with love in Berlin by pixolution.org ♥
```

Download options:
```bash
user@pixolution:~$ pxl_downloader download --help
usage: pxl_downloader download [-h] [--tarfile]
                               [--ratelimit-interval RATELIMIT_INTERVAL]
                               [--ratelimit-downloads RATELIMIT_DOWNLOADS]

optional arguments:
  -h, --help            show this help message and exit
  --tarfile             Store downloaded images directly into tarfile instead
                        of file structure
  --ratelimit-interval RATELIMIT_INTERVAL
                        Interval in seconds (minimum 1.0) for the rate
                        limiter. Default is 1.0 seconds.
  --ratelimit-downloads RATELIMIT_DOWNLOADS
                        Number of downloads per interval (default interval 1
                        second). If negative no rate limit is applied. Default
                        is -1
```
