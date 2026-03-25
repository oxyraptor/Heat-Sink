# Fins Project - Testing Guide

## Quick Links

- **[Start Here](./QUICKSTART.py)** - Overview and getting started
- **[Implementation Summary](../IMPLEMENTATION_SUMMARY.md)** - What was built
- **[API Reference](../docs/API_REFERENCE_DETAILED.md)** - Complete API documentation
- **[Materials Database](../docs/MATERIALS_DATABASE.md)** - All aluminum alloys

---

## Running Tests

### 1. Quick Health Check (⚡ Fastest)

```bash
python verify_and_test_system.py --quick
```

**Time:** ~10 seconds  
**Checks:**

- ✓ Database connectivity
- ✓ Server accessibility
- ✓ ML models loaded
- ✓ Dependencies installed

**Output Example:**

```
════════════════════════════════════════════════════════
            FINS PROJECT - HEALTH CHECK
════════════════════════════════════════════════════════

✓ PASS Database
✓ PASS Server
✓ PASS Dependencies
✓ PASS ML Models

Summary: 4/4 checks passed (100%)
```

---

### 2. API Endpoint Tests

```bash
python verify_api_backend.py
```

**Time:** 1-2 minutes  
**Tests:**

- ✓ Status endpoint (GET /api/)
- ✓ Materials endpoint (GET /api/materials/)
- ✓ Recommendation endpoint (POST /api/recommend/)
- ✓ ML prediction endpoint (POST /api/predict-ml/)
- ✓ CFD optimization endpoint (POST /api/cfd-optimize/)

**Validates:**

- Response status codes
- JSON schema correctness
- Required fields present
- Data type correctness

**Output Example:**

```
════════════════════════════════════════════════════════
        FINS PROJECT - API ENDPOINT TESTS
════════════════════════════════════════════════════════

✓ PASS Status Endpoint
✓ PASS Materials Endpoint
✓ PASS Recommendation Endpoint
✓ PASS ML Prediction Endpoint
✓ PASS CFD Optimization Endpoint

Overall Results: 5/5 tests passed (100%)
```

---

### 3. Full Test Suite (Complete)

```bash
python verify_and_test_system.py
```

**Time:** 5-10 minutes  
**Includes:**

- ✓ All health checks
- ✓ All API tests
- ✓ Django unit tests
- ✓ Integration workflow tests

**Output Example:**

```
════════════════════════════════════════════════════════
        FINS PROJECT - COMPREHENSIVE TEST SUITE
════════════════════════════════════════════════════════

=== PHASE 1: SYSTEM HEALTH CHECKS ===
✓ PASS Database
✓ PASS Server
✓ PASS Dependencies
✓ PASS ML Models

=== PHASE 2: API ENDPOINT TESTS ===
✓ PASS Status Endpoint
✓ PASS Materials Endpoint
✓ PASS Recommendation Endpoint
✓ PASS ML Prediction Endpoint
✓ PASS CFD Optimization Endpoint

=== PHASE 3: DJANGO UNIT TESTS ===
✓ PASS Django Unit Tests

=== PHASE 4: INTEGRATION TESTS ===
✓ PASS Workflow Integration

Overall Results: 14/14 tests passed (100%)
```

---

## Before Running Tests

### Start the Server

Open a terminal and run:

```bash
python start_django.py
```

You should see:

```
System startup complete. Press ENTER to start the server.
Starting development server at http://127.0.0.1:8001/
Quit the server with CONTROL-C.
```

### Run Tests in Another Terminal

Keep the server running, open a new terminal, and run the test commands above.

---

## Understanding Test Output

### Color Coding

- **🟢 Green (✓ PASS)** - Test passed successfully
- **🔴 Red (✗ FAIL)** - Test failed, check logs for details
- **🟡 Yellow (⚠ WARNING)** - Something unexpected but not fatal

### Timing Information

Each test shows how long it took:

```
✓ PASS Status Endpoint (0.125s)
```

Helps identify slow operations.

### Detailed Logs

Full details saved to:

- `logs/test_results.log` - All test results
- `logs/api.log` - API request/response details
- `logs/django.log` - Django operation logs

View in real-time:

```bash
tail -f logs/test_results.log
```

---

## Test Data Used

### Motor Specifications

```python
Motor:
  - Power: 5000W
  - Efficiency: 92%
  - RPM: 3000
  - Surface Area: 150 cm²
  - Ambient Temp: 25°C

Environment:
  - Max Junction Temp: 120°C
  - Air Velocity: 2.0 m/s
  - Humidity: 60%

Constraints:
  - Material: AL6063
  - Max Fin Height: 100mm
  - Max Base Thickness: 30mm
  - Max Fin Pitch: 15mm
```

