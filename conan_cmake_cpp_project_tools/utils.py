import shlex
import shutil
import pathlib
import platform
import os
import subprocess
import fnmatch

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

def is_exe(path):
  '''Return true if file specified by path is an executable.'''
  if path.is_file():
    if os.access(str(path),os.X_OK):
      return True

  return False

def is_git_repo(path : pathlib.Path):
    '''
    Return true if path is part of a git repository.
    '''
    git = shutil.which('git')
    if git is not None:
        with working_directory(path):
            result = subprocess.run([git,'rev-parse','--is-inside-work-tree'],capture_output=True)
            output = result.stdout.decode('utf-8').strip()
            if result.returncode == 0 and output == "true":
                return True

    return False

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
        files = result.stdout.strip().decode('utf-8').split('\n')
    else:
        fd = shutil.which('fd')
        if fd is not None:
            with working_directory(path):
                result = subprocess.run([fd,'.','-t','f'],capture_output=True)
                
            files = result.stdout.decode('utf-8').strip().split('\n')
        else:
            files = path.glob('**/*')


    for file in files:
        file = pathlib.Path(file)
        print(file)
        if filt(file):
            yield file

def make_file_matches_pattern_filter(*patterns):

    def matches(path:pathlib.Path):
        for pattern in patterns:
            if fnmatch.fnmatch(path,pattern):
                return True
        return False

    return matches
