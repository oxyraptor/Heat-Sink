---
title: Heat-Sink Backend
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# Heat Sink Optimization System (Backend)

This is the backend service for the Heat Sink Optimization system, containerized and deployed via Hugging Face Spaces. It provides a REST API built with Django REST Framework (DRF) to serve AI-driven heat sink geometry optimization and Computational Fluid Dynamics (CFD) validation.

> **Note**: This repository only contains the backend code configured for Hugging Face Spaces deployment. The frontend (React + TypeScript) is designed to be hosted separately (e.g., on Vercel).

For an AI-maintainer oriented overview of the codebase, see [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).

## 🚀 Quick Start (Local Docker)

Since this repository is set up for Docker delivery to Hugging Face Spaces, utilizing Docker is the most robust way to run it locally:

```bash
docker build -t heat-sink-backend .
docker run -p 7860:7860 heat-sink-backend
```

The API will be available at `http://localhost:7860/api/`

## 📁 Project Structure

```
.
├── 📂 backend/                 # Django Backend Application
│   ├── core/                   # Business Logic (optimizer, materials, CFD loop)
│   ├── ml_models/              # Machine Learning Models (.pkl)
│   ├── fins_project/           # Django Configuration (settings, urls, etc.)
│   ├── fins_api/               # Django REST API App (views, serializers, models)
│   ├── manage.py               # Django CLI
│   ├── README_BACKEND.md       # Deeper backend-specific documentation
│   └── (testing scripts)       # e.g., verify_and_test_system.py, fins_cli.py
├── Dockerfile                  # Hugging Face Spaces Docker setup
├── requirements_django.txt     # Python dependencies
└── README.md                   # This documentation
```

## 🔌 API Endpoints

### Base URL: `https://<your-hf-space-url>/api`

_(Locally: `http://localhost:7860/api`)_

| Endpoint             | Method | Description                     |
| -------------------- | ------ | ------------------------------- |
| `/api/`              | GET    | API status                      |
| `/api/materials/`    | GET    | List available alloys           |
| `/api/recommend/`    | POST   | Heat sink optimization          |
| `/api/predict-ml/`   | POST   | ML-based prediction             |
| `/api/cfd-optimize/` | POST   | AI-CFD closed-loop optimization |

For required payloads and parameter constraints, reference `docs/API_REFERENCE_DETAILED.md` in the original repository.

## 🔁 AI-CFD Closed-Loop Design Workflow

The backend drives a closed-loop optimization process simulating heat sink physics:

1. **AI Generation**: Artificial intelligence creates initial geometries based on physical constraints.
2. **CFD Validation**: The geometry is processed through physics rules to validate flow uniformity, pressure drop, drag, and temperatures.
3. **Decision & Redesign**: If constraints are met, the design is accepted. If not, the engine modifies the geometry and reevaluates.

## 📦 Non-Docker Local Development

If you prefer to run the project via traditional Python development:

```bash
# 1. Install dependencies
pip install -r requirements_django.txt

# 2. Start the development server
cd backend
python start_django.py # Or: python manage.py runserver
```

## 🧪 Testing

The codebase includes verification scripts you can invoke to assert API health locally:

```bash
cd backend
python verify_and_test_system.py --quick
```

## 🚢 Deployment

By committing this repository with the `Dockerfile` and the Hugging Face Frontmatter (at the top of this README), Hugging Face Spaces will automatically build the container.

Inside the container, traffic is served by `gunicorn` listening on port `7860`:

```bash
gunicorn fins_project.wsgi:application --bind 0.0.0.0:7860 --workers 2
```
