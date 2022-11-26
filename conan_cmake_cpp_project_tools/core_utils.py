import pathlib
import os

encoding = 'utf-8'

class working_directory:
    '''
    A context manager to temporarily change the current working directory.
    '''
    def __init__(self,directory:pathlib.Path):
        self.directory = pathlib.Path(directory).absolute()
        self.old_directory = pathlib.Path( os.getcwd() ).absolute()


    def __enter__(self):
        os.chdir(self.directory)

    def __exit__(self,type,value,traceback):
        os.chdir(self.old_directory)

def flatten(lst):
    '''
    Flatten a nested list/tuple.
    '''
    for item in lst:
        if type(item) in [tuple,list]:
            for nested_item in flatten(item):
                yield nested_item
        else:
            yield item

