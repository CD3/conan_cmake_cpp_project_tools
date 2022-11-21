
from typer.testing import CliRunner

from conan_cmake_cpp_project_tools.cli import *


runner = CliRunner()

def test_app():
  result = runner.invoke(app, ['--help'])
  assert result.exit_code == 0
  assert "Usage: ccc" in result.stdout

