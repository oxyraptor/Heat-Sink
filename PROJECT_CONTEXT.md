# Heat-Sink Project Context for Future Changes

This repository contains two coordinated parts:

- `backend/` is a Django REST service for heat-sink design and validation.
- `ui/` is a Vite + React frontend for the user-facing optimization studio.

Treat the backend as a stateless computational API. Treat the UI as a thin orchestration layer that collects parameters, calls the backend, and renders the results.

## What This Project Does

The backend accepts motor, environment, and constraint inputs, then returns one of three kinds of outputs:

1. A physics-based heat-sink recommendation.
2. An ML-based geometry prediction.
3. A CFD-style closed-loop optimization result.

The system is optimized for thermal design, not for general CRUD or database workflows.

The frontend presents that workflow as a design studio with a unified optimization tab, a heat-sink recommendation tab, and a CFD optimization tab.

## Runtime Entry Points

- `backend/manage.py` starts Django.
- `backend/fins_project/urls.py` mounts the API at both `/api/` and `/`.
- `backend/fins_api/urls.py` defines the public endpoints.
- `backend/start_django.py` runs the development server on port `8001`.
- `backend/start_production.py` runs Gunicorn on port `8000` by default.
- `backend/verify_api_backend.py` and `backend/verify_and_test_system.py` are the primary verification scripts.
- `ui/index.html` boots the frontend app.
- `ui/src/main.tsx` mounts React into `#root`.
- `ui/src/App.tsx` owns the tab layout and backend selection logic.
- `ui/src/components/UnifiedOptimization.tsx` and `ui/src/components/CFDOptimization.tsx` are the major feature components.

### Environment & Compatibility Note

- **Python Version**: Targets Python 3.12+ (currently using 3.14.2 in development).
- **Core Dependencies**: Requires `Django 4.2.x`, `drf`, `numpy`, `scipy`, `pandas`, `scikit-learn`, and `joblib`.
- **Windows Terminal Support**: The custom logger is sensitive to Unicode characters (✓, ⚠, ✗) in non-UTF-8 Windows consoles; these are restricted to plain ASCII in the backend core to prevent `UnicodeEncodeError`.

## Core Control Flow

Typical request flow:

`HTTP request -> URL routing -> DRF view or ViewSet -> serializer validation -> core business logic -> JSON response`

Typical frontend flow:

`User input -> React form state -> backend POST request -> JSON response -> result cards / iteration views`

The main business logic lives here:

- `backend/fins_api/views.py` orchestrates the request handling.
- `backend/core/optimizer.py` performs the thermal and geometry optimization.
- `backend/core/cfd_closed_loop.py` performs the iterative surrogate or external CFD loop.
- `backend/core/materials.py` stores the alloy database.

The frontend follows a similar ownership split:

- `ui/src/App.tsx` coordinates tabs, backend URL selection, and top-level layout.
- `ui/src/components/UnifiedOptimization.tsx` runs the combined CFD + recommend workflow.
- `ui/src/components/CFDOptimization.tsx` runs the CFD-only optimization flow.
- `ui/src/components/ui/*` provides the shared component primitives used by the app.

## API Surface

Public endpoints:

- `GET /` and `GET /api/` return service status.
- `GET /materials/` and `GET /api/materials/` return available alloys.
- `POST /recommend/` and `POST /api/recommend/` return a physics-based design.
- `POST /predict-ml/` and `POST /api/predict-ml/` return ML-predicted geometry.
- `POST /cfd-optimize/` and `POST /api/cfd-optimize/` run the closed-loop CFD workflow.

The serializers that define the request/response contract are in `backend/fins_api/serializers.py`.

The UI currently depends most directly on:

- `POST /recommend/` for the recommendation tab and the unified workflow.
- `POST /cfd-optimize/` for CFD optimization.
- `GET /materials/` if material selection is surfaced or expanded later.

## Domain Model

The project is built around three geometry families in `backend/core/optimizer.py`:

- Rectangular fins.
- Triangular fins.
- Trapezoidal fins.

The thermal model computes equilibrium from convection, radiation, fin efficiency, and base conduction. The optimizer searches candidate geometries with differential evolution and then rounds fin count to an integer before final evaluation.

## Important Invariants

These behaviors should be preserved unless the change is explicitly about changing the physics:

