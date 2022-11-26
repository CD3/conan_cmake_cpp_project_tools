import shlex
import shutil
import pathlib
import platform
import os
import subprocess
import fnmatch
import yaml
import typing
import itertools
from .path_filter_utils import *


def get_system(ext=None):
    return platform.system().lower()

def get_shell(ext=None):
    system = get_system()
    if system.lower() == "linux":
        if ext is None:
            for shell in ['bash']:
                shell = shutil.which(shell)
                if shell is not None:
                    return shell


    raise RuntimeError(f"Could not find a shell for system '{system}'.")



def cmd_to_run_shell_script(filename:pathlib.Path,return_as_string=False):
    shell = pathlib.Path(get_shell())
    if shell.name == "bash":
        cmd = [ str(shell.absolute()), str(filename) ]
        if return_as_string:
            cmd = shlex.join(cmd)
        return cmd


    raise RuntimeError("Could not find a shell to run script.")


def find_file_at_or_above(path : pathlib.Path, filename : str):
    '''
    Look for a file with given name in the current directory and its parents.
    '''
    search_path = path.absolute()
    root_path = pathlib.Path("/")
    while search_path != root_path:
        file = search_path/filename
        if file.exists():
            yield file
        search_path = search_path.parent


def find_file_at_or_below(path : pathlib.Path, filename : str):
    '''
    Look for a file with given name in the current directory and its children (recursively).
    '''
    path = pathlib.Path(path)
    files = path.glob("**/"+filename)
    return files

def get_all_paths_below(root_path:pathlib.Path):
    return root_path.glob("**/*")
    
def find_project_root(path : pathlib.Path, sentinal_files = ['.git','CMakeLists.txt']):
    '''
    Search for the root of the project that the given path belongs to.
    '''
    for sentinal_file in sentinal_files:
        dir = next(find_file_at_or_above(path,sentinal_file),None)
        if dir is not None:
            return dir.parent
    

def make_build_dir_name(build_type:str, system:str):
    return f"build-{system.lower()}-{build_type.lower()}"

def get_source_files(path : pathlib.Path, filt = lambda f: True):
    '''
    Return generator with project's source files.

    This function will use `git ls-files` if path is in a git repository.

    If not, then it will check for the `fd` command call `fd .` from the path directory if it exists.

    If not, then it will glob all files under the path directory.
    '''
    if is_git_repo(path):
        git = shutil.which('git')
        with working_directory(path):
            result = subprocess.run([git,'ls-files'],capture_output=True)
        files = result.stdout.strip().decode(encoding).split('\n')
    else:
        fd = shutil.which('fd')
        if fd is not None:
            with working_directory(path):
                result = subprocess.run([fd,'.','-t','f'],capture_output=True)
                
            files = result.stdout.decode(encoding).strip().split('\n')
        else:
            files = path.glob('**/*')


    for file in files:
        file = pathlib.Path(file)
        if filt(file):
            yield file

def find_unit_test_binaries(dir_to_search:pathlib.Path, filters = is_exe, include_patterns = ['*test*','*Test*'], exclude_patterns = ['*/CMakeFiles/*']):
    '''
    Return a iterator of unit test binaries.
    '''
    if type(filters) is not list:
        filters = [filters]
    if type(include_patterns) is not list:
        include_patterns = [include_patterns]
    if type(exclude_patterns) is not list:
        exclude_patterns = [exclude_patterns]

    files = (dir_to_search.glob('**/*') | pfilter(all_filters(*filters))
                                        | pfilter(filename_matches_pattern_filter(*include_patterns))
                                        | -pfilter(filename_matches_pattern_filter(*exclude_patterns))
            )
    for file in files:
        yield file

def sort_paths(paths:typing.List[pathlib.Path], filters = None, include_patterns = None, exclude_patterns = None):
    '''
    Sorts a list of paths into "include", "exclude" and "removed with filter".

    @param filters : a list of filters, i.e. functions that take a path argument and return True if it should be "kept"
    @param include_patterns : a list of glob-style patterns for matching paths that will be "kept". paths that match any _one_ pattern will be included.
    @param exclude_patterns : a list of glob-style patterns for matching paths that will be "kept". paths that match any _one_ pattern will be excluded.

    Files are sorted by first appling all filters, then checking the include patterns, and then checking the exclude patterns.
    '''

    # set defaults
    if filters is None:
        filters = [lambda p : True]
    if include_patterns is None:
        include_patterns = ['*']
    if exclude_patterns is None:
        exclude_patterns = []

    # turn ConfSettings into lists (without referencing the type)
    if hasattr(filters,'tree'):
        filters = filters.tree
    if hasattr(include_patterns,"tree"):
        include_patterns = include_patterns.tree
    if hasattr(exclude_patterns,"tree"):
        exclude_patterns = exclude_patterns.tree

    # turn single elements into lists
    if type(filters) is not list:
        filters = [filters]
    if type(include_patterns) is not list:
        include_patterns = [include_patterns]
    if type(exclude_patterns) is not list:
        exclude_patterns = [exclude_patterns]


    sorted_paths = {"included":[],"excluded":[],"removed by filter":[],"unspecified":[]}

    for path in paths:
        category = "unspecified"
        if any([ not f(path) for f in filters ]):
            category = "removed by filter"
        else:
            if any([ fnmatch.fnmatch(path.stem,pattern) for pattern in include_patterns ]):
                category = "included"
            if any([ fnmatch.fnmatch(path.stem,pattern) for pattern in exclude_patterns ]):
                category = "excluded"

        sorted_paths[category].append(path)

    return sorted_paths


def parse_option_to_config_entry(option_string:str):
    data = yaml.safe_load(option_string)
    return data


