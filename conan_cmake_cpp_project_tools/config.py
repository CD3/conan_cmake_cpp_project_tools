from fspathtree import fspathtree
import pathlib
from .utils import *
import yaml
import shutil
import os

# /directories/scripts
# /directories/root
# /directories/build
# /files/conanfile
# /files/CMakeLists.txt
# /build_type
# /system
# /shell
# /conan/cmd
# /conan/args
# /conan/extra_args
# /cmake/cmd
# /cmake/args
# /cmake/extra_args
# /install_deps/script_name
# /configure_build/script_name
# /run_build/script_name
# /run_tests/script_name

class ConfSettings(fspathtree):
    class Null:
        def __init__(self,msg=None):
            self.msg = msg
        def __repr__(self):
            if self.msg:
                return f"<NULL:{self.msg}>"
            else:
                return f"<NULL>"

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.__allow_missing_keys = False

    def allow_missing_keys(self,val:bool):
        self.__allow_missing_keys = bool(val)

    def get(self,key,default_value):
        '''
        Override the default fstreepath behavior.

        If `self.strict` is set, then we want to throw an error for missing
        keys. to throw an error if
        `self.strict` is set and the key does not exists. 
        the key does not exists, and the default value if it is an
        instance of Null.
        '''
        val = super().get(key,default_value) if self.__allow_missing_keys else self[key]
        if type(val) == ConfSettings.Null:
            val = default_value
        return val


def load_config_files( cfg: ConfSettings, root_dir:pathlib.Path, config_file_basename:str):
    # look for yaml files
    data = {}
    for file in sorted(list(find_file_at_or_above(root_dir,config_file_basename+".yml")),key=lambda p: len(p.parts)):
        with open(file) as f:
            data.update(yaml.safe_load(f))

    cfg.tree.update(data)

def set_defaults( cfg: ConfSettings, overwrite:bool = True):

    def set(key,val):
        if overwrite or cfg.get(key,None) is None:
            cfg[key] = val

    set('/system', get_system())
    set('/shell', get_shell())
    set('/build_type', ConfSettings.Null())
    set('/files/progress', ConfSettings.Null())
    set('/files/conanfile', ConfSettings.Null())
    set('/files/CMakeLists.txt', ConfSettings.Null())
    set('/directories/root', ConfSettings.Null())
    set('/directories/build', ConfSettings.Null())
    set('/directories/scripts', ConfSettings.Null())
    set('/conan/cmd', ConfSettings.Null())
    set('/conan/args', ConfSettings.Null("Will be generated depending on specific settings and files that are detected."))
    set('/conan/extra_args', ConfSettings.Null("Pass extra command line arguments here."))
    set('/cmake/cmd', ConfSettings.Null())
    set('/cmake/args', ConfSettings.Null("Will be generated depending on specific settings and files that are detected."))
    set('/cmake/extra_args', ConfSettings.Null("Pass extra command line arguments here."))
    set('/cmake/build/cmd', ConfSettings.Null())
    set('/cmake/build/args', ConfSettings.Null("Will be detected by default."))
    set('/cmake/build/extra_args', ConfSettings.Null("Pass extra command line arg here."))
    set('/run_tests/args', ConfSettings.Null())
    set('/run_tests/include', ['*test*','*Test*'])
    set('/run_tests/exclude', ['*/CMakeFiles/*'])
    set('/debug_tests/args', ConfSettings.Null())
    set('/debug_tests/include', ['*test*','*Test*'])
    set('/debug_tests/exclude', ['*/CMakeFiles/*'])
    set('/debug_tests/debugger/cmd', ConfSettings.Null())
    set('/debug_tests/debugger/args', ConfSettings.Null())
    set('/install_deps/script_filename', ConfSettings.Null() )
    set('/configure_build/script_filename', ConfSettings.Null() )
    set('/run_build/script_filename', ConfSettings.Null() )
    set('/run_tests/script_filename', ConfSettings.Null() )



def set_default_build_dir(cfg:ConfSettings):
    cfg['directories/build'] = cfg.get('directories/root',pathlib.Path())/make_build_dir_name(build_type=cfg.get('/build_type','unknown'),system=cfg.get('/system','unknown') )


def set_default_conanfile(cfg:ConfSettings):
    conanfiles = list(find_file_at_or_below(cfg['/directories/root'],"conanfile.py"))
    if len(conanfiles) < 1:
        conanfiles = list(find_file_at_or_below(cfg['/directories/root'],"conanfile.txt"))

    if len(conanfiles) > 0:
        cfg['files/conanfile']= sorted(conanfiles,key=lambda p: p.parts)[0].absolute()



def set_default_cmakefile(cfg:ConfSettings):
    cmakefiles = list(find_file_at_or_below(cfg['/directories/root'],"CMakeLists.txt"))

    if len(cmakefiles) > 0:
        cfg['files/CMakeLists.txt'] = sorted(cmakefiles,key=lambda p: p.parts)[0].absolute()