- The maximum motor temperature is a hard constraint in the recommendation flow.
- Fin count `N` is rounded to an integer before final evaluation.
- The default alloy is `6063-T5` when the user does not choose one.
- ML models may be missing at startup; the API must fail gracefully with a 503 for ML routes.
- CFD surrogate behavior is deterministic unless an external command template is supplied.
- The API is intended to stay stateless; do not introduce database coupling unless required.

## Configuration And Deployment

Key settings live in `backend/fins_project/settings.py`:

- `DEBUG` defaults from the environment and is `True` if unset.
- `SECRET_KEY` must be overridden in production.
- `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` are environment-driven.
- WhiteNoise is enabled for static file serving.
- SQLite exists mainly to satisfy Django requirements, not as a primary application store.

Deployment assumptions:

- Docker is the main deployment path.
- Hugging Face Spaces is the documented target environment.
- Gunicorn listens on port `7860` in the containerized deployment described by the root README.
- The UI runs locally with Vite on port `5173`.
- The UI can target multiple backend base URLs and falls back across them when one is unavailable.

Frontend configuration:

- `VITE_API_BASE_URL` can override the API base URL used by the UI.
- If that variable is not set, the app tries `http://localhost:8001`, `http://127.0.0.1:8001`, then `http://localhost:8000`.
- The UI uses Tailwind CSS tokens, Radix primitives, and Framer Motion for motion.

## Testing And Verification

Primary validation tools:

- `backend/fins_api/tests.py` contains the basic Django test case coverage.
- `backend/verify_api_backend.py` checks the API endpoints.
- `backend/verify_and_test_system.py` performs broader health and system checks.
- `ui` should be validated with `npm run type-check`, `npm run lint`, and `npm run build` from the `ui/` directory.

Prefer the narrowest verification that matches the change:

- API/view/serializer changes -> run the API verification script.
- Optimizer or CFD changes -> run the broader system check.
- Payload or schema changes -> compare against `fins_api/serializers.py` and `fins_api/tests.py` first.
- UI layout, state, or API integration changes -> run the frontend type-check and build first, then verify the affected backend endpoint.

## Files That Control Behavior Most Directly

- `backend/fins_api/views.py`
- `backend/fins_api/serializers.py`
- `backend/core/optimizer.py`
- `backend/core/cfd_closed_loop.py`
- `backend/core/materials.py`
- `backend/fins_project/settings.py`
- `ui/src/App.tsx`
- `ui/src/components/UnifiedOptimization.tsx`
- `ui/src/components/CFDOptimization.tsx`
- `ui/src/index.css`
- `ui/tailwind.config.ts`

If you need to understand the system quickly, read those files first.

## Safe Change Checklist For Future AI Edits

Before editing:

1. Identify the endpoint or solver path the change touches.
2. Read the nearest serializer, view, and core implementation.
3. Confirm whether the change affects temperature constraints, integer rounding, or ML model availability.
4. Keep request and response shapes consistent with existing serializers and tests.
5. For UI changes, read the tab component, the target feature component, and the shared styling tokens before editing.

After editing:

1. Run the smallest relevant verification.
2. Check for regressions in status, materials, recommend, ML prediction, and CFD optimize flows if the edit is shared logic.
3. Do not broaden the change into unrelated optimization or deployment code unless necessary.
4. For UI changes, run the frontend type-check and build, then verify the affected API flow end-to-end.

## Known Gaps

The repository does not document:

- How the ML models were trained.
- The external CFD command template expected by the closed-loop path.
- Formal performance budgets for optimization runtime.
- A structured error taxonomy for client-side handling.
- A backend-serving strategy for the UI in production versus static hosting.
- Design-system documentation for the frontend component primitives.

### Operational Notes

- **Scientific Stack**: The installation of `scipy` and `pandas` on Windows can take significant time; always verify the `.venv` state before running scripts.
- **Port Conflict**: The backend defaults to `8001` via `start_django.py` to avoid conflicts with other common services often on `8000`.
- **Statelessness**: No authentication or user accounts are currently implemented; parameters are passed strictly via JSON POST requests.

## Short Rule For Future Agents

This codebase is safest to change by staying local: view the serializer, the view, and the owning core module for the exact path you plan to modify, and for frontend work read the relevant tab component plus the shared UI primitives before editing. Avoid altering solver behavior unless the request explicitly calls for it.
