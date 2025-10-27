# Installation Guide

## Overview

The MEGA DeFi Profit Machine is now available as a fully installable Python package with modern packaging infrastructure following Python Enhancement Proposals (PEPs) standards.

## Installation Methods

### Method 1: Install from Source (Development)

For development or to get the latest version:

```bash
# Clone the repository
git clone https://github.com/fxgeniusllc-oss/MEGA_-DEFI-.git
cd MEGA_-DEFI-

# Install in editable mode (recommended for development)
pip install -e .
```

This allows you to make changes to the code and see them immediately reflected without reinstalling.

### Method 2: Install with Development Tools

If you plan to contribute or run tests:

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

This installs additional tools:
- `pytest` - For running tests
- `pytest-cov` - For code coverage
- `black` - For code formatting
- `flake8` - For linting
- `mypy` - For type checking

### Method 3: Build and Install Distribution

To create distribution packages:

```bash
# Build the package
python3 setup.py sdist bdist_wheel

# Install the built package
pip install dist/mega_defi-1.0.0-py3-none-any.whl
```

## Verifying Installation

After installation, verify it works:

```python
# Test import
python3 -c "from mega_defi.profit_machine import create_profit_machine; print('✅ Installation successful!')"

# Run examples
python3 examples/basic_usage.py
python3 examples/advanced_simulation.py
```

## Running Tests

```bash
# Run all tests
python3 -m unittest discover tests/ -v

# With pytest (if dev dependencies installed)
pytest tests/ -v
```

## Package Features

- **Zero runtime dependencies**: Pure Python implementation
- **Modern packaging**: Uses `pyproject.toml` (PEP 621)
- **Backward compatible**: Includes `setup.py` for older pip versions
- **Type hints**: Prepared for future type checking
- **Comprehensive tests**: 23+ unit tests covering all components

## Package Structure

```
mega-defi/
├── mega_defi/           # Main package
│   ├── __init__.py
│   ├── profit_machine.py
│   └── core/            # Core components
│       ├── __init__.py
│       ├── strategy_engine.py
│       ├── market_analyzer.py
│       ├── risk_manager.py
│       └── profit_optimizer.py
├── tests/               # Unit tests
├── examples/            # Usage examples
├── pyproject.toml       # Modern packaging config
├── setup.py             # Backward compatible setup
└── README.md            # Main documentation
```

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed:

```bash
pip list | grep mega-defi
```

### Test Failures

Run tests with verbose output:

```bash
python3 -m unittest discover tests/ -v
```

## Uninstalling

```bash
pip uninstall mega-defi
```

## Building Documentation

The package includes inline documentation. To view:

```python
import mega_defi
help(mega_defi.profit_machine.ProfitMachine)
```

## Contributing

When contributing:

1. Install with dev dependencies: `pip install -e ".[dev]"`
2. Run tests before committing: `python3 -m unittest discover tests/`
3. Format code: `black mega_defi/ tests/`
4. Check linting: `flake8 mega_defi/`

## Future Publishing

To publish to PyPI (maintainers only):

```bash
# Install publishing tools
pip install twine

# Build distributions
python3 setup.py sdist bdist_wheel

# Upload to PyPI
twine upload dist/*
```

After publishing, users can install with:
```bash
pip install mega-defi
```
