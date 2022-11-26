import pathlib
import os
import platform
import fnmatch
import shutil
import subprocess
import itertools
from .core_utils import *


class pfilter:
    '''
    A class for applying filters to iterators/generators
    using the pipe (|) operator. i.e.

    pathlib.Path().glob("**/*) | pfilter( lambda p : p.is_file() )
    '''
    def __init__(self,filter_func):
        self.filter_func = filter_func


    def __xor__(self,other):
        filter_func = lambda x: self.filter_func(x) or other.filter_func(x)
        return pfilter(filter_func)

    def __neg__(self):
        filter_func = lambda x: not self.filter_func(x)
        return pfilter(filter_func)


    def __ror__(self,iter):
        for item in iter:
            if self.filter_func(item):
                yield item

class ptransform:
    '''
    A class for applying transforms to iterators/generators
    using the pipe (|) operator. i.e.

    pathlib.Path().glob("**/*) | ptransform( lambda p : p.absolute() )
    '''
    def __init__(self,transform_func):
        self.transform_func = transform_func


    def __ror__(self,iter):
        for item in iter:
            yield self.transform_func(item)

def is_file(path:pathlib.Path):
    return path.is_file()

def is_exe(path):
  '''Return true if file specified by path is an executable.'''
  if path.is_file():
    if os.access(str(path),os.X_OK):
      return True

  return False

def is_debug_exe(path:pathlib.Path):
  '''
  Return true if the file is a debug-able executable.
  '''
  if is_exe(path):
    if platform.system().lower() == "linux":
      ret = subprocess.check_output(["file",str(path.absolute())])
      return ret.decode(encoding).find("with debug_info") > -1

  return False

def is_git_repo(path : pathlib.Path):
    '''
    Return true if path is part of a git repository.
    '''
    git = shutil.which('git')
    if git is not None:
        result = subprocess.run([git,'rev-parse','--is-inside-work-tree'],capture_output=True,cwd=path)
        output = result.stdout.decode(encoding).strip()
        if result.returncode == 0 and output == "true":
            return True

    return False

def all_filters(*filters):
    def passes(path:pathlib.Path):
        return all( [f(path) for f in filters] )
    return passes

def any_filters(*filters):
    def passes(path:pathlib.Path):
        return any( [f(path) for f in filters] )
    return passes


def filename_matches_pattern_filter(*patterns):
    patterns = list(flatten(patterns))
    def matches(path:pathlib.Path):
        for pattern in itertools.chain(patterns):
            if fnmatch.fnmatch(path,pattern):
                return True
        return False

    return matches