### Expected Results

- **Recommendation:** 12-15 fins, 85-95°C junction temp
- **ML Prediction:** Similar to recommendation
- **CFD Optimization:** Refined geometry after iterations

---

## Troubleshooting Tests

### Test Won't Run

```bash
# Error: "Connection refused"
Solution: Start server first
$ python start_django.py

# Error: "ML Models not found"
Solution: Check ml_models/ directory
ls ml_models/
# Should show: thermal_model.pkl, inverse_model.pkl

# Error: "Port 8001 already in use"
Solution: Kill the process
$ lsof -i :8001
$ kill -9 <PID>
```

### Test Fails

1. **Check the log file:**

   ```bash
   tail -50 logs/test_results.log
   ```

2. **Look for error messages** starting with `✗ ERROR`

3. **Common issues:**
   - Database not migrated: `python manage.py migrate`
   - Dependencies missing: `pip install -r requirements_django.txt`
   - ML models not loaded: Check file sizes > 10MB
   - Server not responding: Check it's running

4. **Run health check to isolate issue:**
   ```bash
   python verify_and_test_system.py --quick
   ```

---

## Test Validation

Each test validates:

### Status Code

- Expected: 200 (success), 4xx (client error), 5xx (server error)
- Verified: Correct status code returned

### Response Format

- Expected: Valid JSON with required fields
- Verified: Schema matches specification

### Data Integrity

- Expected: Numeric fields are numbers, arrays are arrays, etc.
- Verified: All data types correct

### Performance

- Expected: API < 1 second, ML < 2 seconds, CFD < 15 minutes
- Verified: Timeout if exceeds limits

---

## Test Output Locations

### Console Output

- Real-time display while tests run
- Color-coded for quick reading

### Log Files

**Test Results:**

```bash
cat logs/test_results.log
```

**API Details:**

```bash
cat logs/api.log
```

**Django Operations:**

```bash
cat logs/django.log
```

**Clear old logs:**

```bash
rm logs/*.log
```

---

## Expected Test Times

| Test Type          | Typical Time | Range      |
| ------------------ | ------------ | ---------- |
| Quick Health Check | ~10 sec      | 5-15 sec   |
| API Tests          | ~90 sec      | 60-120 sec |
| Full Suite         | ~5-10 min    | 4-12 min   |

_Times vary based on system hardware and network conditions_

---

## Continuous Testing

### Run tests automatically

In CI/CD pipeline:

```bash
python verify_and_test_system.py  # Returns exit code 0 (pass) or 1 (fail)
```

Use in scripts:

```bash
if python verify_and_test_system.py --quick; then
    echo "All tests passed!"
else
    echo "Tests failed!"
    tail logs/test_results.log
    exit 1
fi
```

---

## What Gets Tested

### ✅ Tested Endpoints

1. **GET /** - System Status
   - Returns: status, version, services info
   - Validates: JSON format, required fields

2. **GET /materials/** - Material List
   - Returns: 6 aluminum alloys with properties
   - Validates: Field names, data types, material count

3. **POST /recommend/** - Heat Sink Recommendation
   - Input: Motor, environment, constraints
   - Returns: Recommended geometry and performance
   - Validates: All geometry fields, thermal values

4. **POST /predict-ml/** - ML Prediction
   - Input: Problem specifications
   - Returns: Predicted geometry
   - Validates: Prediction fields, confidence scores

5. **POST /cfd-optimize/** - CFD Optimization
   - Input: Problem with CFD parameters
   - Returns: Optimized geometry and metrics
   - Validates: Optimization progress, final results

### ✅ Tested Functionality

- Database connectivity
- ML model loading
- Request serialization
- Response deserialization
- Error handling
- Integration workflows

---

## Next Steps

1. **Verify System Works:**

   ```bash
   python verify_and_test_system.py --quick
   ```

2. **Review Results:**
   - Check console output
   - Review logs/test_results.log

3. **Run Full Suite:**

   ```bash
   python verify_and_test_system.py
   ```

4. **Check Documentation:**
   - [API Reference](../docs/API_REFERENCE_DETAILED.md)
   - [Materials Database](../docs/MATERIALS_DATABASE.md)

5. **Try the API:**
   ```bash
   curl http://127.0.0.1:8001/api/materials/
   ```

---

For more information, see:

- [Complete README](../README.md)
- [Implementation Summary](../IMPLEMENTATION_SUMMARY.md)
- [QUICKSTART Guide](./QUICKSTART.py)
- [Interactive Management CLI](./fins_cli.py)
