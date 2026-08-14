"""
Pytest configuration and fixtures for LibRA tests.
"""
import pytest
import os
import sys
import shutil
from pathlib import Path

# Test configuration
pytest_plugins = []

@pytest.fixture(scope="session")
def gold_standard_dir():
    """Fixture to provide the test data directory path."""
    # Start from test directory and look for gold_standard
    test_dir = Path(__file__).parent
    
    # Check if gold_standard exists locally in tests/
    local_gold_dir = test_dir / "gold_standard"
    if local_gold_dir.exists():
        return local_gold_dir
    
    # Look for it in the main repository structure (relative path)
    # Go up from libra-python/tests/ to libra/apps/src/tests/gold_standard
    repo_gold_dir = test_dir.parent.parent / "apps" / "src" / "tests" / "gold_standard"
    if repo_gold_dir.exists():
        return repo_gold_dir
    
    # If neither exists, return None - tests requiring data will skip
    return None

@pytest.fixture(scope="session") 
def libra_verbose():
    """Enable verbose LibRA output for tests."""
    original_value = os.environ.get('LIBRA_VERBOSE', '')
    os.environ['LIBRA_VERBOSE'] = '1'
    yield
    if original_value:
        os.environ['LIBRA_VERBOSE'] = original_value
    else:
        os.environ.pop('LIBRA_VERBOSE', None)

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test" 
    )