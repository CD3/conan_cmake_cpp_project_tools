from conan_cmake_cpp_project_tools import utils
from conan_cmake_cpp_project_tools import config
import tempfile
import pathlib
import pytest

def test_config_setting_updates():

    cfg = config.ConfSettings()
    cfg['a/b/v1'] = 'one'
    cfg['a/b/v2'] = ['two', 'three']

    assert cfg.tree['a']['b']['v1'] == 'one'
    assert cfg.tree['a']['b']['v2'][0] == 'two'
    assert cfg.tree['a']['b']['v2'][1] == 'three'

    keys = [ str(p) for p in cfg.get_all_leaf_node_paths() ]
    assert '/a/b/v1' in keys
    assert '/a/b/v2/0' in keys
    assert '/a/b/v2/1' in keys

    cfg2 = config.ConfSettings()
    cfg2['/a/v1'] = 'four'

    cfg.update(cfg2)

    assert cfg['/a/v1'] == "four"
    assert cfg['/a/b/v1'] == "one"
    assert cfg['/a/b/v2/0'] == "two"
    assert cfg['/a/b/v2/1'] == "three"

def test_load_config_from_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        (pathlib.Path(tmpdir) / "a/b/c/d/e").mkdir(parents=True)
        (pathlib.Path(tmpdir) / "a/b/c/d/e/ccc.yml").write_text('''
shell: bash
cmake:
    cmd: /usr/bin/cmake
    args:
        - "-DCMAKE_BUILD_TYPE=Debug"
        ''')
        (pathlib.Path(tmpdir) / "a/b/c/d/e/ccc-user.yml").write_text('''
cmake:
    cmd: /usr/local/bin/cmake
        ''')

        (pathlib.Path(tmpdir) / "a/b/c/d/ccc.yml").write_text('''
system : Linux
        ''')

        (pathlib.Path(tmpdir) / "a/b/c/ccc.yml").write_text('''
shell: zsh
        ''')

        cfg = config.ConfSettings()
        config.load_config_files(cfg,pathlib.Path(tmpdir)/'a/b/c/d/e', 'ccc')

        assert cfg['/system'] == "Linux"
        assert cfg['/shell'] == "bash"
        assert cfg['/cmake/cmd'] == "/usr/bin/cmake"
        assert cfg['/cmake/args/0'] == "-DCMAKE_BUILD_TYPE=Debug"

        cfg = config.ConfSettings()
        config.load_config_files(cfg,pathlib.Path(tmpdir)/'a/b/c/d', 'ccc')

        assert cfg['/system'] == "Linux"
        assert cfg['/shell'] == "zsh"


        cfg = config.ConfSettings()
        config.load_config_files(cfg,pathlib.Path(tmpdir)/'a/b/c/d/e', 'ccc')

        assert cfg['/system'] == "Linux"
        assert cfg['/shell'] == "bash"
        assert cfg['/cmake/cmd'] == "/usr/bin/cmake"
        assert cfg['/cmake/args/0'] == "-DCMAKE_BUILD_TYPE=Debug"

        config.load_config_files(cfg,pathlib.Path(tmpdir)/'a/b/c/d/e', 'ccc-user')

        assert cfg['/system'] == "Linux"
        assert cfg['/shell'] == "bash"
        assert cfg['/cmake/cmd'] == "/usr/local/bin/cmake"
        assert cfg['/cmake/args/0'] == "-DCMAKE_BUILD_TYPE=Debug"


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





