from setuptools import setup

setup(name='PythonImageDownloader',
      version='1.2.0',
      packages=['downloader'],
      entry_points={
          'console_scripts': [
              'pxl_downloader = downloader.__main__:main'
          ]
      },
      )
