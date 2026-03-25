#!/usr/bin/env python
"""
FINS PROJECT - QUICK START GUIDE

This file provides quick instructions for using the new features.
Read this first!
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║          🌡️  FINS - Heat Sink Optimization System  🌡️                     ║
║                      Quick Start Guide v1.0                                ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 QUICKEST WAY TO GET STARTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Option 1: Interactive Menu (Easiest!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ python fins_cli.py

This launches a full interactive menu with options to:
✓ Start/stop servers
✓ Run tests  
✓ View documentation
✓ Manage database
✓ Check logs


Option 2: Manual Commands
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Start Server
$ python start_django.py
→ Server runs at http://127.0.0.1:8001/api

Step 2: Quick Health Check (in another terminal)
$ python verify_and_test_system.py --quick
→ Takes ~10 seconds, checks all systems

Step 3: Run All Tests
$ python verify_and_test_system.py
→ Takes 5-10 minutes, runs everything

Step 4: View Results
Check logs/test_results.log for detailed results


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Complete API Reference with examples:
→ docs/API_REFERENCE_DETAILED.md
  - All 5 endpoints documented
  - 50+ code examples (Python & cURL)
  - Request/response formats
  - Troubleshooting guide

Materials Database:
→ docs/MATERIALS_DATABASE.md
  - All 6 aluminum alloys listed
  - Thermal/mechanical properties
  - Selection guide by application
  - Cost comparison

Documentation Index:
→ ../docs/README.md
  - System design overview
  - Component interactions
  - Documentation map

Code Walkthrough:
→ docs/CODE_EXPLAINED.md
  - Module organization
  - Key functions explained
  - Data flow diagram


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧪 TESTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quick Health Check (10 seconds):
$ python verify_and_test_system.py --quick

Checks:
✓ Database connectivity
✓ Server running
✓ ML models loaded
✓ Dependencies installed


API Endpoint Tests (1-2 minutes):
$ python verify_api_backend.py

Tests all 5 endpoints:
✓ System status
✓ Materials list
✓ Recommendation endpoint
✓ ML prediction
✓ CFD optimization


Interactive Full Test CLI:
$ python interactive_full_test_cli.py

Interactive API Test CLI (custom payload/path):
$ python interactive_api_test_cli.py


Full Test Suite (5-10 minutes):
$ python verify_and_test_system.py

Includes:
✓ Health checks
✓ API tests
✓ Django unit tests
✓ Integration workflows
✓ Response validation


View Test Results:
$ tail -f logs/test_results.log


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 LOGGING & DEBUGGING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

All operations are logged with human-readable output:

API Request Logs:
$ tail -f logs/api.log

Sample output:
[14:22:15] ▶ Starting: GET /materials/
[14:22:15]  ✓ SUCCESS Retrieved 6 materials
[14:22:15] ✓ GET /materials/ completed (0.123s)


Django Operation Logs:
$ tail -f logs/django.log

Test Results:
$ tail -f logs/test_results.log


CLI Management Logs:
$ tail -f logs/cli.log


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 API QUICK REFERENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Base URL: http://127.0.0.1:8001/api

Endpoints:
  GET  /                    System status
  GET  /materials/          List materials
  POST /recommend/          Heat sink recommendation
  POST /predict-ml/         ML geometry prediction
  POST /cfd-optimize/       CFD optimization


Quick Test:
$ curl http://127.0.0.1:8001/api/
$ curl http://127.0.0.1:8001/api/materials/


Python Example:
import requests
response = requests.get('http://127.0.0.1:8001/api/materials/')
print(response.json())


Full examples: docs/API_REFERENCE_DETAILED.md


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Development Server:
$ python start_django.py
  - Runs on: http://127.0.0.1:8001/
  - Hot reload: Enabled
  - Debug mode: On

Production Server:
$ python start_production.py [host] [port] [workers]
  - Default: 0.0.0.0:8000 with 4 workers
  - Example: python start_production.py 0.0.0.0 8000 8


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆘 TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Port already in use:
$ lsof -i :8001
$ kill -9 <PID>

ML models not found:
→ Check backend/ml_models/ directory
→ Should have: thermal_model.pkl, inverse_model.pkl

Database error:
$ python manage.py migrate

Can't connect to API:
1. Ensure server is running: python start_django.py
2. Check http://127.0.0.1:8001/api/
3. View logs: tail -f logs/api.log

Test failures:
$ tail -f logs/test_results.log
→ Look for ✗ FAIL entries


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ NEW FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Interactive Management CLI (fins_cli.py)
  → One-click access to all tools and documentation

✓ Unified Test Suite (verify_and_test_system.py)
  → Health checks, API tests, integration tests in one script

✓ Human-Readable Logging (core/logger.py)
  → Color-coded output, timestamps, performance metrics

✓ Complete API Documentation
  → 50+ examples, all parameters explained

✓ Materials Database Guide
  → All 6 alloys compared, selection tips

✓ Interactive CLI Menu
  → 19 menu options for everything you need


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 FILES OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core System:
✓ start_django.py            Development server
✓ start_production.py        Production server (Gunicorn)
✓ manage.py                  Django CLI

New Tools:
✓ fins_cli.py               Interactive management (START HERE)
✓ verify_and_test_system.py Unified testing suite
✓ core/logger.py            Logging utility

Documentation:
✓ README.md                             Quick overview
✓ docs/README.md                        Documentation index
✓ docs/API_REFERENCE_DETAILED.md       Complete API docs
✓ docs/MATERIALS_DATABASE.md           Material specs
✓ docs/CODE_EXPLAINED.md               Code walkthrough
✓ docs/AI_CFD_OPTIMIZATION_AGENT.md    CFD workflow spec

Logs:
✓ logs/api.log              API request logs
✓ logs/django.log           Django operation logs
✓ logs/test_results.log     Test execution results
✓ logs/cli.log              CLI management logs


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 RECOMMENDED WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. First Time Setup:
   $ python verify_and_test_system.py --quick
   → Verify everything works

2. Daily Development:
   $ python fins_cli.py
   → Use interactive menu for everything

3. Before Deployment:
   $ python verify_and_test_system.py
   → Run full test suite

4. Debugging Issues:
   $ tail -f logs/test_results.log
   $ tail -f logs/api.log
   → View detailed logs


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Questions? Check docs/API_REFERENCE_DETAILED.md or run: python fins_cli.py

Status: ✅ Ready for production use
Version: 1.0.0
Date: 2026-03-25

""")
