from conan_cmake_cpp_project_tools import utils
import platform
import shutil
import pathlib
import os
import stat
import tempfile

def test_running_scripts():
    cmd = utils.cmd_to_run_shell_script("run.sh",return_as_string=True)
    assert cmd == shutil.which("bash")+" run.sh"

def test_relative_paths():

    here = pathlib.Path().absolute()
    
    assert os.path.relpath(here.parent.absolute(), here.absolute()) == ".."
    assert os.path.relpath(here.parent.absolute(), here) == ".."


def test_find_files():

    with tempfile.TemporaryDirectory() as tmpdir:
        (pathlib.Path(tmpdir) / "a/b/c/d/e").mkdir(parents=True)
        (pathlib.Path(tmpdir) / "a/b/c/d/e/file.txt").write_text('')
        (pathlib.Path(tmpdir) / "a/b/c/d/file.txt").write_text('')
        (pathlib.Path(tmpdir) / "a/b/c/d/file.bin").write_text('')
        (pathlib.Path(tmpdir) / "a/b/c/file.txt").write_text('')
        (pathlib.Path(tmpdir) / "a/b/c/file.bin").write_text('')
        (pathlib.Path(tmpdir) / "a/b/file.txt").write_text('')
        (pathlib.Path(tmpdir) / "a/CMakeLists.txt").write_text('')
        (pathlib.Path(tmpdir) / "a/b/c/.git").write_text('')

        files = list(utils.find_file_at_or_below(pathlib.Path(tmpdir),"file.txt"))
        
        assert len(files) == 4
        assert str(files[0]) == tmpdir+"/a/b/file.txt"
        assert str(files[1]) == tmpdir+"/a/b/c/file.txt"
        assert str(files[2]) == tmpdir+"/a/b/c/d/file.txt"
        assert str(files[3]) == tmpdir+"/a/b/c/d/e/file.txt"
        assert type(files[0]) == type(pathlib.Path())

        files = list(utils.find_file_at_or_below(pathlib.Path(tmpdir),"file.bin"))
        
        assert len(files) == 2
        assert str(files[0]) == tmpdir+"/a/b/c/file.bin"
        assert str(files[1]) == tmpdir+"/a/b/c/d/file.bin"

        files = list(utils.find_file_at_or_below(pathlib.Path(tmpdir)/"a","file.txt"))
        
        assert len(files) == 4
        assert str(files[0]) == tmpdir+"/a/b/file.txt"
        assert str(files[1]) == tmpdir+"/a/b/c/file.txt"
        assert str(files[2]) == tmpdir+"/a/b/c/d/file.txt"
        assert str(files[3]) == tmpdir+"/a/b/c/d/e/file.txt"

        files = list(utils.find_file_at_or_below(pathlib.Path(tmpdir)/"a/b","file.txt"))
        
        assert len(files) == 4
        assert str(files[0]) == tmpdir+"/a/b/file.txt"
        assert str(files[1]) == tmpdir+"/a/b/c/file.txt"
        assert str(files[2]) == tmpdir+"/a/b/c/d/file.txt"
        assert str(files[3]) == tmpdir+"/a/b/c/d/e/file.txt"


        files = list(utils.find_file_at_or_below(pathlib.Path(tmpdir)/"a/b/c","file.txt"))
        
        assert len(files) == 3
        assert str(files[0]) == tmpdir+"/a/b/c/file.txt"
        assert str(files[1]) == tmpdir+"/a/b/c/d/file.txt"
        assert str(files[2]) == tmpdir+"/a/b/c/d/e/file.txt"

        files = list(utils.find_file_at_or_above(pathlib.Path(tmpdir)/"a","file.txt"))
        
        assert len(files) == 0

        files = list(utils.find_file_at_or_above(pathlib.Path(tmpdir)/"a/b","file.txt"))
        
        assert len(files) == 1
        assert str(files[0]) == tmpdir+"/a/b/file.txt"

        files = list(utils.find_file_at_or_above(pathlib.Path(tmpdir)/"a/b","file.txt"))
        
        assert len(files) == 1

        root = utils.find_project_root(pathlib.Path(tmpdir)/"a/b/c/d")
        assert str(root) == tmpdir + "/a/b/c"

        root = utils.find_project_root(pathlib.Path(tmpdir)/"a/b/c")
        assert str(root) == tmpdir + "/a/b/c"

        root = utils.find_project_root(pathlib.Path(tmpdir)/"a/b")
        assert str(root) == tmpdir + "/a"

        root = utils.find_project_root(pathlib.Path(tmpdir)/"a")
        assert str(root) == tmpdir + "/a"

        root = utils.find_project_root(pathlib.Path(tmpdir))
        assert root is None




