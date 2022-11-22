from .utils import *
from .script import Script, CmdGenerator
import tempfile
import platform
import subprocess
import fnmatch
import typer
from os.path import relpath
from .config import fspathtree

def install_deps(config:fspathtree,run=True):

    if config.get('directories/build',None) is None:
        raise RuntimeError("No build directory given. Cannot run install_deps step.")
    script = Script( system=config.get('/system',get_system()), shell=config.get('/shell', get_shell()) )
    script_filename = config.get('install_deps/script_filename','01-install_deps')
    
    
    with working_directory(config['directories/scripts']):
        bdir = config['directories/build'].absolute()
        cdir = config['files/conanfile'].absolute().parent

        script.cd(bdir.parent)
        script.mkdir(relpath(bdir,bdir.parent))
        script.cd(relpath(bdir,bdir.parent))


        build_type = config.get('build_type','Debug')

        conan_cmd = [ config.get('conan/cmd','conan') ]
        default_args = ['install','{conan_dir}','-pr:b=default','-s',f'build_type={build_type}']
        conan_cmd += [ arg.format(conan_dir=relpath(cdir,bdir)) for arg in config.get('conan/args',fspathtree(default_args)).tree ]
        conan_cmd += [ arg.format(conan_dir=relpath(cdir,bdir)) for arg in config.get('conan/extra_args',fspathtree([])).tree ]


        script.add_command( conan_cmd )


        script.write(pathlib.Path(script_filename),exit_on_error=True)
        
        if run:
            cmd = cmd_to_run_shell_script(script_filename)
            result = subprocess.run(cmd)
            return result.returncode

        


    

def configure_build(config:fspathtree,run=True):

    if config.get('directories/build',None) is None:
        raise RuntimeError("No build directory given. Cannot run configure_build step.")
    script = Script( system=config.get('/system',get_system()), shell=config.get('/shell', get_shell()) )
    script_filename = config.get('configure_build/script_filename','02-configure_build')
    
    
    with working_directory(config['directories/scripts']):
        bdir = config['directories/build'].absolute()
        cdir = config['files/CMakeLists.txt'].absolute().parent

        script.cd(bdir.parent)
        script.mkdir(relpath(bdir,bdir.parent))
        script.cd(relpath(bdir,bdir.parent))
        script.activate_environment(bdir,bdir) 



        build_type = config.get('build_type','Debug')
        cmake_cmd = [ config.get('cmake/cmd','cmake') ]
        default_args = ["{cmake_dir}"]
        if (bdir/"conan_toolchain.cmake").exists():
            default_args += ["-DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake"]
        default_args += [f"-DCMAKE_BUILD_TYPE={build_type}"]
        cmake_cmd += [ arg.format(cmake_dir=relpath(cdir,bdir)) for arg in config.get('cmake/args',fspathtree(default_args)).tree ]
        cmake_cmd += [ arg.format(cmake_dir=relpath(cdir,bdir)) for arg in config.get('cmake/extra_args',fspathtree([])).tree ]

        script.add_command( cmake_cmd )


        script.deactivate_environment(bdir,bdir)


        script.write(pathlib.Path(script_filename),exit_on_error=True)
        
        if run:
            cmd = cmd_to_run_shell_script(script_filename)
            result = subprocess.run(cmd)
            return result.returncode


def run_build(config:fspathtree,run=True):

    if config.get('directories/build',None) is None:
        raise RuntimeError("No build directory given. Cannot run configure_build step.")

    bdir = config['directories/build'].absolute()

    if not bdir.exists():
        raise RuntimeError(f"The build directory '{bdir}' has not been created yet.")

    script = Script( system=config.get('/system',get_system()), shell=config.get('/shell', get_shell()) )
    script_filename = config.get('run_build/script_filename','03-run_build')

    with working_directory(config['directories/scripts']):
        script.cd(bdir.parent)
        script.cd(relpath(bdir,bdir.parent))
        script.activate_environment(bdir,bdir)

        cmake_cmd = [ config.get('cmake/cmd','cmake') ]
        default_args = ["--build",'.']
        cmake_cmd += [ arg for arg in config.get('cmake/build/args',fspathtree(default_args)).tree ]
        cmake_cmd += [ arg for arg in config.get('cmake/build/extra_args',fspathtree([])).tree ]

        script.add_command( cmake_cmd )

        script.deactivate_environment(bdir,bdir)

        script.write(pathlib.Path(script_filename),exit_on_error=True)
        
        if run:
            cmd = cmd_to_run_shell_script(script_filename)
            result = subprocess.run(cmd)
            return result.returncode

