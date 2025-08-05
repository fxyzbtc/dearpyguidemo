# DearPyGui Demo Project

A comprehensive demonstration project showcasing various integration patterns with DearPyGui, including threading, task queues, and multiprocessing approaches for building responsive GUI applications.

## Demonstrations

| File | Description | Key Features |
|------|-------------|--------------|
| `hello.py` | **Threading + Queue Demo** | Basic GUI with background worker thread using Python threading and queues for progress updates |
| `hello_huey.py` | **Huey Task Queue Integration** | Advanced GUI demonstrating Huey task queue integration with real-time progress tracking and comprehensive logging |

### Test Demonstrations

| File | Description | Purpose |
|------|-------------|---------|
| `tests/test_hello.py` | Unit tests for basic threading demo | Testing thread-based GUI components |
| `tests/test_hello_huey.py` | Unit tests for Huey integration | Testing task queue functionality |
| `tests/test_queue.py` | Queue-based worker testing | Multiprocessing queue communication patterns |
| `tests/test_queue_fixed.py` | Enhanced queue worker tests | Improved queue handling with error recovery |
| `tests/test_mp.py` | Multiprocessing demonstrations | Process-based parallelism examples |
| `tests/test_combined_filter.py` | Combined filtering operations | Data processing and filtering demonstrations |

## Key Technologies

- **DearPyGui**: Modern, fast Python GUI framework
- **Huey**: Lightweight task queue for background processing
- **Threading**: Python threading for concurrent operations
- **Multiprocessing**: Process-based parallelism
- **Queue**: Inter-thread/process communication

## Features Demonstrated

### Threading Integration (`hello.py`)
- Background worker threads
- Thread-safe queue communication
- Real-time progress updates
- Non-blocking GUI operations

### Huey Task Queue (`hello_huey.py`)
- Task queue management
- Background task execution
- Progress tracking with global state
- Comprehensive logging system
- Memory-based task storage
- Frame-based polling for UI updates

## Installation

### Prerequisites
- Python 3.12 or higher
- UV package manager (recommended) or pip

### Using UV (Recommended)
```bash
# Clone the repository
git clone https://github.com/fxyzbtc/dearpyguidemo.git
cd dearpyguidemo

# Install dependencies
uv sync

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### Using Pip
```bash
# Clone the repository
git clone https://github.com/fxyzbtc/dearpyguidemo.git
cd dearpyguidemo

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -e .
```

## Running the Demos

### Basic Threading Demo
```bash
python hello.py
```
Features a simple GUI with:
- Start Job button to begin background work
- Real-time progress bar
- Log output window
- Clear Log functionality

### Advanced Huey Integration Demo
```bash
python hello_huey.py
```
Features an advanced GUI with:
- Multiple task types (simulation, network, file operations)
- Real-time progress tracking
- Comprehensive logging
- Task queue management
- Background consumer threads

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test files
pytest tests/test_hello.py
pytest tests/test_hello_huey.py
```

## Project Structure

```
dearpyguidemo/
├── hello.py                    # Basic threading demo
├── hello_huey.py              # Huey task queue demo
├── tests/                     # Test suite
│   ├── test_hello.py         # Threading demo tests
│   ├── test_hello_huey.py    # Huey demo tests
│   ├── test_queue.py         # Queue communication tests
│   ├── test_queue_fixed.py   # Enhanced queue tests
│   ├── test_mp.py            # Multiprocessing tests
│   └── test_combined_filter.py # Data filtering tests
├── pyproject.toml             # Project configuration
├── pytest.ini                # Test configuration
├── uv.lock                    # Dependency lock file
└── README.md                  # This file
```

## Dependencies

### Core Dependencies
- `dearpygui>=2.1.0` - Modern Python GUI framework
- `huey>=2.5.3` - Lightweight task queue
- `matplotlib>=3.10.5` - Plotting and visualization
- `networkx>=3.5` - Network analysis library
- `tqdm>=4.67.1` - Progress bars for command line

### Development Dependencies
- `pytest>=8.4.1` - Testing framework
- `pytest-cov>=6.2.1` - Coverage testing
- `coverage>=7.10.2` - Code coverage analysis

## Contributing

We welcome contributions! Here are some ways you can help:

### Ways to Contribute
1. **Report Bugs**: Open an issue describing the bug and steps to reproduce
2. **Suggest Features**: Propose new demonstrations or improvements
3. **Submit Pull Requests**: Add new examples or fix existing issues
4. **Improve Documentation**: Help improve code comments and README

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to functions and classes
- Include type hints where appropriate
- Write tests for new functionality

## Links

- **Homepage**: [GitHub Repository](https://github.com/fxyzbtc/dearpyguidemo)
- **Issues**: [Report Issues](https://github.com/fxyzbtc/dearpyguidemo/issues)
- **Pull Requests**: [Contribute Code](https://github.com/fxyzbtc/dearpyguidemo/pulls)
- **DearPyGui Documentation**: [https://dearpygui.readthedocs.io/](https://dearpygui.readthedocs.io/)
- **Huey Documentation**: [https://huey.readthedocs.io/](https://huey.readthedocs.io/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [DearPyGui](https://github.com/hoffstadt/DearPyGui) - Amazing Python GUI framework
- [Huey](https://github.com/coleifer/huey) - Simple and efficient task queue
- Python community for excellent threading and multiprocessing libraries