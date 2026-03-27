# Test Suite Documentation

## Current Scope

This folder currently contains pytest scaffolding and utility scripts.

## Structure

```text
tests/
|- conftest.py                 # Pytest configuration + Django setup
|- README.md                   # This file
|- unit/                       # Unit test package scaffold
|  `- __init__.py
|- integration/                # Integration test package scaffold
|  `- __init__.py
`- utilities/                  # Helper scripts for development
  |- __init__.py
  |- check_db.py
  |- set_admin_password.py
  `- system_status.py
```

## Running Tests

### Prerequisites

```bash
pip install pytest pytest-django
```

### Run All Tests

```bash
pytest tests/
```

### Run By Package

```bash
pytest tests/unit/
pytest tests/integration/
```

### Run A Specific Test

```bash
pytest tests/unit/test_example.py
pytest tests/integration/test_example_api.py::test_recommend_endpoint_basic
```

## Existing API-Level Tests

Current API regression tests are in `backend/fins_api/tests.py`.

## Utility Scripts

### check_db.py

```bash
python tests/utilities/check_db.py
```

### set_admin_password.py

```bash
python tests/utilities/set_admin_password.py
```

### system_status.py

```bash
python tests/utilities/system_status.py
```

## Notes

- `conftest.py` initializes Django for pytest.
- Keep long-running HTTP checks out of unit tests.
- Add new tests under `tests/unit/` and `tests/integration/` as coverage grows.
