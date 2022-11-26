from .utils import *
from .script import Script, CmdGenerator
import tempfile
import platform
import subprocess
import fnmatch
import typer
from os.path import relpath
from .config import ConfSettings
from rich import print

def install_deps(config:ConfSettings,run=True):

    if config.get('/directories/build',None) is None:
        raise RuntimeError("No build directory given. Cannot run install_deps step.")
    script = Script( system=config.get('/system',get_system()), shell=config.get('/shell', get_shell()) )
    script_filename = config.get('/install_deps/script_filename','01-install_deps')
    
    
    with working_directory(config['directories/scripts']):
        bdir = config['directories/build'].absolute()
        cdir = config['files/conanfile'].absolute().parent

        script.cd(bdir.parent)
        script.mkdir(relpath(bdir,bdir.parent))
        script.cd(relpath(bdir,bdir.parent))


        build_type = config.get('/build_type','Debug')

        conan_cmd = [ config.get('/conan/cmd','conan') ]
        default_args = ['install','{conan_dir}','-pr:b=default','-s','build_type={build_type}']
        conan_cmd += [ arg.format(conan_dir=relpath(cdir,bdir),build_type=build_type) for arg in config.get('/conan/args',ConfSettings(default_args)).tree ]
        conan_cmd += [ arg.format(conan_dir=relpath(cdir,bdir),build_type=build_type) for arg in config.get('/conan/extra_args',ConfSettings([])).tree ]


        script.add_command( conan_cmd )


        script.write(pathlib.Path(script_filename),exit_on_error=True)
        
        if run:
            cmd = cmd_to_run_shell_script(script_filename)
            result = subprocess.run(cmd)
            return result.returncode

        


    

def configure_build(config:ConfSettings,run=True):

    if config.get('/directories/build',None) is None:
        raise RuntimeError("No build directory given. Cannot run configure_build step.")
    script = Script( system=config.get('/system',get_system()), shell=config.get('/shell', get_shell()) )
    script_filename = config.get('/configure_build/script_filename','02-configure_build')
    
    
    with working_directory(config['directories/scripts']):
        bdir = config['directories/build'].absolute()
        cdir = config['files/CMakeLists.txt'].absolute().parent

        script.cd(bdir.parent)
        script.mkdir(relpath(bdir,bdir.parent))
        script.cd(relpath(bdir,bdir.parent))
        script.activate_environment(bdir,bdir) 



        build_type = config.get('/build_type','Debug')
        cmake_cmd = [ config.get('/cmake/cmd','cmake') ]
        default_args = ["{cmake_dir}"]
        if (bdir/"conan_toolchain.cmake").exists():
            default_args += ["-DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake"]
        default_args += ["-DCMAKE_BUILD_TYPE={build_type}"]
        cmake_cmd += [ arg.format(cmake_dir=relpath(cdir,bdir),build_type=build_type) for arg in config.get('/cmake/args',ConfSettings(default_args)).tree ]
        cmake_cmd += [ arg.format(cmake_dir=relpath(cdir,bdir),build_type=build_type) for arg in config.get('/cmake/extra_args',ConfSettings([])).tree ]

        script.add_command( cmake_cmd )


        script.deactivate_environment(bdir,bdir)


        script.write(pathlib.Path(script_filename),exit_on_error=True)
        
        if run:
            cmd = cmd_to_run_shell_script(script_filename)
            result = subprocess.run(cmd)
            return result.returncode


def run_build(config:ConfSettings,run=True):

    if config.get('/directories/build',None) is None:
        raise RuntimeError("No build directory given. Cannot run configure_build step.")

    bdir = config['directories/build'].absolute()

    if not bdir.exists():
        raise RuntimeError(f"The build directory '{bdir}' has not been created yet.")

    script = Script( system=config.get('/system',get_system()), shell=config.get('/shell', get_shell()) )
    script_filename = config.get('/run_build/script_filename','03-run_build')

    with working_directory(config['directories/scripts']):
        script.cd(bdir.parent)
        script.cd(relpath(bdir,bdir.parent))
        script.activate_environment(bdir,bdir)

        cmake_cmd = [ config.get('/cmake/cmd','cmake') ]
        default_args = ["--build",'.']
        cmake_cmd += [ arg for arg in config.get('/cmake/build/args',ConfSettings(default_args)).tree ]
        cmake_cmd += [ arg for arg in config.get('/cmake/build/extra_args',ConfSettings([])).tree ]

        script.add_command( cmake_cmd )

        script.deactivate_environment(bdir,bdir)

        script.write(pathlib.Path(script_filename),exit_on_error=True)
        
        if run:
            cmd = cmd_to_run_shell_script(script_filename)
            result = subprocess.run(cmd)
            return result.returncode

