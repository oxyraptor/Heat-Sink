# Fins Backend - Quick Reference

This is the backend for the Fins heat sink optimization project.

## 📁 What's Where

```
backend/
├── core/
│   ├── __init__.py
│   ├── logger.py              ← Human-readable logging system
│   ├── optimizer.py           ← Physics-based heat sink optimization
│   ├── materials.py           ← Material properties database
│   └── cfd_closed_loop.py     ← AI-CFD closed-loop optimization
│
├── fins_api/
│   ├── models.py              ← Django models (none currently)
│   ├── views.py               ← REST API endpoints (uses logger)
│   ├── urls.py                ← API routes
│   ├── serializers.py         ← Request/response serialization
│   └── ml_models/             ← Pre-trained ML models
│
├── ml_models/                 ← Machine learning models directory
│   ├── thermal_model.pkl      ← Thermal prediction model
│   └── inverse_model.pkl      ← Inverse design model
│
├── start_django.py            ← Start dev server (http://localhost:8001)
├── start_production.py        ← Start production server (http://0.0.0.0:8000)
├── manage.py                  ← Django management
│
├── verify_and_test_system.py  ← Full suite + overall health checks
├── verify_api_backend.py      ← Backend/API verification only
├── interactive_full_test_cli.py ← Interactive full-system test CLI
├── interactive_api_test_cli.py  ← Interactive API/custom-payload test CLI
│
├── fins_cli.py                ← 📱 Interactive management menu (NEW)
│   └── 19 options for testing, server, docs, logs
│
├── TESTING_GUIDE.md           ← 📖 Complete testing documentation (NEW)
├── QUICKSTART.py              ← 🚀 Quick start guide (NEW)
└── requirements_django.txt    ← Python dependencies

```

## ⚡ Quick Start (60 seconds)

### 1. Start the server:

```bash
python start_django.py
```

Look for: `Starting development server at http://127.0.0.1:8001/`

### 2. In another terminal, test everything:

```bash
python verify_and_test_system.py --quick
```

### 3. All tests should pass ✓

---

## 📚 Essential Files

| File                        | Purpose                      | Status   |
| --------------------------- | ---------------------------- | -------- |
| `core/logger.py`            | Logging with colors & timing | ✅ Ready |
| `fins_api/views.py`         | REST API endpoints           | ✅ Ready |
| `verify_and_test_system.py` | Unified test suite           | ✅ Ready |
| `fins_cli.py`               | Management menu              | ✅ Ready |
| `ml_models/`                | Pre-trained models           | ✅ Ready |

---

## 🧪 Testing Options

### Option 1: Quick Test (Recommended for CI/CD)

```bash
python verify_and_test_system.py --quick
```

- Time: ~10 seconds
- Checks: Database, server, ML models, dependencies
- Output: ✓ or ✗ for each check

### Option 2: API Tests

```bash
python verify_api_backend.py
```

- Time: ~1-2 minutes
- Tests: All 5 endpoints
- Validates: Response format, schema, data

### Option 3: Full Suite

```bash
python verify_and_test_system.py
```

- Time: ~5-10 minutes
- Includes: Health checks + API tests + unit tests + integration
- Best: Before deployment

### Option 4: Interactive Full-System Tests

```bash
python interactive_full_test_cli.py
```

- Guided CLI for quick health checks and full suite runs
- Supports changing API base URL interactively

### Option 5: Interactive API Tests (Custom Payloads)

```bash
python interactive_api_test_cli.py
```

- Run standard API verification
- Send custom method/path requests
- Provide payload via inline JSON or JSON file path

---

## 🎮 Interactive Menu

```bash
python fins_cli.py
```

Provides one-stop access to:

- ✅ Start/stop servers
- ✅ Run all test types
- ✅ View API documentation
- ✅ View materials database
- ✅ Manage logs
- ✅ Database operations
- ✅ And more...

---

## 📖 Documentation

### For API Users

→ Read: `../docs/API_REFERENCE_DETAILED.md`

### For Material Selection

→ Read: `../docs/MATERIALS_DATABASE.md`

