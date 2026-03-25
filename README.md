# Heat Sink Optimization System

A complete heat sink optimization system with Django REST Framework backend and React TypeScript frontend.

## 🚀 Quick Start

### Backend (Django)

**Development Mode** (with hot reload):

```bash
python start_django.py
```

Server runs at: `http://127.0.0.1:8001/`

**Production Mode** (using Gunicorn):

```bash

pip install gunicorn
python start_production.py
```

Server runs at: `http://0.0.0.0:8000/`

> **Note**: The development server warning is normal - use `start_django.py` for development and `start_production.py` for production deployment.

### Frontend (React + TypeScript)

```bash
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173/`

## 📚 Documentation Hub

Use these links to jump directly to the exact documentation you need:

- **Documentation Index (Recommended Start)**: [docs/README.md](docs/README.md)
- **Quick Start Guide**: [backend/QUICKSTART.py](backend/QUICKSTART.py)
- **Backend Overview**: [backend/README_BACKEND.md](backend/README_BACKEND.md)
- **Testing Guide**: [backend/TESTING_GUIDE.md](backend/TESTING_GUIDE.md)
- **Detailed API Reference**: [docs/API_REFERENCE_DETAILED.md](docs/API_REFERENCE_DETAILED.md)
- **Materials Database**: [docs/MATERIALS_DATABASE.md](docs/MATERIALS_DATABASE.md)
- **AI-CFD Optimization Spec**: [docs/AI_CFD_OPTIMIZATION_AGENT.md](docs/AI_CFD_OPTIMIZATION_AGENT.md)
- **Implementation Summary**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

## 📁 Project Structure

```
Fins/
├── 📂 backend/                 # Django Backend
│   ├── core/                   # Business Logic
│   │   ├── optimizer.py        # Heat sink optimization algorithms
│   │   ├── materials.py        # Material properties database
│   │   ├── cfd_closed_loop.py  # AI-CFD closed-loop optimization agent
│   │   ├── logger.py           # Human-readable logging utility
│   │   └── __init__.py
│   │
│   ├── ml_models/              # Machine Learning Models
│   │   ├── thermal_model.pkl   # Forward thermal model
│   │   └── inverse_model.pkl   # Inverse optimization model
│   │
│   ├── fins_project/           # Django Project Configuration
│   │   ├── settings.py         # Django settings
│   │   ├── urls.py             # Main URL routing
│   │   ├── wsgi.py             # WSGI config
│   │   └── asgi.py             # ASGI config
│   │
│   ├── fins_api/               # Django REST API App
│   │   ├── views.py            # API ViewSets and views
│   │   ├── serializers.py      # DRF serializers
│   │   ├── urls.py             # API URL routing
│   │   ├── tests.py            # Test cases
│   │   └── models.py           # Database models
│   │
│   ├── manage.py               # Django CLI
│   ├── start_django.py         # Development server launcher
│   ├── start_production.py     # Production server launcher
│   ├── verify_and_test_system.py # Unified health checks + API/integration tests
│   ├── verify_api_backend.py   # Backend/API verification tests only
│   ├── interactive_full_test_cli.py # Interactive full-system test CLI
│   ├── interactive_api_test_cli.py # Interactive API/custom payload test CLI
│   ├── fins_cli.py             # Interactive management CLI (menu driven)
│   ├── TESTING_GUIDE.md        # Backend test execution and troubleshooting guide
│   ├── README_BACKEND.md       # Backend-specific quick reference
│   ├── QUICKSTART.py           # Fast startup and command reference
│   ├── requirements_django.txt # Python dependencies
│   └── db.sqlite3              # SQLite database
│
├── 📂 ui/                      # React + TypeScript Frontend
│   ├── src/
│   │   ├── App.tsx             # Main application component
│   │   ├── main.tsx            # Entry point
│   │   ├── components/         # UI components (shadcn-ui)
│   │   │   └── ui/             # Reusable UI components
│   │   └── lib/                # Utilities
│   │       └── utils.ts        # Helper functions
│   │
│   ├── public/                 # Static assets
│   ├── package.json            # NPM dependencies
│   ├── vite.config.ts          # Vite configuration
│   ├── tailwind.config.ts      # Tailwind CSS config
│   ├── tsconfig.json           # TypeScript config
│   └── index.html              # HTML entry point
│
├── 📂 docs/                    # Documentation
│   ├── API_REFERENCE_DETAILED.md # Full endpoint docs with payloads and examples
│   ├── MATERIALS_DATABASE.md   # Detailed alloy/material reference
│   ├── CODE_EXPLAINED.md       # Code explanation
│   ├── ML_ALGORITHMS.md        # ML algorithms documentation
│   ├── README_DJANGO.md        # Django-specific docs
│   ├── AI_CFD_OPTIMIZATION_AGENT.md # Closed-loop CFD workflow spec
│   └── PDF/                    # Additional PDF documentation
│
├── 📂 scripts/                 # Utility Scripts
│   └── Scraper/                # Data scraping utilities
│
├── README.md                   # This file
└── .gitignore                  # Git ignore rules
```

