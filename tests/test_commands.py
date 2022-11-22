from conan_cmake_cpp_project_tools import utils,steps,script
import tempfile
import pathlib
import subprocess
import fspathtree

def test_command_generator():
    cmd_generator = script.CmdGenerator("linux")

    assert cmd_generator.cd(pathlib.Path("tmp")) == "cd tmp"
    assert cmd_generator.cd(pathlib.Path("tmp with space")) == "cd 'tmp with space'"

    assert cmd_generator.mkdir(pathlib.Path("tmp")) == "mkdir -p tmp"
    assert cmd_generator.mkdir(pathlib.Path("tmp with space")) == "mkdir -p 'tmp with space'"


def test_build_steps():
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        (tmpdir / "Project1").mkdir(parents=True)
        (tmpdir / "Project1/src").mkdir(parents=True)
        (tmpdir / "Project1/.git").mkdir(parents=True)
        (tmpdir / "Project1/testing").mkdir(parents=True)
        (tmpdir / "Project1/conanfile.txt").write_text('''
[requires]
boost/1.72.0
[generators]
CMakeDeps
CMakeToolchain
        ''')
        (tmpdir / "Project1/CMakeLists.txt").write_text('''
cmake_minimum_required(VERSION 3.16)
project(test)
find_package(Boost REQUIRED)
add_executable(main-tests src/main.cpp)
target_link_libraries(main-tests Boost::boost)
        ''')
        (tmpdir / "Project1/src/main.cpp").write_text('''
#include <iostream>
#include <boost/units/quantity.hpp>
int main(int argc, char* argv[])
{
    std::cout << "works";
    for(int i = 1; i < argc; ++i)
    {
        std::cout << " " << argv[i];
    }
    return 0;
}
        ''')


        config = fspathtree.fspathtree()

        config["directories/root"] = tmpdir/"Project1"
        config["directories/build"] = tmpdir/"Project1/build-test"
        config["directories/scripts"] = tmpdir/"Project1"
        config["files/conanfile"] = tmpdir/"Project1/conanfile.txt"
        config["files/CMakeLists.txt"] = tmpdir/"Project1/CMakeLists.txt"
        config["platform"] = "linux"


        steps.install_deps(config,run=False)

        script_text = (tmpdir/"Project1/01-install_deps").read_text()
        script_lines = script_text.split('\n')

        assert len(script_lines) == 5
        assert script_lines[0] == "set -e"
        assert script_lines[1] == "cd "+str(tmpdir/"Project1")
        assert script_lines[2] == "mkdir -p build-test"
        assert script_lines[3] == "cd build-test"
        assert script_lines[4] == "conan install .. -pr:b=default -s build_type=Debug"


        config["conan/extra_args"] = ["-j","build-info-tree.json"]

        steps.install_deps(config,run=False)

        script_text = (tmpdir/"Project1/01-install_deps").read_text()
        script_lines = script_text.split('\n')

        assert len(script_lines) == 5
        assert script_lines[0] == "set -e"
        assert script_lines[1] == "cd "+str(tmpdir/"Project1")
        assert script_lines[2] == "mkdir -p build-test"
        assert script_lines[3] == "cd build-test"
        assert script_lines[4] == "conan install .. -pr:b=default -s build_type=Debug -j build-info-tree.json"

        cmd = utils.cmd_to_run_shell_script(tmpdir/"Project1/01-install_deps")
        res = subprocess.run(cmd)
        assert res.returncode == 0

        steps.configure_build(config,run=False)

        script_text = (tmpdir/"Project1/02-configure_build").read_text()
        script_lines = script_text.split('\n')

        assert len(script_lines) == 5
        assert script_lines[0] == "set -e"
        assert script_lines[1] == "cd "+str(tmpdir/"Project1")
        assert script_lines[2] == "mkdir -p build-test"
        assert script_lines[3] == "cd build-test"
        assert script_lines[4] == "cmake .. -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Debug"
        (tmpdir / "Project1/build-test/activate.sh").write_text('''
echo "activating virtual environment"
        ''')

        steps.configure_build(config,run=False)

        script_text = (tmpdir/"Project1/02-configure_build").read_text()
        script_lines = script_text.split('\n')

        assert len(script_lines) == 6
        assert script_lines[0] == "set -e"
        assert script_lines[1] == "cd "+str(tmpdir/"Project1")
        assert script_lines[2] == "mkdir -p build-test"
        assert script_lines[3] == "cd build-test"
        assert script_lines[4] == "source activate.sh"
        assert script_lines[5] == "cmake .. -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Debug"


        (tmpdir / "Project1/build-test/deactivate.sh").write_text('''
        ''')

        steps.configure_build(config,run=False)

        script_text = (tmpdir/"Project1/02-configure_build").read_text()
        script_lines = script_text.split('\n')

        assert len(script_lines) == 7
        assert script_lines[0] == "set -e"
        assert script_lines[1] == "cd "+str(tmpdir/"Project1")
        assert script_lines[2] == "mkdir -p build-test"
        assert script_lines[3] == "cd build-test"
        assert script_lines[4] == "source activate.sh"
        assert script_lines[5] == "cmake .. -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Debug"
        assert script_lines[6] == "source deactivate.sh"


        cmd = utils.cmd_to_run_shell_script(tmpdir/"Project1/02-configure_build")
        res = subprocess.run(cmd)
        assert res.returncode == 0


        steps.run_build(config,run=False)

        script_text = (tmpdir/"Project1/03-run_build").read_text()
        script_lines = script_text.split('\n')

        assert len(script_lines) == 6
        assert script_lines[0] == "set -e"
        assert script_lines[1] == "cd "+str(tmpdir/"Project1")
        assert script_lines[2] == "cd build-test"
        assert script_lines[3] == "source activate.sh"
        assert script_lines[4] == "cmake --build ."
        assert script_lines[5] == "source deactivate.sh"


        cmd = utils.cmd_to_run_shell_script(tmpdir/"Project1/03-run_build")
        res = subprocess.run(cmd)
        assert res.returncode == 0


        steps.run_tests(config,run=False)

        script_text = (tmpdir/"Project1/04-run_tests").read_text()
        script_lines = script_text.split('\n')

        assert len(script_lines) == 4
        assert script_lines[0] == "set -e"
        assert script_lines[1] == "cd "+str(tmpdir/"Project1")
        assert script_lines[2] == "cd build-test"
        assert script_lines[3] == "./main-tests"

        cmd = utils.cmd_to_run_shell_script(tmpdir/"Project1/04-run_tests")
        res = subprocess.run(cmd,capture_output=True)
        assert res.returncode == 0
        assert res.stdout.decode('utf-8') == "works"

        assert utils.is_exe( tmpdir/"Project1/build-test/main-tests")
        assert utils.is_debug_exe( tmpdir/"Project1/build-test/main-tests")
        files = list(utils.find_unit_test_binaries(tmpdir))
        assert len(files) == 1
        files[0].name == 'main-tests'
        files = list(filter(utils.is_debug_exe,utils.find_unit_test_binaries(tmpdir)))
        assert len(files) == 1
        files[0].name == 'main-tests'


        config["run_tests/args/*-tests"] = ['one','two']

        steps.run_tests(config,run=False)

        script_text = (tmpdir/"Project1/04-run_tests").read_text()
        script_lines = script_text.split('\n')

        assert len(script_lines) == 4
        assert script_lines[0] == "set -e"
        assert script_lines[1] == "cd "+str(tmpdir/"Project1")
        assert script_lines[2] == "cd build-test"
        assert script_lines[3] == "./main-tests one two"

        cmd = utils.cmd_to_run_shell_script(tmpdir/"Project1/04-run_tests")
        res = subprocess.run(cmd,capture_output=True)
        assert res.returncode == 0
        assert res.stdout.decode('utf-8') == "works one two"

