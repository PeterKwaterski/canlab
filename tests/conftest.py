"""Pytest configuration and fixtures for canlab tests."""
import os
from pathlib import Path

import pytest


@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_dbc_path(test_data_dir):
    """Return the path to the sample DBC file."""
    return test_data_dir / "sample.dbc"


@pytest.fixture
def sample_asc_path(test_data_dir):
    """Return the path to the sample ASC file."""
    return test_data_dir / "sample.asc"


@pytest.fixture
def sample_asc2_path(test_data_dir):
    """Return the path to the second sample ASC file."""
    return test_data_dir / "sample2.asc"
