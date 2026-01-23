"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

import pytest

# Add src to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def data_dir(project_root):
    """Return the data directory path."""
    return project_root / "data"


@pytest.fixture
def images_dir(project_root):
    """Return the images directory path."""
    return project_root / "images"
