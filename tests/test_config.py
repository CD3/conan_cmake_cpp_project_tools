from conan_cmake_cpp_project_tools import utils
from conan_cmake_cpp_project_tools import config
import tempfile
import pathlib
import pytest

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

        cfg = config.ConfSettings()
        config.load_config_files(cfg,pathlib.Path(tmpdir)/'a/b/c/d/e', 'ccc')

        assert cfg['system'] == "Linux"
        assert cfg['shell'] == "bash"
        assert cfg['cmake/cmd'] == "/usr/bin/cmake"

        cfg = config.ConfSettings()
        config.load_config_files(cfg,pathlib.Path(tmpdir)/'a/b/c/d', 'ccc')

        assert cfg['system'] == "Linux"
        assert cfg['shell'] == "zsh"

def test_config_settings_class():

    cfg = config.ConfSettings()

    cfg['/conan/cmd'] = 'conan'
    cfg['/conan/args'] = ['install','-s', 'build_type={build_type}']
    cfg['/var'] = "val"

    assert cfg['/conan/args/0'] == "install"
    assert cfg['/conan/args/1'] == "-s"
    assert cfg['/conan/args/2'] == "build_type={build_type}"
    assert cfg['/conan/args'].tree[0] == "install"
    assert cfg['/conan/args'].tree[1] == "-s"
    assert cfg['/conan/args'].tree[2] == "build_type={build_type}"

    assert cfg.get('/var','missing') == "val"
    with pytest.raises(KeyError) as e:
        assert cfg.get('/var2','missing') == "val"
    cfg['var2'] = config.ConfSettings.Null("Setting is known but not set")
    assert cfg.get('/var2','missing') == "missing"
    assert cfg['/var2'].msg  == "Setting is known but not set"

    cfg.allow_missing_keys(True)
    assert cfg.get('/var3','missing') == "missing"





