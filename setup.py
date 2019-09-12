from setuptools import setup

setup(name='PythonImageDownloader',
      version='1.0.1',
      packages=['downloader'],
      entry_points={
          'console_scripts': [
              'pxl_downloader = downloader.__main__:main'
          ]
      },
      )
