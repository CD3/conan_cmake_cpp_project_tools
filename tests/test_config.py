from conan_cmake_cpp_project_tools import utils
from conan_cmake_cpp_project_tools import config
import tempfile
import pathlib

def test_load_config_from_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        (pathlib.Path(tmpdir) / "a/b/c/d/e").mkdir(parents=True)
        (pathlib.Path(tmpdir) / "a/b/c/d/e/ccc.yml").write_text('''
shell: bash
cmake:
    cmd: /usr/bin/cmake
        ''')

        (pathlib.Path(tmpdir) / "a/b/c/d/ccc.yml").write_text('''
system : Linux
        ''')

        (pathlib.Path(tmpdir) / "a/b/c/ccc.yml").write_text('''
shell: zsh
        ''')

        cfg = config.fspathtree()
        config.load_config_files(cfg,pathlib.Path(tmpdir)/'a/b/c/d/e', 'ccc')

        assert cfg['system'] == "Linux"
        assert cfg['shell'] == "bash"
        assert cfg['cmake/cmd'] == "/usr/bin/cmake"

        cfg = config.fspathtree()
        config.load_config_files(cfg,pathlib.Path(tmpdir)/'a/b/c/d', 'ccc')

        assert cfg['system'] == "Linux"
        assert cfg['shell'] == "zsh"
