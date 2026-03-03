"""Shared test fixtures and configuration."""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Fixture that saves and restores environment variables after the test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Fixture that creates a temporary directory and cleans it up after the test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_env_file(temp_dir: Path) -> Path:
    """Fixture that creates a temporary .env file."""
    env_file = temp_dir / ".env"
    env_file.write_text("TEST_VAR=test_value\nANOTHER_VAR=another_value\n")
    return env_file
