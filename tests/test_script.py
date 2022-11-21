from conan_cmake_cpp_project_tools import Script
from conan_cmake_cpp_project_tools import utils
import tempfile
import pathlib
import subprocess



def test_writing_shell_script():
    script = Script(shell="bash")
    script.add_command(['echo','hello','world'])

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmppath = pathlib.Path(tmpdirname)

        script.write( tmppath/"script.sh" )

        lines = (tmppath/"script.sh").read_text().split("\n")
        assert len(lines) == 1
        assert lines[0] == "echo hello world"

        script.write( tmppath/"script.sh", exit_on_error=True )

        lines = (tmppath/"script.sh").read_text().split("\n")
        assert len(lines) == 2
        assert lines[0] == "set -e"
        assert lines[1] == "echo hello world"

        
        # subprocess.check_output( 





