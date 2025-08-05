import pytest
import multiprocessing as mp
import sys

def pytest_configure(config):
    """Configure pytest settings"""
    # Set multiprocessing start method for Windows compatibility
    if sys.platform.startswith('win'):
        mp.set_start_method('spawn', force=True)

@pytest.fixture(scope="session")
def mp_context():
    """Provide multiprocessing context for tests"""
    return mp.get_context('spawn')

@pytest.fixture
def sample_queue():
    """Provide a sample queue for testing"""
    return mp.Queue()

@pytest.fixture
def sample_data():
    """Provide sample test data"""
    return {
        "strings": ["hello", "world", "test"],
        "numbers": [1, 2, 3, 4, 5],
        "mixed": ["hello", 123, True, None]
    }

@pytest.fixture
def sample_fixture():
    return "sample data"