## 🔌 API Endpoints

### Base URL: `http://127.0.0.1:8001/api`

| Endpoint             | Method | Description                     |
| -------------------- | ------ | ------------------------------- |
| `/api/`              | GET    | API status                      |
| `/api/materials/`    | GET    | List available alloys           |
| `/api/recommend/`    | POST   | Heat sink optimization          |
| `/api/predict-ml/`   | POST   | ML-based prediction             |
| `/api/cfd-optimize/` | POST   | AI-CFD closed-loop optimization |

For required payloads, parameter constraints, and expected response formats, see [docs/API_REFERENCE_DETAILED.md](docs/API_REFERENCE_DETAILED.md).

## 📦 Dependencies

### Backend

```bash
cd backend
pip install -r requirements_django.txt
```

- Django 6.0.3
- djangorestframework 3.16.1
- django-cors-headers 4.9.0
- numpy, scipy, pandas, joblib, scikit-learn
- gunicorn (for production)

### Frontend

```bash
cd ui
npm install
```

- React 19.0.0
- TypeScript 5.x
- Vite 5.4.21
- Tailwind CSS 3.4
- shadcn-ui components

## 🧪 Development

### Run Backend

```bash
cd backend
python manage.py runserver 8001
```

### Run Frontend

```bash
cd ui
npm run dev
```

### Run Tests

```bash
cd backend
python verify_and_test_system.py --quick
```

Additional test modes:

```bash
cd backend
python verify_api_backend.py
python interactive_full_test_cli.py
python interactive_api_test_cli.py
python verify_and_test_system.py
```

Interactive option:

```bash
cd backend
python fins_cli.py
```

## 🎯 Features

- ✅ Advanced heat sink optimization algorithms
- ✅ Multiple aluminum alloy support (6063-T5, 6061-T6, 1050A)
- ✅ ML-based thermal predictions
- ✅ Real-time optimization with constraint handling
- ✅ Unified Optimizer with left-side vertical configuration panel
- ✅ Analysis Results card with fin description fields (including number of fins)
- ✅ Turbulence separation toggle in Unified Optimizer CFD controls
- ✅ Modern responsive UI
- ✅ TypeScript for type safety
- ✅ RESTful API with Django
- ✅ CORS enabled for development
- ✅ Human-readable logging for API and Django operations
- ✅ Four focused test entry scripts (full, API verify, interactive full, interactive API)
- ✅ Interactive backend CLI with menu-first workflow

## 🔁 AI-CFD Closed-Loop Design Workflow

### Process Overview

1. **AI Tool -> Generates Design (O/P)**
   - The AI tool creates an initial geometry, parameters, and design.
   - This is labeled as O/P (output).

