from fspathtree import fspathtree
import pathlib
from .utils import *
import yaml

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


def load_config_files( cfg: fspathtree, root_dir:pathlib.Path, config_file_basename:str):
    # look for yaml files
    data = {}
    for file in sorted(list(find_file_at_or_above(root_dir,config_file_basename+".yml")),key=lambda p: len(p.parts)):
        with open(file) as f:
            data.update(yaml.safe_load(f))

    cfg.tree.update(data)

def set_defaults( cfg: fspathtree, overwrite:bool = True):

    if overwrite or cfg.get('/system',None) is None:
        cfg['/system'] = get_system()

    if overwrite or cfg.get('/shell',None) is None:
        cfg['/shell'] = get_shell()


def set_default_build_dir(cfg:fspathtree):
    cfg['directories/build'] = cfg.get('directories/root',pathlib.Path())/make_build_dir_name(build_type=cfg.get('/build_type','unknown'),system=cfg.get('/system','unknown') )


def set_default_conanfile(cfg:fspathtree):
    conanfiles = list(find_file_at_or_below(cfg['/directories/root'],"conanfile.py"))
    if len(conanfiles) < 1:
        conanfiles = list(find_file_at_or_below(cfg['/directories/root'],"conanfile.txt"))

    if len(conanfiles) > 0:
        cfg['files/conanfile']= sorted(conanfiles,key=lambda p: p.parts)[0].absolute()



def set_default_cmakefile(cfg:fspathtree):
    cmakefiles = list(find_file_at_or_below(cfg['/directories/root'],"CMakeLists.txt"))

    if len(cmakefiles) > 0:
        cfg['files/CMakeLists.txt'] = sorted(cmakefiles,key=lambda p: p.parts)[0].absolute()

