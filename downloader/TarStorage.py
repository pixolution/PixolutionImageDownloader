#!bin/python3
# -*- coding: utf-8 -*-1
import os
import tarfile

class TarStorage:

    def __init__(self,list_file_name,outdir):
        self.tar_name=os.path.join(outdir,os.path.basename(list_file_name)+"_images.tar")

    """
    Allows together with __exit__ to use this class in with statements.
    Open the tar file handle.
    """
    def __enter__(self):
        self.tarfile=tarfile.open(self.tar_name,'w:')
        return self.tarfile

    """
    Allows together with __enter__ to use this class in with statements
    Closes the tar file handle.
    """
    def __exit__(self, exc_type, exc_value, traceback):
        self.tarfile.close()
        self.tarfile=None
