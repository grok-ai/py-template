"""Tests for template rendering."""

import subprocess
from pathlib import Path

import pytest

from conftest import get_package_name


class TestProjectStructure:
    """Tests for generated project structure."""

    def test_package_directory_created(self, default_project: Path, default_copier_args: dict):
        package_name = get_package_name(default_copier_args["project_name"])
        package_dir = default_project / "src" / package_name
        assert package_dir.exists()
        assert package_dir.is_dir()

    def test_init_file_created(self, default_project: Path, default_copier_args: dict):
        package_name = get_package_name(default_copier_args["project_name"])
        init_file = default_project / "src" / package_name / "__init__.py"
        assert init_file.exists()

    def test_utils_file_created(self, default_project: Path, default_copier_args: dict):
        package_name = get_package_name(default_copier_args["project_name"])
        utils_file = default_project / "src" / package_name / "utils.py"
        assert utils_file.exists()

    def test_tests_directory_created(self, default_project: Path):
        tests_dir = default_project / "tests"
        assert tests_dir.exists()
        assert tests_dir.is_dir()

    def test_pyproject_created(self, default_project: Path):
        pyproject = default_project / "pyproject.toml"
        assert pyproject.exists()

    def test_readme_created(self, default_project: Path):
        readme = default_project / "README.md"
        assert readme.exists()


class TestPyprojectRendering:
    """Tests for pyproject.toml rendering."""

    def test_project_name_in_pyproject(self, default_project: Path, default_copier_args: dict):
        pyproject = default_project / "pyproject.toml"
        content = pyproject.read_text()
        expected_name = default_copier_args["project_name"].lower().replace(" ", "-")
        assert f'name = "{expected_name}"' in content

    def test_description_in_pyproject(self, default_project: Path, default_copier_args: dict):
        pyproject = default_project / "pyproject.toml"
        content = pyproject.read_text()
        assert f'description = "{default_copier_args["description"]}"' in content


class TestReadmeRendering:
    """Tests for README.md rendering."""

    def test_project_name_in_readme(self, default_project: Path, default_copier_args: dict):
        readme = default_project / "README.md"
        content = readme.read_text()
        assert default_copier_args["project_name"] in content
        assert "{{ project_name }}" not in content
        assert "undefined" not in content.lower()

    def test_description_in_readme(self, default_project: Path, default_copier_args: dict):
        readme = default_project / "README.md"
        content = readme.read_text()
        assert default_copier_args["description"] in content


class TestPrecommitConfig:
    """Tests for pre-commit configuration."""

    def test_precommit_config_when_enabled(self, precommit_enabled_project: Path):
        precommit_config = precommit_enabled_project / ".pre-commit-config.yaml"
        assert precommit_config.exists()
        content = precommit_config.read_text()
        assert "repos:" in content

    def test_precommit_config_when_disabled(self, default_project: Path):
        """default_project already has use_precommit=False."""
        precommit_config = default_project / ".pre-commit-config.yaml"
        if precommit_config.exists():
            content = precommit_config.read_text().strip()
            lines = [
                line for line in content.split("\n") if not line.strip().startswith("#")
            ]
            assert "repos:" not in "\n".join(lines)


class TestGitInitialization:
    """Tests for Git initialization."""

    def test_git_initialized(self, default_project: Path):
        git_dir = default_project / ".git"
        assert git_dir.exists()
        assert git_dir.is_dir()

    def test_initial_commit_created(self, default_project: Path):
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=default_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Project initialization" in result.stdout


class TestDependencyInstallation:
    """Tests for dependency installation (when env_init=True)."""

    @pytest.mark.slow
    def test_uv_sync_succeeds(self, env_init_project: Path):
        result = subprocess.run(
            ["uv", "sync"],
            cwd=env_init_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"uv sync failed: {result.stderr}"


class TestPythonImports:
    """Tests for Python import functionality in generated projects."""

    @pytest.mark.slow
    def test_package_imports_successfully(self, env_init_project: Path, default_copier_args: dict):
        package_name = get_package_name(default_copier_args["project_name"])
        result = subprocess.run(
            ["uv", "run", "python", "-c", f"import {package_name}"],
            cwd=env_init_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Import failed: {result.stderr}"

    @pytest.mark.slow
    def test_package_exports_available(self, env_init_project: Path, default_copier_args: dict):
        package_name = get_package_name(default_copier_args["project_name"])
        import_code = f"""
from {package_name} import get_project_root
from {package_name}.utils import get_env, load_envs, environ, seed_everything
print('All exports imported successfully')
print('PROJECT_ROOT:', get_project_root())
"""
        result = subprocess.run(
            ["uv", "run", "python", "-c", import_code],
            cwd=env_init_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Import failed: {result.stderr}"
        assert "All exports imported successfully" in result.stdout

    @pytest.mark.slow
    def test_hyphenated_project_name_creates_valid_package(self, hyphenated_project: Path):
        package_name = get_package_name("my-cool-project")
        package_dir = hyphenated_project / "src" / package_name
        assert package_dir.exists(), f"Package directory {package_name} not found"

        result = subprocess.run(
            ["uv", "run", "python", "-c", f"import {package_name}; print('OK')"],
            cwd=hyphenated_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Import failed: {result.stderr}"
        assert "OK" in result.stdout

    @pytest.mark.slow
    def test_generated_tests_pass(self, env_init_project: Path):
        result = subprocess.run(
            ["uv", "run", "pytest", "tests", "-v"],
            cwd=env_init_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Tests failed: {result.stdout}\n{result.stderr}"
