# Test Suite Documentation

## AI-CFD Closed-Loop Context

This test suite supports an AI + CFD style optimization loop:

1. AI generates design candidates.
2. Physics behavior is evaluated (directly or via modeled/surrogate behavior).
3. Results are validated against constraints.
4. Designs are accepted or sent back for improvement.

Validation intent in this project includes checks such as:

- Drag-related performance thresholds
- Pressure drop acceptability
- Flow behavior consistency
- Thermal limits (temperature constraints)

```text
AI generates design
  ↓
CFD simulates physics
  ↓
Check performance
   ↓           ↓
 Accept      Improve
    ↓
       AI redesign
    ↓
       repeat
```

## Structure

```
tests/
├── conftest.py                 # Pytest configuration + Django setup
├── README.md                   # This file
├── unit/                       # Unit tests for individual components
│   ├── __init__.py
│   ├── test_cfd_closed_loop.py  # Closed-loop CFD + motor stress tests
│   ├── test_ml_model.py       # ML model functionality tests
│   └── test_optimizer_geometry.py  # Optimizer geometry selection tests
├── integration/                # Integration tests for API endpoints
│   ├── __init__.py
│   ├── test_api_endpoint.py    # Basic HTTP API tests
│   ├── test_api_geometry.py    # Geometry recommendation tests
│   ├── test_display_logic.py   # Frontend display formatting tests
│   └── test_recommend.py       # End-to-end pipeline tests
└── utilities/                  # Helper scripts for development
    ├── __init__.py
    ├── check_db.py            # Database inspection
    ├── set_admin_password.py   # Admin credentials management
    └── system_status.py        # System status report
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

### Run Specific Test Types

**Unit Tests Only:**

```bash
pytest tests/unit/
```

**Integration Tests Only:**

```bash
pytest tests/integration/
```

### Run Specific Test

```bash
pytest tests/unit/test_ml_model.py
pytest tests/integration/test_api_endpoint.py::test_recommend_endpoint_basic
```

### Verbose Output

```bash
pytest tests/ -v
```

### Show Print Statements

```bash
pytest tests/ -s
```

## Test Descriptions

### Unit Tests

#### `test_ml_model.py`

- Tests ML model is properly loaded
- Verifies prediction capability
- Checks output shape and validity

#### `test_optimizer_geometry.py`

- Tests geometry selection for different motor scenarios
- Verifies optimizer recommends appropriate geometries
- Validates temperature constraints

#### `test_cfd_closed_loop.py`

- Tests PASS path for the CFD closed-loop optimizer
- Tests MAX_ITERATIONS_REACHED behavior for strict constraints
- Tests motor-stress coupling (high-stress motors worsen CFD metrics)

### Integration Tests

#### `test_api_endpoint.py`

- Tests HTTP /recommend/ endpoint
- Verifies response structure
- Validates parameter ranges

#### `test_api_geometry.py`

- Tests geometry recommendations via HTTP API
- Validates different scenarios return different geometries
- Checks temperature compliance

#### `test_display_logic.py`

- Tests frontend field filtering (excluded fields removal)
- Verifies unit conversion (meters to millimeters)
- Validates display formatting

#### `test_recommend.py`

- End-to-end test of recommendation pipeline
- Tests input validation
- Verifies optimization execution
- Validates output structure

## Utility Scripts

### `check_db.py`

Inspect the SQLite database:

```bash
python tests/utilities/check_db.py
```

Output:

```
Database: D:\Akif\Fins\backend\db.sqlite3
Tables:
  ✓ auth_group (0 rows)
  ✓ auth_permission (59 rows)
  ✓ auth_user (1 rows)
  ...
```

### `set_admin_password.py`

Set or reset admin user password:

```bash
python tests/utilities/set_admin_password.py
```

Output:

```
✓ Password set successfully
  Username: admin
  Password: admin123
```

### `system_status.py`

Display comprehensive system status:

```bash
python tests/utilities/system_status.py
```

## Important Notes

### Django Setup

The `conftest.py` file automatically initializes Django before any tests run. This allows tests to:

- Import Django models and serializers
- Access the database
- Use Django utilities

### Running Tests Locally

1. Ensure Django development server is NOT running for unit tests
2. For integration tests that call HTTP endpoints, start the server first:
   ```bash
   python manage.py runserver 8001
   ```

### Expected Geometries

The optimizer can recommend:

- **Rectangular**: Simple, efficient for moderate cooling
- **Triangular**: Better fin efficiency, good for aggressive cooling
- **Trapezoidal**: Compromise between simplicity and performance

## Troubleshooting

### Import Errors

If you get import errors like "No module named 'fins_api'":

- Ensure you're running pytest from the project root: `pytest backend/tests/`
- Check that `conftest.py` is loading correctly

### Database Errors

If databases tests fail:

- Verify Django migrations: `python manage.py migrate`
- Check database exists: `ls backend/db.sqlite3`

### Connection Errors (Integration Tests)

If HTTP tests fail with connection errors:

- Start Django server: `python manage.py runserver 8001`
- Verify frontend server if testing UI: `npm run dev`

## Adding New Tests

1. Add test file to appropriate subdirectory (unit/ or integration/)
2. Follow naming convention: `test_*.py`
3. Use pytest conventions:
   ```python
   def test_something():
       """Test description"""
       assert condition, "Error message"
   ```
4. conftest.py will automatically initialize Django