def run_tests(config:fspathtree,run=True):
    if config.get('directories/build',None) is None:
        raise RuntimeError("No build directory given. Cannot run configure_build step.")

    bdir = config['directories/build'].absolute()

    if not bdir.exists():
        raise RuntimeError(f"The build directory '{bdir}' has not been created yet.")

    cmd_generator = CmdGenerator(config.get('platform',None))
    script = Script( system=config.get('/system',get_system()), shell=config.get('/shell', get_shell()) )
    script_filename = config.get('run_build/script_filename','04-run_tests')

    with working_directory(config['directories/scripts']):
        script.cd(bdir.parent)
        script.cd(relpath(bdir,bdir.parent))
        script.activate_run_environment(bdir,bdir)

        test_exes = find_unit_test_binaries(bdir)

        for exe in test_exes:
            print("Found test executable:",exe)
            args = []
            for pattern in config.get('/run_tests/args',fspathtree([])).tree:
                if fnmatch.fnmatch(exe,pattern):
                    args = config[f'run_tests/args/{pattern}'].tree


            script.call(exe,bdir,args)


        script.write(pathlib.Path(script_filename),exit_on_error=True)

        script.deactivate_run_environment(bdir,bdir)
        
        if run:
            cmd = cmd_to_run_shell_script(script_filename)
            result = subprocess.run(cmd)
            return result.returncode


def debug_tests(config:fspathtree,run=True):
    if config.get('directories/build',None) is None:
        raise RuntimeError("No build directory given. Cannot run configure_build step.")

    bdir = config['directories/build'].absolute()

    if not bdir.exists():
        raise RuntimeError(f"The build directory '{bdir}' has not been created yet.")

    cmd_generator = CmdGenerator(config.get('platform',None))
    script = Script( system=config.get('/system',get_system()), shell=config.get('/shell', get_shell()) )
    script_filename = config.get('run_build/script_filename','05-debug_tests')

    with working_directory(config['directories/scripts']):
        script.cd(bdir.parent)
        script.cd(relpath(bdir,bdir.parent))
        script.activate_run_environment(bdir,bdir)

        test_exes = list(filter(is_debug_exe, find_unit_test_binaries(bdir)))
        if len(test_exes) < 1:
            print("Did not find any test executables with debug symbols.")

        choice = 0
        if len(test_exes) > 1:
            print("Found multiple test executables. Which one do you want to debug?")
            typer.promp("Select exe",choice)
            while choice < 0 or choice >= len(test_exes):
                choice = 0
                typer.promp(f"Please choose number between 0 and {len(test_exes)-1}",choice)
        
        exe = test_exes[choice]

        print("Found test executable:",exe)
        args = []
        for pattern in config.get('/debug_tests/args',fspathtree([])).tree:
            if fnmatch.fnmatch(exe,pattern):
                args = config[f'debug_tests/args/{pattern}'].tree

        debugger = config.get('/debug_tests/debugger/cmd','gdb')
        debugger_args = config.get('/debug_tests/debugger/args',['-tui'])
        cmd = [ debugger ] + debugger_args + [str(exe)] +  args

        script.add_command( shlex.join(cmd) )


        script.write(pathlib.Path(script_filename),exit_on_error=True)

        script.deactivate_run_environment(bdir,bdir)
        
        if run:
            cmd = cmd_to_run_shell_script(script_filename)
            result = subprocess.run(cmd)
            return result.returncode


def install(config:fspathtree,run=True):
    '''
    Install project into given directory.
    '''

    if config.get('directories/build',None) is None:
        raise RuntimeError("No build directory given. Cannot run configure_build step.")

    bdir = config['directories/build'].absolute()

    if not bdir.exists():
        raise RuntimeError(f"The build directory '{bdir}' has not been created yet.")

    script = Script( system=config.get('/system',get_system()), shell=config.get('/shell', get_shell()) )
    script_filename = config.get('run_build/script_filename','05-install')

    with working_directory(config['directories/scripts']):
        script.cd(bdir.parent)
        script.cd(relpath(bdir,bdir.parent))

        cmake_cmd = [ config.get('cmake/cmd','cmake') ]
        default_args = ["--install",'.']
        cmake_cmd += [ arg for arg in config.get('cmake/install/args',fspathtree(default_args)).tree ]
        cmake_cmd += [ arg for arg in config.get('cmake/install/extra_args',fspathtree([])).tree ]

        script.add_command( cmake_cmd )


        script.write(pathlib.Path(script_filename),exit_on_error=True)
        
        if run:
            cmd = cmd_to_run_shell_script(script_filename)
            result = subprocess.run(cmd)
            return result.returncode
