# user-defined exceptions
class Error(Exception):
   """Base class for other exceptions"""
   pass
class FileExists(Error):
   """Raised when the input value is too small"""
   pass
class DownloadFailed(Error):
   """Raised when the input value is too large"""
   pass