def run_tests(config:ConfSettings,run=True):
    if config.get('/directories/build',None) is None:
        raise RuntimeError("No build directory given. Cannot run configure_build step.")

    bdir = config['directories/build'].absolute()

    if not bdir.exists():
        raise RuntimeError(f"The build directory '{bdir}' has not been created yet.")

    cmd_generator = CmdGenerator(config.get('/system',None))
    script = Script( system=config.get('/system',get_system()), shell=config.get('/shell', get_shell()) )
    script_filename = config.get('/run_build/script_filename','04-run_tests')

    with working_directory(config['directories/scripts']):
        script.cd(bdir.parent)
        script.cd(relpath(bdir,bdir.parent))
        script.activate_run_environment(bdir,bdir)

        include_patterns = config.get('/run_tests/include',ConfSettings(['*test*','*Test*']))
        exclude_patterns = config.get('/run_tests/exclude',ConfSettings([]))
        include_patterns_filter = filename_matches_pattern_filter(include_patterns.tree)
        exclude_patterns_filter = filename_matches_pattern_filter(exclude_patterns.tree)

        exes = list(bdir.glob("**/*") | pfilter(is_exe))
        included_exes = list(exes | pfilter(include_patterns_filter))
        excluded_exes = list(included_exes | pfilter(exclude_patterns_filter))
        test_exes = list(included_exes | -pfilter(exclude_patterns_filter))

        print("Found test executables:")
        if len(test_exes) > 0:
            for exe in test_exes:
                print("  ",exe)
        if len(exes) != len(included_exes):
            print(f"These executables were found, but skipped because they did not match an include pattern ({include_patterns.tree}):")
            for exe in exes:
                if exe not in included_exes:
                    print("  ",exe)
        if len(excluded_exes) > 0:
            print(f"These executables were found, but skipped because they matched an exclude pattern ({exclude_patterns.tree}):")
            for exe in exes:
                if exe in excluded_exes:
                    print("  ",exe)

        for exe in test_exes:
            args = []
            for pattern in config.get('/run_tests/args',ConfSettings([])).tree:
                if fnmatch.fnmatch(exe,pattern):
                    if config[f'run_tests/args/{pattern}'] is not None:
                        if type(config[f'run_tests/args/{pattern}']) == str:
                            args = [config[f'run_tests/args/{pattern}']]
                        else:
                            args = config[f'run_tests/args/{pattern}'].tree


            script.call(exe,bdir,args)


        script.write(pathlib.Path(script_filename),exit_on_error=True)

        script.deactivate_run_environment(bdir,bdir)
        
        if run:
            cmd = cmd_to_run_shell_script(script_filename)
            result = subprocess.run(cmd)
            return result.returncode


def debug_tests(config:ConfSettings,run=True):
    if config.get('/directories/build',None) is None:
        raise RuntimeError("No build directory given. Cannot run configure_build step.")

    bdir = config['directories/build'].absolute()

    if not bdir.exists():
        raise RuntimeError(f"The build directory '{bdir}' has not been created yet.")

    cmd_generator = CmdGenerator(config.get('/system',None))
    script = Script( system=config.get('/system',get_system()), shell=config.get('/shell', get_shell()) )
    script_filename = config.get('/run_build/script_filename','05-debug_tests')

    with working_directory(config['directories/scripts']):
        script.cd(bdir.parent)
        script.cd(relpath(bdir,bdir.parent))
        script.activate_run_environment(bdir,bdir)

        include_patterns = config.get('/debug_tests/include',ConfSettings(['*test*','*Test*']))
        exclude_patterns = config.get('/debug_tests/exclude',ConfSettings([]))
        include_patterns_filter = filename_matches_pattern_filter(include_patterns.tree)
        exclude_patterns_filter = filename_matches_pattern_filter(exclude_patterns.tree)

        exes = list(bdir.glob("**/*") | pfilter(is_debug_exe))
        included_exes = list(exes | pfilter(include_patterns_filter))
        excluded_exes = list(included_exes | pfilter(exclude_patterns_filter))
        test_exes = list(included_exes | -pfilter(exclude_patterns_filter))

        print("Found test executables:")
        if len(test_exes) > 0:
            for exe in test_exes:
                print("  ",exe)
        if len(exes) != len(included_exes):
            print(f"These executables were found, but skipped because they did not match an include pattern ({include_patterns.tree}):")
            for exe in exes:
                if exe not in included_exes:
                    print("  ",exe)
        if len(excluded_exes) > 0:
            print(f"These executables were found, but skipped because they matched an exclude pattern ({exclude_patterns.tree}):")
            for exe in exes:
                if exe in excluded_exes:
                    print("  ",exe)


        if len(test_exes) < 1:
            print("[yellow]Did not find any test executables with debug symbols.[/yellow]")
            return 0

        choice = 0
        if len(test_exes) > 1:
            print("Found multiple test executables. Which one do you want to debug?")
            for i,exe in enumerate(test_exes):
                print(i,exe)
            choice = typer.prompt("Select exe",choice)
            print(choice)
            while choice < 0 or choice >= len(test_exes):
                choice = 0
                choice = typer.prompt(f"Please choose number between 0 and {len(test_exes)-1}",choice)
        
        exe = test_exes[choice]

        args = []
        for pattern in config.get('/debug_tests/args',ConfSettings([])).tree:
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


def install(config:ConfSettings,run=True):
    '''
    Install project into given directory.
    '''

    if config.get('/directories/build',None) is None:
        raise RuntimeError("No build directory given. Cannot run configure_build step.")

    bdir = config['directories/build'].absolute()

    if not bdir.exists():
        raise RuntimeError(f"The build directory '{bdir}' has not been created yet.")

    script = Script( system=config.get('/system',get_system()), shell=config.get('/shell', get_shell()) )
    script_filename = config.get('/run_build/script_filename','05-install')

    with working_directory(config['directories/scripts']):
        script.cd(bdir.parent)
        script.cd(relpath(bdir,bdir.parent))

        cmake_cmd = [ config.get('/cmake/cmd','cmake') ]
        default_args = ["--install",'.']
        cmake_cmd += [ arg for arg in config.get('/cmake/install/args',ConfSettings(default_args)).tree ]
        cmake_cmd += [ arg for arg in config.get('/cmake/install/extra_args',ConfSettings([])).tree ]

        script.add_command( cmake_cmd )


        script.write(pathlib.Path(script_filename),exit_on_error=True)
        
        if run:
            cmd = cmd_to_run_shell_script(script_filename)
            result = subprocess.run(cmd)
            return result.returncode
