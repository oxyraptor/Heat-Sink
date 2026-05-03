# Heat Sink Optimization API - Django REST Framework

This is the Django REST Framework implementation of the Heat Sink Optimization API, migrated from FastAPI.

## Project Structure

```
Fins/
├── fins_project/           # Django project directory
│   ├── __init__.py
│   ├── settings.py         # Django settings
│   ├── urls.py             # Project URL configuration
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── fins_api/               # Django app for API
│   ├── __init__.py
│   ├── apps.py             # App configuration
│   ├── models.py           # Database models (none needed)
│   ├── serializers.py      # DRF serializers
│   ├── views.py            # DRF ViewSets and views
│   ├── urls.py             # App URL configuration
│   ├── admin.py            # Admin configuration
│   └── tests.py            # Test cases
├── manage.py               # Django management script
├── optimizer.py            # Heat sink optimization logic (unchanged)
├── materials.py            # Material properties (unchanged)
├── requirements_django.txt # Django dependencies
└── README_DJANGO.md        # This file
```

## Installation

1. **Install dependencies:**

```bash
pip install -r requirements_django.txt
```

2. **Run migrations (creates SQLite database):**

```bash
python manage.py migrate
```

3. **Create superuser (optional, for admin access):**

```bash
python manage.py createsuperuser
```

## Running the Server

### Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

### Specify Port

```bash
python manage.py runserver 8000
```

### Production (using gunicorn)

```bash
pip install gunicorn
gunicorn fins_project.wsgi:application --bind 0.0.0.0:8000
```

## API Endpoints

All endpoints remain the same as the FastAPI implementation:

### 1. Status Endpoint
- **URL:** `GET /`
- **Description:** Returns API status
- **Response:**
```json
{
  "status": "System Operational",
  "message": "Heat Sink Optimization API"
}
```

### 2. Materials List
- **URL:** `GET /materials/`
- **Description:** Returns list of available aluminum alloys
- **Response:**
```json
{
  "alloys": ["6063-T5", "6061-T6", "1050A"]
}
```

### 3. Heat Sink Recommendation
- **URL:** `POST /recommend/`
- **Description:** Generates optimal heat sink design
- **Request Body:**
```json
{
  "motor": {
    "motor_type": "Servo",
    "rated_power": 1000,
    "rated_voltage": 48,
    "rated_current": 25,
    "max_temp": 120,
    "casing_width": 0.1,
    "casing_length": 0.1,
    "casing_height": 0.1
  },
  "environment": {
    "ambient_temp": 25,
    "airflow_type": "Forced",
    "air_velocity": 5
  },
  "constraints": {
    "max_height": 0.05,
    "min_fin_thickness": 0.001
  },
  "preferred_alloy": "6063-T5"
}
```

### 4. ML Prediction
- **URL:** `POST /predict-ml/`
- **Description:** ML-based geometry prediction
- **Request Body:**
```json
{
  "Q_heat": 100,
  "width": 0.1,
  "length": 0.1,
  "ambient": 25,
  "velocity": 5,
  "N": 10,
  "H": 0.03,
  "t_base": 0.002,
  "geom_type": "Rectangular"
}
```

## Testing

### Run Tests

```bash
python manage.py test
```

### Run Specific Test

```bash
python manage.py test fins_api.tests.HeatSinkAPITestCase.test_status_endpoint
```

### Run with Coverage

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Key Differences from FastAPI

### 1. Project Structure
- Django uses a project + app structure
- Settings are centralized in `settings.py`

### 2. Serializers
- Uses DRF `Serializer` classes instead of Pydantic `BaseModel`
- Validation is handled by DRF

### 3. Views
- Uses DRF `ViewSet` and `APIView` instead of FastAPI route decorators
- HTTP methods are explicit (e.g., `def post(self, request)`)

### 4. Routing
- URLs are defined in `urls.py` files
- Uses Django's URL dispatcher

### 5. CORS
- Uses `django-cors-headers` middleware instead of FastAPI's CORS middleware

### 6. Running
- Uses `manage.py runserver` instead of `uvicorn`

## Maintained Logic

All business logic from the FastAPI implementation is preserved:

- ✅ Heat sink optimization algorithms (`optimizer.py`)
- ✅ Material properties database (`materials.py`)
- ✅ ML model integration (thermal_model.pkl, inverse_model.pkl)
- ✅ Physics calculations
- ✅ Constraint handling
- ✅ Error handling
- ✅ Response formatting

## Configuration

### CORS Settings

By default, CORS is enabled for all origins (development):

```python
CORS_ALLOW_ALL_ORIGINS = True
```

For production, update `fins_project/settings.py`:

```python
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    # Add your frontend URLs
]
```

### Debug Mode

For production, set in `settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'your-ip']
```

## Admin Interface

Django provides a built-in admin interface at `/admin/`

1. Create superuser: `python manage.py createsuperuser`
2. Visit: `http://127.0.0.1:8000/admin/`

## Deployment

### Using Gunicorn + Nginx

1. Install gunicorn: `pip install gunicorn`
2. Run: `gunicorn fins_project.wsgi:application --bind 0.0.0.0:8000`
3. Configure Nginx as reverse proxy

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements_django.txt .
RUN pip install -r requirements_django.txt

COPY . .
RUN python manage.py migrate

CMD ["gunicorn", "fins_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Build and run:
```bash
docker build -t fins-api .
docker run -p 8000:8000 fins-api
```

## Migration Notes

The Django implementation maintains 100% compatibility with the existing frontend:
- All endpoint URLs are the same
- Request/response formats are identical
- CORS configuration matches FastAPI setup
- Error handling is equivalent

Simply update the frontend API base URL if the port changed, then it works seamlessly!
