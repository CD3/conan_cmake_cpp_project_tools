from .utils import *
import pathlib
from os.path import relpath

class Script:
    def __init__(self,system:str = None, shell:str = None):
        self.lines = []
        self.cmd_generator = CmdGenerator(system=system,shell=shell)

    def add_command(self, cmd):
        if cmd is None:
            return
        if type(cmd) == list:
            cmd = shlex.join(cmd)
        self.lines.append( cmd )

    def write(self,filename:pathlib.Path,exit_on_error=False):
        lines = []
        if exit_on_error:
            lines += [self.cmd_generator.enable_exit_on_error()]
        lines += self.lines
        for i in range(len(lines)):
            if callable(lines[i]):
                lines[i] = lines[i]()
        filename.write_text( "\n".join(filter(lambda l: l is not None, lines)) )

    def __getattr__(self,attr):
        if hasattr(self.cmd_generator,attr):
            # We are doing some redirection here.
            # We want to add support for all of the methods provided by  the CmdGenerator class,
            # so that the caller does not have to use it directly. For example, if the caller
            # wanted to add a command make a directory, in a cross platform way, they could use and instance
            # of the CmdGenerator class to create the actual text that would be typed into the shell.
            # 
            # So, if the user calls a method that is implemented by CmdGenerator, we want to append a
            # call to our self.cmd_generator's method. But, we want to wrap it in a lambda so that we can delay the
            # evaluation of the function. That way way, we can build up a script, and "render" it for different shells
            # by changing the shell attribute.
            #
            # However, all we can do here (in the __getattr__) is return the thing that will be called. We do not get
            # the arguments to the call, because at this point, Python does not know if the attribute is a
            # variable or function. So, we create _another_ lambda that takes arbitrary arguments and keyword arguments,
            # and forwards them to our cmd_generator member.
            return lambda *args,**kwargs: self.add_command( lambda: getattr(self.cmd_generator,attr)(*args,**kwargs))



class CmdGenerator:
    '''
    A class for generating command strings for some common tasks (creating or deleting a directory, sourcing another file, etc.)
    that handles differences between operating systems and shell.
    '''
    def __init__(self,system:str=None,shell=None):
        self.system = system.lower() if system else platform.system().lower()
        self.shell = pathlib.Path(shell if shell else get_shell())

    def cd(self,dirname:pathlib.Path):
        cmd = ["cd",str(dirname)]
        return shlex.join(cmd)

    def mkdir(self,dirname:pathlib.Path, make_parents=True):
        cmd = None
        if self.system == "linux":
            if make_parents:
                cmd = [ "mkdir", "-p", str(dirname) ]
            else:
                cmd = [ "mkdir", str(dirname) ]

        if cmd is None:
            raise RuntimeError(f"System '{self.system}' is not supported for the 'mkdir' command yet.")

        return shlex.join(cmd)

    def source(self,filename:pathlib.Path):
        cmd = None
        if self.system == "linux":
            cmd = ["source",filename]

        if cmd is None:
            raise RuntimeError(f"System '{self.system}' is not supported for the 'source' command yet.")

        return shlex.join(cmd)

    def source_scripts_if_present_for_system(self,scripts,script_dir:pathlib.Path,source_from_dir:pathlib.Path):
        lines = []
        for script,system in scripts:
            script = script_dir/script
            if script.exists() and self.system == system:
                lines.append( self.source(relpath(script,source_from_dir)) )
        if len(lines):
            return '\n'.join(lines)

    def activate_environment(self,script_dir:pathlib.Path,source_from_dir:pathlib.Path):
        return self.source_scripts_if_present_for_system( [ ('activate.sh','linux'), ('activate.ps1','windows') ], script_dir, source_from_dir )

    def deactivate_environment(self,script_dir:pathlib.Path,source_from_dir:pathlib.Path):
        return self.source_scripts_if_present_for_system( [ ('deactivate.sh','linux'), ('deactivate.ps1','windows') ], script_dir, source_from_dir )

    def activate_run_environment(self,script_dir:pathlib.Path,source_from_dir:pathlib.Path):
        return self.source_scripts_if_present_for_system( [ ('activate_run.sh','linux'), ('activate_run.ps1','windows') ], script_dir, source_from_dir )

    def deactivate_run_environment(self,script_dir:pathlib.Path,source_from_dir:pathlib.Path):
        return self.source_scripts_if_present_for_system( [ ('deactivate_run.sh','linux'), ('deactivate_run.ps1','windows') ], script_dir, source_from_dir )

    def activate_build_environment(self,script_dir:pathlib.Path,source_from_dir:pathlib.Path):
        return self.source_scripts_if_present_for_system( [ ('activate_build.sh','linux'), ('activate_build.ps1','windows') ], script_dir, source_from_dir )

    def deactivate_build_environment(self,script_dir:pathlib.Path,source_from_dir:pathlib.Path):
        return self.source_scripts_if_present_for_system( [ ('deactivate_build.sh','linux'), ('deactivate_build.ps1','windows') ], script_dir, source_from_dir )


    def enable_exit_on_error(self):
        if self.shell.name == "bash":
            return "set -e"

    def call(self,filename:pathlib.Path,call_dir:pathlib.Path,args):
        '''
        Generate command to call a file from a given directory.
        '''
        rel_filename = relpath(filename,call_dir)
        if self.shell.name == "bash":
            rel_filename = "./"+rel_filename
        else:
            raise RuntimeError(f"Could not find a way to run '{filename}'.")

        return shlex.join([rel_filename] + args)