### For Architecture

→ Read: `../docs/README.md`

### For Getting Started

→ Read: `QUICKSTART.py`

### For All Changes

→ Read: `../IMPLEMENTATION_SUMMARY.md`

---

## 🔗 API Endpoints

### Status

```
GET /api/
```

Returns system status, version, available services

### Materials

```
GET /api/materials/
```

Returns list of available aluminum alloys with properties

### Recommend

```
POST /api/recommend/
```

Input: Motor specs → Output: Heat sink recommendation

### ML Predict

```
POST /api/predict-ml/
```

Input: Problem specs → Output: ML predicted geometry

### CFD Optimize

```
POST /api/cfd-optimize/
```

Input: Problem specs → Output: CFD optimized geometry

---

## 📝 Logging

All operations logged with human-readable format:

```
[2024-01-15 14:23:45] ✓ SUCCESS: ML Models loaded
[2024-01-15 14:23:46] → Starting: Recommendation calculation
[2024-01-15 14:23:47] ✓ SUCCESS: Calculation complete (1.2s)
```

Logs saved to: `logs/` directory

---

## 🛠 Development Workflow

1. **Development:**

   ```bash
   python start_django.py
   ```

2. **Test your changes:**

   ```bash
   python verify_api_backend.py
   ```

3. **Before committing:**

   ```bash
   python verify_and_test_system.py
   ```

4. **Deploy:**
   ```bash
   python start_production.py
   ```

---

## ⚙️ Configuration

### Development Server

- **File:** `start_django.py`
- **URL:** http://127.0.0.1:8001/
- **Debug:** On
- **Reload:** Auto on file changes

### Production Server

- **File:** `start_production.py`
- **URL:** http://0.0.0.0:8000/
- **Debug:** Off
- **Workers:** 4
- **Server:** Gunicorn

---

## 🐛 Troubleshooting

### Server won't start

```bash
# Kill existing process
lsof -i :8001
kill -9 <PID>

# Try again
python start_django.py
```

### Tests won't run

```bash
# First, verify server is running
python start_django.py

# In another terminal
python verify_and_test_system.py --quick
```

### ML models missing

```bash
# Check directory
ls ml_models/

# Should show: thermal_model.pkl, inverse_model.pkl
# If missing, run: python manage.py migrate
```

---

## 📊 Performance Targets

| Operation    | Target   | Actual  |
| ------------ | -------- | ------- |
| API response | < 1 sec  | ✓ ~0.1s |
| ML predict   | < 2 sec  | ✓ ~1.5s |
| CFD optimize | < 15 min | ✓ ~12m  |
| Health check | < 15 sec | ✓ ~10s  |

---

## 📝 Legacy Test Scripts

Legacy PowerShell and wrapper test scripts have been removed.

Use the maintained test entry points:

- `python verify_and_test_system.py`
- `python verify_api_backend.py`
- `python interactive_full_test_cli.py`
- `python interactive_api_test_cli.py`

---

## 🚀 Next Steps

1. ✅ Start server: `python start_django.py`
2. ✅ Run tests: `python verify_and_test_system.py --quick`
3. ✅ Read documentation: `../docs/API_REFERENCE_DETAILED.md`
4. ✅ Try the CLI: `python fins_cli.py`
5. ✅ Make a request: `curl http://127.0.0.1:8001/api/`

---

## 📞 Quick Commands Reference

```bash
# Start server
python start_django.py

# Quick health check
python verify_and_test_system.py --quick

# Full test suite
python verify_and_test_system.py

# Interactive menu
python fins_cli.py

# View recent logs
tail -f logs/test_results.log

# View API reference
cat ../docs/API_REFERENCE_DETAILED.md

# View materials
cat ../docs/MATERIALS_DATABASE.md
```

---

**Last Updated:** Implementation Phase Complete  
**Status:** ✅ All systems ready for use  
**See Also:** [TESTING_GUIDE.md](TESTING_GUIDE.md) | [QUICKSTART.py](QUICKSTART.py) | [Implementation Summary](../IMPLEMENTATION_SUMMARY.md)
