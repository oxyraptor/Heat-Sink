# Bug Report and Fix Plan

This file explains the issues found during test runs, why they are bugs, and the most direct way to fix each one.

## 1. Django tests fail because `huggingface_hub` is missing

### What happened

Running `python manage.py test fins_api.tests -v 2` started Django, built the test database, and then failed while importing `backend/fins_api/views.py`. The import `from huggingface_hub import hf_hub_download` raised `ModuleNotFoundError`.

### Why this is a bug

The backend cannot load its URL configuration if one of its view dependencies is missing. That means even basic API tests cannot start. This is not just a test issue; it is a runtime dependency problem that blocks the application from booting in the current environment.

### How to fix it

Install the missing package into the active Python environment and make sure it is listed in the backend dependency file so it is available in future setups.

Recommended actions:

1. Add `huggingface_hub` to `requirements_django.txt` if it is meant to be a required backend dependency.
2. Reinstall backend dependencies in `.venv`.
3. Rerun the Django tests to confirm the import succeeds.

If the import is optional, the safer code fix would be to guard it with a fallback path so the app can still start when the package is absent.

## 2. API verification scripts fail because `requests` is missing

### What happened

Both `python verify_api_backend.py` and `python verify_and_test_system.py --quick` failed immediately with `ModuleNotFoundError: No module named 'requests'`.

### Why this is a bug

These scripts are part of the repository’s verification workflow, so they should run in the documented environment. A missing dependency here prevents health checks and endpoint tests from running at all.

### How to fix it

Install `requests` in the active backend environment and make sure it is declared in the backend requirements file.

Recommended actions:

1. Add `requests` to `requirements_django.txt` if it is intended to be required.
2. Reinstall dependencies in the virtual environment.
3. Run `python verify_api_backend.py` again to confirm the scripts start.

## 3. Frontend lint fails because ESLint version and config are incompatible

### What happened

`npm run lint` failed with `ERR_PACKAGE_PATH_NOT_EXPORTED` from `ui/eslint.config.js`, specifically when it tried to import `eslint/config` while the installed ESLint version is `8.57.1`.

### Why this is a bug

The lint command is part of the frontend’s standard verification flow. If it crashes before analyzing any source files, the lint setup is broken. This is usually a configuration and dependency mismatch rather than a code issue in the React app itself.

### How to fix it

Align the ESLint config with the installed ESLint major version, or upgrade ESLint to a version that supports the config import being used.

Recommended actions:

1. Inspect `ui/eslint.config.js` and remove any imports that are not supported by ESLint 8.
2. If the config was written for ESLint 9 flat config, upgrade the frontend ESLint package set consistently.
3. Rerun `npm run lint` after the version/config alignment.

## 4. One backend unit test passed, which helps narrow the issue

### What happened

The frontend type check passed, and the test selection for the Django backend showed that the environment can start far enough to build a test database before failing on imports.

### Why this matters

This suggests the project is not broadly broken. The failures are concentrated in dependency and configuration loading, which makes the fix scope clearer.

### How to proceed

After fixing the missing Python packages and the ESLint version mismatch, rerun the same commands:

1. `python manage.py test fins_api.tests -v 2`
2. `python verify_api_backend.py`
3. `python verify_and_test_system.py --quick`
4. `npm run lint`

If those pass, you can then run the full backend test suite and the frontend production build for a stronger verification pass.

## Summary

The main bugs are not business-logic defects in the heat sink algorithms. They are environment and tooling issues that block the app from being tested or started reliably:

- Missing Python dependency: `huggingface_hub`
- Missing Python dependency: `requests`
- Frontend lint toolchain mismatch: ESLint config vs installed version

Fixing those three issues should restore the normal verification path.
