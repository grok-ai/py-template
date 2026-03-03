"""Test configuration for template-level tests."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Generator

import pytest
import yaml


def get_package_name(project_name: str) -> str:
    """Compute package_name from project_name.

    Must match the logic in copier.yml:
        {{ project_name | lower | replace(' ', '_') | replace('-', '_') }}
    """
    return project_name.lower().replace(" ", "_").replace("-", "_")


def generate_project(
    template_dir: Path,
    output_dir: Path,
    **kwargs,
) -> Path:
    """Generate a project from the template with the given options.

    Args:
        template_dir: Path to the template directory.
        output_dir: Path to the output directory.
        **kwargs: Additional copier arguments.

    Returns:
        Path to the generated project.
    """
    cmd = [
        "uvx",
        "copier",
        "copy",
        "--trust",
        "--force",
        str(template_dir),
        str(output_dir),
    ]

    for key, value in kwargs.items():
        if isinstance(value, bool):
            cmd.extend(["-d", f"{key}={str(value).lower()}"])
        elif isinstance(value, (list, dict)):
            cmd.extend(["-d", f"{key}={yaml.dump(value)}"])
        else:
            cmd.extend(["-d", f"{key}={value}"])

    # Use env vars for git config to avoid mutating global config
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Test User",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test User",
        "GIT_COMMITTER_EMAIL": "test@example.com",
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "init.defaultBranch",
        "GIT_CONFIG_VALUE_0": "main",
    }

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"Copier failed: {result.stderr}\n{result.stdout}")

    return output_dir


# ---------------------------------------------------------------------------
# Session-scoped fixtures 
# NOTE: Tests using these must be READ-ONLY -- do not modify the project dir.
# Use temp_project_dir (function-scoped) if you need a mutable project.
# ---------------------------------------------------------------------------

DEFAULT_COPIER_ARGS = {
    "project_name": "testpkg",
    "description": "A test project",
    "remote_url": "",
    "use_precommit": False,
    "env_init": False,
    "license": "MIT",
    "python_version": ">=3.9",
    "maintainers": [{"name": "Test User", "email": "test@example.com"}],
    "extra_dependencies": [],
}


@pytest.fixture(scope="session")
def template_dir() -> Path:
    """Return the path to the template directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def default_copier_args() -> dict:
    """Default arguments for copier copy."""
    return dict(DEFAULT_COPIER_ARGS)


@pytest.fixture(scope="session")
def default_project(template_dir: Path) -> Generator[Path, None, None]:
    """Project generated with default args (env_init=False, use_precommit=False).

    Shared by: TestProjectStructure, TestPyprojectRendering,
               TestReadmeRendering, TestGitInitialization,
               TestPrecommitConfig.test_precommit_config_when_disabled.
    """
    with tempfile.TemporaryDirectory(prefix="py-template-test-default-") as tmpdir:
        generate_project(template_dir, Path(tmpdir), **DEFAULT_COPIER_ARGS)
        yield Path(tmpdir)


@pytest.fixture(scope="session")
def precommit_enabled_project(template_dir: Path) -> Generator[Path, None, None]:
    """Project generated with use_precommit=True."""
    args = {**DEFAULT_COPIER_ARGS, "use_precommit": True}
    with tempfile.TemporaryDirectory(prefix="py-template-test-precommit-") as tmpdir:
        generate_project(template_dir, Path(tmpdir), **args)
        yield Path(tmpdir)


@pytest.fixture(scope="session")
def env_init_project(template_dir: Path) -> Generator[Path, None, None]:
    """Project generated with env_init=True (deps installed)."""
    args = {**DEFAULT_COPIER_ARGS, "env_init": True}
    with tempfile.TemporaryDirectory(prefix="py-template-test-envinit-") as tmpdir:
        project_dir = Path(tmpdir)
        generate_project(template_dir, project_dir, **args)
        yield project_dir


@pytest.fixture(scope="session")
def hyphenated_project(template_dir: Path) -> Generator[Path, None, None]:
    """Project generated with a hyphenated name (env_init=True)."""
    args = {**DEFAULT_COPIER_ARGS, "project_name": "my-cool-project", "env_init": True}
    with tempfile.TemporaryDirectory(prefix="py-template-test-hyphen-") as tmpdir:
        project_dir = Path(tmpdir)
        generate_project(template_dir, project_dir, **args)
        yield project_dir


# Function-scoped fixture for tests that need a mutable project
@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Create a fresh temporary directory (use for tests that modify the project)."""
    with tempfile.TemporaryDirectory(prefix="py-template-test-") as tmpdir:
        yield Path(tmpdir)
