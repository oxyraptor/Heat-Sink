# Project Structure

## Overview

Current top-level layout:

```text
Fins/
|- backend/      # Django backend, APIs, test runners, CLI tools
|- docs/         # Documentation index and technical references
|- ui/           # React + TypeScript frontend
|- scripts/      # Utility scripts
|- setup.py      # Initial setup helper
|- README.md     # Main project guide
`- IMPLEMENTATION_SUMMARY.md
```

## Backend

```text
backend/
|- core/                         # Optimization, materials, logging, CFD loop
|- fins_api/                     # Django REST API app
|- fins_project/                 # Django project settings and routing
|- ml_models/                    # Trained model artifacts
|- tests/                        # Python tests
|- manage.py
|- start_django.py
|- start_production.py
|- requirements_django.txt
|- fins_cli.py                   # Interactive management console
|- verify_and_test_system.py     # Full suite + health checks
|- verify_api_backend.py         # API/backend verification only
|- interactive_full_test_cli.py  # Interactive full-system test runner
`- interactive_api_test_cli.py   # Interactive API/custom payload test runner
```

## Documentation

```text
docs/
|- README.md                     # Documentation index (entry point)
|- API_REFERENCE_DETAILED.md
|- MATERIALS_DATABASE.md
|- AI_CFD_OPTIMIZATION_AGENT.md
|- CODE_EXPLAINED.md
|- ML_ALGORITHMS.md
|- README_DJANGO.md
`- PDF/
```

## Frontend

```text
ui/
|- src/
|- public/
|- package.json
|- vite.config.ts
|- tailwind.config.ts
`- tsconfig.json
```

## Test Entry Points

Use these four scripts as the maintained testing surface:

1. `python backend/verify_and_test_system.py`
2. `python backend/verify_api_backend.py`
3. `python backend/interactive_full_test_cli.py`
4. `python backend/interactive_api_test_cli.py`

## Recommended Run Flow

1. Start backend: `python backend/start_django.py`
2. Quick validation: `python backend/verify_and_test_system.py --quick`
3. API-only validation: `python backend/verify_api_backend.py`
4. Full verification before push: `python backend/verify_and_test_system.py`

## Notes

- Legacy PowerShell and wrapper test scripts were removed to avoid duplicate paths.
- `docs/README.md` is the single documentation navigation entry point.

---

Last updated: March 25, 2026
