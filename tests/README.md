# Tests for canlab

This directory contains the test suite for the canlab library.

**BEFORE RUNNING:** See GitHub Issues relating to tests

## Running Tests

### Install Test Dependencies

```bash
pip install -e ".[dev]"
# or
uv pip install -e ".[dev]"
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run specific test file
pytest tests/test_encoder_decoder.py
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

## Test Structure

- `test_encoder_decoder.py` - Tests for CAN frame encoding and decoding (LSB/MSB)
- `test_conversions.py` - Tests for ID conversion functions
- `test_dbc_loader.py` - Tests for DBC file loading and parsing
- `test_asc_parser.py` - Tests for ASC log file parsing
- `test_integration.py` - Integration tests for full workflows
- `conftest.py` - Pytest configuration and fixtures
- `data/` - Test data files (DBC and ASC samples)

## Test Data

The `data/` directory contains sample files used for testing:
- `sample.dbc` - Sample DBC file with messages and signals
- `sample.asc` - Sample ASC log file
- `sample2.asc` - Alternative ASC log file format

## Writing New Tests

When adding new tests:

1. Follow the naming convention: `test_*.py` for test files, `test_*` for test functions
2. Use pytest markers: `@pytest.mark.unit` or `@pytest.mark.integration`
3. Use fixtures from `conftest.py` when possible
4. Add test data files to `data/` if needed

**Note:** The current test suite has been generated using A.I.