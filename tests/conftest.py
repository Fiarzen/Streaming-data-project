"""
Configuration file for pytest.
"""
import pytest
import os
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_env_variables():
    """Mock environment variables for all tests by default."""
    with patch.dict(os.environ, {"GUARDIAN_API_KEY": "test-api-key"}):
        yield

def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )