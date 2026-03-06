# Project Structure - Quick Reference

## Overview

The project has been reorganized into a clean, professional structure:

```
Fins/
├── backend/          # All Django/Python code
├── frontend/         # All React/TypeScript code
├── docs/             # All documentation
├── scripts/          # Utility scripts
├── setup.py          # One-command setup
└── README.md         # Main documentation
```

##  Detailed Structure

### Backend (`backend/`)
```
backend/
├── core/                       # Business Logic
│   ├── optimizer.py            # Heat sink optimization
│   ├── materials.py            # Material properties
│   └── __init__.py
│
├── ml_models/                  # ML Models
│   ├── thermal_model.pkl
│   └── inverse_model.pkl
│
├── fins_project/               # Django Project
│   ├── settings.py             # ← Updated with sys.path
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── fins_api/                   # Django App
│   ├── views.py                # ← Updated imports
│   ├── serializers.py
│   ├── urls.py
│   └── tests.py
│
├── manage.py
├── start_django.py             # Dev server
├── start_production.py         # Production server
├── requirements_django.txt
└── db.sqlite3
```

### Frontend (`frontend/`)
```
frontend/
├── src/
│   ├── App.tsx                 # Main component
│   ├── main.tsx                # Entry point
│   ├── components/             # UI components
│   │   └── ui/                 # shadcn-ui
│   └── lib/
│       └── utils.ts
│
├── public/
├── package.json
├── vite.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

### Documentation (`docs/`)
```
docs/
├── CODE_EXPLAINED.md
├── ML_ALGORITHMS.md
├── README_DJANGO.md
├── FASTAPI_TO_DJANGO_MIGRATION.md
└── PDF/
```

### Scripts (`scripts/`)
```
scripts/
└── Scraper/
    ├── scraper.py
    └── servo_motor_specs.csv
```

## 🔧 Code Changes Made

### 1. Updated `backend/fins_api/views.py`
```python
# OLD
from materials import list_materials
from optimizer import DesignOptimizer
ml_model = joblib.load("thermal_model.pkl")

# NEW
from core.materials import list_materials
from core.optimizer import DesignOptimizer
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML_MODELS_DIR = os.path.join(BASE_DIR, 'ml_models')
ml_model = joblib.load(os.path.join(ML_MODELS_DIR, "thermal_model.pkl"))
```

### 2. Updated `backend/fins_project/settings.py`
```python
# Added sys.path configuration
import sys
sys.path.insert(0, str(BASE_DIR))
```
##  Running the Application

### Quick Setup (First Time)
```bash
python setup.py
```

### Development Mode
```bash
# Terminal 1 - 
python start_django.py

# Terminal 2 - Frontend
npm run dev
```

### Production Mode
```bash
# Backend
pip install gunicorn
python start_production.py

# Frontend
npm run build
```

## Important Paths

| Old Path | New Path |
|----------|----------|
| `optimizer.py` | `backend/core/optimizer.py` |
| `materials.py` | `backend/core/materials.py` |
| `thermal_model.pkl` | `backend/ml_models/thermal_model.pkl` |
| `inverse_model.pkl` | `backend/ml_models/inverse_model.pkl` |
| `manage.py` | `backend/manage.py` |
| `fins_project/` | `backend/fins_project/` |
| `fins_api/` | `backend/fins_api/` |
| `ui/` | `frontend/` |
| `CODE_EXPLAINED.md` | `docs/CODE_EXPLAINED.md` |
| `Scraper/` | `scripts/Scraper/` |

## Benefits of New Structure

1. **Clear Separation**: Backend, frontend, docs, and scripts are clearly separated
2. **Professional**: Follows industry-standard project layout
3. **Scalable**: Easy to add new modules or features
4. **Maintainable**: Easier to navigate and understand
5. **Deployable**: Backend and frontend can be deployed independently

## 🔍 Finding Files

### Backend Code
```bash
cd backend
# Business logic: core/
# API code: fins_api/
# ML models: ml_models/
# Config: fins_project/
```

### Frontend Code
```bash
cd frontend
# Components: src/components/
# Main app: src/App.tsx
# Config: vite.config.ts, tailwind.config.ts
```

### Documentation
```bash
cd docs
# All markdown files and PDFs here
```

## 🆘 Troubleshooting

### Import Error: `No module named 'core'`
**Solution**: Make sure you're running from the `backend/` directory and that `settings.py` has the sys.path modification.

### Frontend not connecting to backend
**Solution**: Check that backend is running on port 8001 and update frontend API base URL if needed.

### ML Models not loading
**Solution**: Ensure `thermal_model.pkl` and `inverse_model.pkl` are in `backend/ml_models/` directory.

---

**Last Updated**: March 6, 2026