def test_working_directory_context_manager():

    cwd = os.getcwd()

    with tempfile.TemporaryDirectory() as tmpdir:
        assert os.getcwd() == cwd
        with utils.working_directory(tmpdir):
            assert os.getcwd() == tmpdir
        assert os.getcwd() == cwd

def test_list_source_files():

    with tempfile.TemporaryDirectory() as tmpdir:
        (pathlib.Path(tmpdir) / "a/b/c/d/e").mkdir(parents=True)
        (pathlib.Path(tmpdir) / "a/b/c/d/e/file.txt").write_text('')
        (pathlib.Path(tmpdir) / "a/b/c/d/file.txt").write_text('')
        (pathlib.Path(tmpdir) / "a/b/c/d/file.bin").write_text('')
        (pathlib.Path(tmpdir) / "a/b/c/file.txt").write_text('')
        (pathlib.Path(tmpdir) / "a/b/c/file.bin").write_text('')
        (pathlib.Path(tmpdir) / "a/b/file.txt").write_text('')
        (pathlib.Path(tmpdir) / "a/CMakeLists.txt").write_text('')
        (pathlib.Path(tmpdir) / "a/conanfile.py").write_text('')
        
        assert not utils.is_git_repo( pathlib.Path(tmpdir) / "a/b/c/")
        assert not utils.is_git_repo( pathlib.Path(tmpdir) / "a/b/")
        files = list(utils.get_source_files(pathlib.Path(tmpdir)))
        assert len(files) == 8
        files = list(utils.get_source_files(pathlib.Path(tmpdir), lambda p: p.name == 'file.bin'))
        assert len(files) == 2

        files = list(utils.get_source_files(pathlib.Path(tmpdir), utils.make_file_matches_pattern_filter('*.txt') ))
        assert len(files) == 5

        files = list(utils.get_source_files(pathlib.Path(tmpdir), utils.make_file_matches_pattern_filter('*.txt','*.bin') ))
        assert len(files) == 7

        files = list(utils.get_source_files(pathlib.Path(tmpdir), lambda p : utils.make_file_matches_pattern_filter('*.txt','*.bin')(p) and not utils.make_file_matches_pattern_filter('*.txt')(p) ))
        assert len(files) == 2



def test_cmd_option_cfg_entry_parsing():

    data = utils.parse_option_to_config_entry("/directories/build : /home/user/build")
    assert '/directories/build' in data
    assert data['/directories/build'] == '/home/user/build'

    data = utils.parse_option_to_config_entry(''''/directories/build ' : " /home/user/build"''')
    assert '/directories/build ' in data
    assert data['/directories/build '] == ' /home/user/build'

    data = utils.parse_option_to_config_entry(''''/list' : ["a","b"]''')
    assert '/list' in data
    assert len(data['/list']) == 2
    assert type(data['/list']) == list

def test_find_test_binaries():
    with tempfile.TemporaryDirectory() as tmpdir:
        (pathlib.Path(tmpdir) / "a/b/c/d/e").mkdir(parents=True)
        files = ['a/b/c/d/e/unit-tests', 'a/b/c/d/e/build-script', 'a/b/c/d/project-CatchTests']

        for file in files:
            file = pathlib.Path(tmpdir) / file
            file.write_text('')

        tests_binaries = list(utils.find_unit_test_binaries(pathlib.Path(tmpdir)))
        assert len(tests_binaries) == 0

        tests_binaries = list(utils.find_unit_test_binaries(pathlib.Path(tmpdir), include_patterns='*build*'))
        assert len(tests_binaries) == 0

        tests_binaries = list(utils.find_unit_test_binaries(pathlib.Path(tmpdir), include_patterns='*build*', exclude_patterns=['*']))
        assert len(tests_binaries) == 0

        for file in files:
            file = pathlib.Path(tmpdir) / file
            os.chmod(file, os.stat(file).st_mode | stat.S_IEXEC)



        tests_binaries = list(utils.find_unit_test_binaries(pathlib.Path(tmpdir)))
        assert len(tests_binaries) == 2

        tests_binaries = list(utils.find_unit_test_binaries(pathlib.Path(tmpdir), include_patterns=['*build*']))
        assert len(tests_binaries) == 1

        tests_binaries = list(utils.find_unit_test_binaries(pathlib.Path(tmpdir), include_patterns='*build*', exclude_patterns=['*']))
        assert len(tests_binaries) == 0


