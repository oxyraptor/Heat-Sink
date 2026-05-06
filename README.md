---
title: Heat-Sink Backend
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
app_file: app.py
pinned: false
---

# Heat Sink Optimization System

**Languages:** Python (69%), TypeScript (28%), CSS (1.8%), Other (0.7%)  
**Backend:** Django REST Framework, ML models (.pkl), Docker  
**Frontend:** TypeScript (React), CSS  
**Deployment:** Hugging Face Spaces (Backend), Vercel/Other (Frontend)

---

## 🚩 Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Quick Start (Docker)](#quick-start-docker)
- [Non-Docker Development](#non-docker-local-development)
- [API Endpoints](#api-endpoints)
- [AI-CFD Optimization Workflow](#ai-cfd-closed-loop-design-workflow)
- [Testing](#testing)
- [Frontend (UI)](#frontend-ui)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [References & Further Reading](#references--further-reading)

---

## Project Overview

This repository contains the **backend** for the Heat Sink Optimization system: an AI/ML-powered platform that automates the design of heat sinks for electronics and thermal management. The service is engineered to support an iterative, closed-loop workflow using machine learning and physics-based (CFD) simulation.  
**Frontend code (TypeScript/React)** is hosted separately, e.g., on Vercel. See the [`ui/README.md`](ui/README.md).

> **Note:** This backend is configured for portable containerized deployment via Docker and Hugging Face Spaces.

---

## Architecture

- **Backend (Python/Django/DRF)**: Serves the REST API, runs optimization pipeline using ML models, orchestrates simulation, exposes endpoints for heat sink recommendation, materials, and AI-CFD workflows.
- **Frontend (React/TS)**: Provides interactive dashboard and configuration panel (see [`ui/`](ui/)), consumes backend API.
- **Shared Data Flow**: 
    ```
    User → Frontend (TypeScript) → API (Django) → AI/ML Model & CFD Engine → Results → Frontend
    ```
- **ML Models**: `.pkl` files residing in `backend/ml_models/` performing inference for prediction endpoints.
- **Docker**: All backend components are dockerized for local/Hugging Face deployment.

---

## Quick Start (Docker)
1. **Clone the repo**
    ```bash
    git clone https://github.com/oxyraptor/Heat-Sink.git
    cd Heat-Sink
    ```
2. **Build and run (Docker)**
    ```bash
    docker build -t heat-sink-backend .
    docker run -p 7860:7860 heat-sink-backend
    ```
3. **Access the API**
    - Base: [http://localhost:7860/api/](http://localhost:7860/api/)

---

## Non-Docker Local Development

1. **Install dependencies**
    ```bash
    pip install -r requirements_django.txt
    ```
2. **Start the dev server**
    ```bash
    cd backend
    python start_django.py
    # OR
    python manage.py runserver
    ```

---

## API Endpoints

Base: `/api/` (e.g., `http://localhost:7860/api/`, or `/api/` on HF Spaces)

| Endpoint             | Method | Description                     | Example Payload                      |
|----------------------|--------|---------------------------------|--------------------------------------|
| `/api/`              | GET    | API status/health               | N/A                                  |
| `/api/materials/`    | GET    | List available alloys           | N/A                                  |
| `/api/recommend/`    | POST   | Heat sink optimization          | See below                            |
| `/api/predict-ml/`   | POST   | ML-based prediction             | See below                            |
| `/api/cfd-optimize/` | POST   | AI-CFD closed-loop optimization | See below                            |

### Example: Recommend Endpoint

**POST** `/api/recommend/`

```json
{
  "ambient_temperature": 60,
  "max_temp": 120,
  "power": 15.0,
  "material": "AL6061",
  "geometry_type": "rectangular"
}
```
**Returns**
```json
{
  "geometry": { "fin_height": 16.0, "fin_count": 32, ... },
  "material": "AL6061",
  "predicted_temp": 110.5,
  "valid": true
}
```
*See [`docs/API_REFERENCE_DETAILED.md`](docs/API_REFERENCE_DETAILED.md) for full payloads and description.*

---

## AI-CFD Closed-Loop Design Workflow

The backend powers an iterative, AI-driven engineering loop:

1. **AI Generation**: Generates initial heat sink design geometry
2. **CFD Validation**: Runs computational fluid dynamics (CFD) simulation for validation (flow, drag, temperature, pressure drop)
3. **Decision & Redesign**: If constraints fail, auto-redesigns and re-simulates until optimal

*This process supports generative engineering, autonomous CAD, and surrogate-based analysis.*

---

## Testing

See [`backend/tests/README.md`](backend/tests/README.md) for:
- Unit test suite for ML models, geometry, closed-loop logic
- Integration tests for all API endpoints
- Useful test scripts for DB inspection, admin reset, server health

**How to run:**
```bash
pip install pytest pytest-django
pytest backend/tests/
```
*Run individual test files or suite as described in the tests/README.md.*

---

## Frontend (UI)

See [`ui/README.md`](ui/README.md) for:
- Unified optimization panel, CFD optimizer, iteration rendering
- Local dev: `npm install && npm run dev`
- Runs at [http://localhost:5173/](http://localhost:5173/)
- Tabs: Optimizer, CFD Optimization, Unified Optimizer (configuration + results)

---

## Project Structure

```
.
├── backend/                 # Django Backend (AI, API, ML, CFD)
│   ├── core/                # Business Logic
│   ├── ml_models/           # ML .pkl files
│   ├── fins_project/        # Django Config
│   ├── fins_api/            # DRF App
│   ├── manage.py            # CLI
│   └── tests/               # Unit & Integration Tests
├── ui/                      # Frontend (see README.md)
├── Dockerfile               # For Hugging Face Spaces/Docker deployment
├── requirements_django.txt  # Backend Python deps
└── README.md                # This file
```

---

## Deployment

If pushed as-is to Hugging Face Spaces, the backend image will be built and exposed as a service at port 7860.
- Serve via Gunicorn:
    ```bash
    gunicorn fins_project.wsgi:application --bind 0.0.0.0:7860 --workers 2
    ```

---

## Contributing

1. Open issues or discussion threads for bugs, feature requests, and feedback!
2. Fork, branch, and submit a pull request describing your improvement.
3. Please see [CONTRIBUTING.md](CONTRIBUTING.md) if available – style, lint, and test before submitting PRs.

---

## License

Distributed under the MIT License (or specify as appropriate).

---

## References & Further Reading

- [Project Context and Maintainer Info](PROJECT_CONTEXT.md)
- [Detailed API Spec](docs/API_REFERENCE_DETAILED.md)
- Hugging Face Spaces: [https://huggingface.co/spaces](https://huggingface.co/spaces)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PyTorch](https://pytorch.org/) or [scikit-learn](https://scikit-learn.org/) (for ML model)
