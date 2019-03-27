from setuptools import setup

setup(name='PythonImageDownloader',
      version='0.1.0',
      packages=['downloader'],
      entry_points={
          'console_scripts': [
              'pxl_downloader = downloader.__main__:main'
          ]
      },
      )