2. **Output -> CFD Tool**
   - The generated design is passed into Computational Fluid Dynamics (CFD).
   - CFD runs simulation (flow, pressure, drag, heat, etc.).

3. **Validation Step**
   - Results from CFD are validated against constraints.
   - Example checks:
     - Drag < threshold
     - Pressure drop acceptable
     - Flow uniformity OK
     - Temperature within limits

4. **Decision**
   - **YES -> Accept ✅**
     - Design meets performance requirements.
   - **NO -> Redesign Loop 🔁**
     - Feedback goes back to the AI tool.
     - AI modifies geometry and resubmits to CFD.

### Current Implementation (March 2026)

- Backend endpoint: `POST /cfd-optimize/`
- Orchestrator: `backend/core/cfd_closed_loop.py` (`CFDOptimizationAgent`)
- Unified UI tab: `Unified Optimizer` in `ui/src/components/UnifiedOptimization.tsx`

Unified Optimizer now provides:

- Left vertical Configuration card (motor + CFD parameters)
- `Allow Turbulence Separation` toggle mapped to `allow_separation`
- `Analysis Results` card with:
  - Valid Design
  - Geometry
  - Parameters (Number of Fins, Fin Height, Fin Spacing, Geometry Type, Tip Thickness, Taper Angle)
  - Material Alloy

The Analysis Results section combines CFD optimization output with recommendation
data from `POST /recommend/` so fin-specific fields (for example Number of Fins)
are populated when available.

Number of Fins rendering behavior:

- Primary source: `POST /recommend/` response (`parameters.n`)
- Fallback source: CFD optimization summary when compatible fin metadata is present
- Final fallback: displays `N/A` only if neither response contains fin-count metadata

The surrogate model is now motor-aware. It uses motor power, voltage/current,
max temperature, and motor dimensions (diameter/length) to adjust CFD difficulty.
Higher motor stress increases pressure drop risk, reduces velocity uniformity,
and can trigger `thermal_stress_zone` in weak regions.

### Loop Flow

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

### Technical Meaning

- **AI** = design generator / optimizer
- **CFD** = physics truth engine
- **Validator** = objective function
- **Loop** = closed-loop optimization

- AI + simulation optimization
- Surrogate-based design
- Generative engineering
- Autonomous engineering loop

## 🚢 Production Deployment

### Backend (Gunicorn)

```bash
cd backend
pip install gunicorn
gunicorn fins_project.wsgi:application --bind 0.0.0.0:8000
```

### Frontend (Build)

```bash
cd ui
npm run build
```

## 📖 Documentation

- **Documentation Hub (Start Here)**: [backend/README_BACKEND.md](backend/README_BACKEND.md)
- **Testing Guide**: [backend/TESTING_GUIDE.md](backend/TESTING_GUIDE.md)
- **Quick Start**: [backend/QUICKSTART.py](backend/QUICKSTART.py)
- **Detailed API Reference**: [docs/API_REFERENCE_DETAILED.md](docs/API_REFERENCE_DETAILED.md)
- **Materials Database**: [docs/MATERIALS_DATABASE.md](docs/MATERIALS_DATABASE.md)
- **Django Documentation**: [docs/README_DJANGO.md](docs/README_DJANGO.md)
- **Code Explanation**: [docs/CODE_EXPLAINED.md](docs/CODE_EXPLAINED.md)
- **ML Algorithms**: [docs/ML_ALGORITHMS.md](docs/ML_ALGORITHMS.md)
- **AI-CFD Optimization Agent Spec**: [docs/AI_CFD_OPTIMIZATION_AGENT.md](docs/AI_CFD_OPTIMIZATION_AGENT.md)
- **Implementation Summary**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

## 🤝 Contributing

This is a production-ready system. All core functionality is complete and tested.

## 📄 License

Proprietary - Heat Sink Optimization System

---

**Last Updated**: March 25, 2026
