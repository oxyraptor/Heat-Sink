# Fins API Reference Documentation

**Last Updated:** 2026-03-25  
**API Version:** 1.0.0  
**Base URL:** `http://localhost:8001/api`

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Response Format](#response-format)
4. [Error Handling](#error-handling)
5. [Endpoints](#endpoints)
   - [System Status](#system-status-endpoint)
   - [Materials](#materials-endpoint)
   - [Heat Sink Recommendation](#heat-sink-recommendation-endpoint)
   - [ML Prediction](#ml-prediction-endpoint)
   - [CFD Optimization](#cfd-optimization-endpoint)

---

## Overview

The Fins API is a RESTful service for optimizing aluminum heat sink designs for electric motor thermal management. It provides three primary optimization approaches:

- **Rule-based Recommendation**: Fast physics-based optimization using thermal equations
- **ML-based Prediction**: Machine learning inverse design prediction
- **AI-CFD Optimization**: Closed-loop iterative optimization using computational fluid dynamics

### Base URL

```
http://localhost:8001/api
```

### Server Status

- Development: `http://127.0.0.1:8001/`
- Production: Configurable via Gunicorn (default: `http://0.0.0.0:8000/`)

---

## Authentication

**Current Status:** No authentication required (open API)

All endpoints are publicly accessible without authentication tokens or API keys.

---

## Response Format

All API responses follow a consistent JSON format:

### Success Response (2xx)

```json
{
  "success": true,
  "data": {
    "recommended_geometry": {...},
    "thermal_performance": {...}
  },
  "message": "Operation completed successfully"
}
```

### Error Response (4xx, 5xx)

```json
{
  "success": false,
  "error": "Detailed error message",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field_name": "Validation error description"
  }
}
```

---

## Error Handling

### Common Error Codes

| Error Code          | HTTP Status | Description                      |
| ------------------- | ----------- | -------------------------------- |
| `VALIDATION_ERROR`  | 400         | Invalid input parameters         |
| `INVALID_MATERIAL`  | 400         | Specified material not available |
| `COMPUTATION_ERROR` | 500         | Optimization computation failed  |
| `CFD_TIMEOUT`       | 504         | CFD simulation exceeded timeout  |
| `MISSING_PARSER`    | 500         | ML model not loaded              |

### Example Error Response

```json
{
  "success": false,
  "error": "Invalid motor power value",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "motor_power_w": "Must be a positive number, got: -100"
  }
}
```

---

## Endpoints

---

## System Status Endpoint

**Check API health and system status**

### Request

```
GET /
```

### Response

**Status:** 200 OK

```json
{
  "status": "operational",
  "version": "1.0.0",
  "services": {
    "ml_models": "loaded",
    "materials_db": "initialized",
    "cfd_engine": "ready"
  },
  "timestamp": "2026-03-25T14:30:45Z"
}
```

### Example cURL

```bash
curl -X GET http://localhost:8001/api/
```

### Example Python

```python
import requests

response = requests.get('http://localhost:8001/api/')
print(response.json())
```

---

## Materials Endpoint

**Retrieve available aluminum alloy materials with thermal properties**

### Request

```
GET /materials/
```

### Query Parameters

None required. All materials returned by default.

### Response

**Status:** 200 OK

```json
{
  "success": true,
  "data": [
    {
      "id": "AL6063",
      "name": "Aluminum 6063-T5",
      "density": 2.7,
      "thermal_conductivity": 201,
      "specific_heat": 896,
      "cost_per_kg": 2.5,
      "machinability": 8,
      "availability": "High"
    },
    {
      "id": "AL6061",
      "name": "Aluminum 6061-T6",
      "density": 2.7,
      "thermal_conductivity": 167,
      "specific_heat": 896,
      "cost_per_kg": 2.2,
      "machinability": 7,
      "availability": "High"
    },
    {
      "id": "AL7075",
      "name": "Aluminum 7075-T73",
      "density": 2.81,
      "thermal_conductivity": 130,
      "specific_heat": 960,
      "cost_per_kg": 12.0,
      "machinability": 4,
      "availability": "Medium"
    }
  ],
  "count": 6,
  "message": "Materials retrieved successfully"
}
```

### Material Properties Definition

| Field                  | Unit   | Type   | Description                          |
| ---------------------- | ------ | ------ | ------------------------------------ |
| `id`                   | -      | string | Material identifier code             |
| `name`                 | -      | string | Full material name                   |
| `density`              | g/cm³  | float  | Material density                     |
| `thermal_conductivity` | W/m·K  | float  | Heat conduction coefficient          |
| `specific_heat`        | J/kg·K | float  | Heat capacity per unit mass          |
| `cost_per_kg`          | USD    | float  | Material cost                        |
| `machinability`        | 0-10   | int    | Manufacturing ease (higher = easier) |
| `availability`         | -      | string | Market availability                  |

### Example cURL

```bash
curl -X GET http://localhost:8001/api/materials/
```

### Example Python

```python
import requests

response = requests.get('http://localhost:8001/api/materials/')
materials = response.json()['data']

for material in materials:
    print(f"{material['name']}: {material['thermal_conductivity']} W/m·K")
```

---

## Heat Sink Recommendation Endpoint

**Generate optimized heat sink design using physics-based algorithms**

### Request

```
POST /recommend/
```

### Request Payload

```json
{
  "motor_specs": {
    "power_w": 5000,
    "efficiency": 0.92,
    "rpm": 3000,
    "surface_area_cm2": 150,
    "ambient_temp_c": 25
  },
  "environment": {
    "max_junction_temp_c": 120,
    "air_velocity_mps": 2.0,
    "humidity_percent": 60
  },
  "constraints": {
    "material": "AL6063",
    "max_fin_height_mm": 100,
    "max_base_thickness_mm": 30,
    "max_fin_pitch_mm": 15
  },
  "optimization_target": "thermal_resistance"
}
```

### Request Parameters

#### `motor_specs` (Required)

| Parameter          | Unit  | Type  | Range     | Description                          |
| ------------------ | ----- | ----- | --------- | ------------------------------------ |
| `power_w`          | Watts | float | > 0       | Motor electrical power output        |
| `efficiency`       | %     | float | 0-1       | Motor efficiency (0.85-0.95 typical) |
| `rpm`              | rpm   | int   | > 0       | Motor rotational speed               |
| `surface_area_cm2` | cm²   | float | > 0       | Motor housing surface area           |
| `ambient_temp_c`   | °C    | float | -40 to 70 | Ambient temperature                  |

#### `environment` (Required)

| Parameter             | Unit | Type  | Range          | Description                       |
| --------------------- | ---- | ----- | -------------- | --------------------------------- |
| `max_junction_temp_c` | °C   | float | > ambient_temp | Maximum safe junction temperature |
| `air_velocity_mps`    | m/s  | float | > 0            | Air velocity over heat sink       |
| `humidity_percent`    | %    | int   | 0-100          | Relative humidity                 |

#### `constraints` (Required)

| Parameter               | Unit | Type   | Description                           |
| ----------------------- | ---- | ------ | ------------------------------------- |
| `material`              | -    | string | Material ID from materials endpoint   |
| `max_fin_height_mm`     | mm   | float  | Maximum fin height                    |
| `max_base_thickness_mm` | mm   | float  | Maximum base/mounting plate thickness |
| `max_fin_pitch_mm`      | mm   | float  | Maximum distance between fins         |

#### `optimization_target` (Optional)

| Value                | Description                              |
| -------------------- | ---------------------------------------- |
| `thermal_resistance` | **Default**: Minimize thermal resistance |
| `cost`               | Minimize total cost                      |
| `weight`             | Minimize total weight                    |
| `manufacturability`  | Optimize for ease of manufacturing       |

### Response

**Status:** 200 OK

```json
{
  "success": true,
  "data": {
    "recommended_geometry": {
      "fin_height_mm": 85,
      "fin_thickness_mm": 2.5,
      "fin_pitch_mm": 12,
      "base_thickness_mm": 20,
      "number_of_fins": 14,
      "total_mass_g": 450,
      "material": "AL6063"
    },
    "thermal_performance": {
      "thermal_resistance_k_per_w": 0.042,
      "junction_temp_c": 85,
      "heat_removal_rate_w": 4600,
      "convection_coefficient_w_m2k": 125
    },
    "manufacturing_info": {
      "cost_usd": 18.5,
      "machining_time_hours": 1.25,
      "complexity_score": 6.5
    },
    "design_summary": "Optimized aluminum heat sink with 14 fins for maximal thermal efficiency"
  },
  "message": "Design recommendation generated successfully"
}
```

### Response Fields

#### `recommended_geometry`

| Field               | Unit  | Description                  |
| ------------------- | ----- | ---------------------------- |
| `fin_height_mm`     | mm    | Height of cooling fins       |
| `fin_thickness_mm`  | mm    | Thickness of each fin        |
| `fin_pitch_mm`      | mm    | Distance between fin centers |
| `base_thickness_mm` | mm    | Mounting base thickness      |
| `number_of_fins`    | count | Number of fins to machine    |
| `total_mass_g`      | grams | Total heat sink mass         |
| `material`          | -     | Material used (from input)   |

#### `thermal_performance`

| Field                          | Unit   | Description                          |
| ------------------------------ | ------ | ------------------------------------ |
| `thermal_resistance_k_per_w`   | K/W    | Temperature rise per watt dissipated |
| `junction_temp_c`              | °C     | Resulting motor junction temperature |
| `heat_removal_rate_w`          | Watts  | Maximum sustainable heat removal     |
| `convection_coefficient_w_m2k` | W/m²·K | Air-side convection efficiency       |

#### `manufacturing_info`

| Field                  | Unit  | Description                                |
| ---------------------- | ----- | ------------------------------------------ |
| `cost_usd`             | USD   | Estimated material + labor cost            |
| `machining_time_hours` | hours | Estimated CNC machining time               |
| `complexity_score`     | 0-10  | Manufacturing complexity (higher = harder) |

### Error Response

**Status:** 400 Bad Request

```json
{
  "success": false,
  "error": "Invalid thermal constraint specification",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "max_junction_temp_c": "Must be greater than ambient temperature (25°C)"
  }
}
```

### Example cURL - Basic Request

```bash
curl -X POST http://localhost:8001/api/recommend/ \
  -H "Content-Type: application/json" \
  -d '{
    "motor_specs": {
      "power_w": 5000,
      "efficiency": 0.92,
      "rpm": 3000,
      "surface_area_cm2": 150,
      "ambient_temp_c": 25
    },
    "environment": {
      "max_junction_temp_c": 120,
      "air_velocity_mps": 2.0,
      "humidity_percent": 60
    },
    "constraints": {
      "material": "AL6063",
      "max_fin_height_mm": 100,
      "max_base_thickness_mm": 30,
      "max_fin_pitch_mm": 15
    }
  }'
```

### Example Python - Full Request

```python
import requests
import json

url = 'http://localhost:8001/api/recommend/'

payload = {
    "motor_specs": {
        "power_w": 5000,
        "efficiency": 0.92,
        "rpm": 3000,
        "surface_area_cm2": 150,
        "ambient_temp_c": 25
    },
    "environment": {
        "max_junction_temp_c": 120,
        "air_velocity_mps": 2.0,
        "humidity_percent": 60
    },
    "constraints": {
        "material": "AL6063",
        "max_fin_height_mm": 100,
        "max_base_thickness_mm": 30,
        "max_fin_pitch_mm": 15
    },
    "optimization_target": "thermal_resistance"
}

response = requests.post(url, json=payload)
result = response.json()

if result['success']:
    geom = result['data']['recommended_geometry']
    perf = result['data']['thermal_performance']

    print(f"✓ Recommendation Generated")
    print(f"  Fins: {geom['number_of_fins']} × {geom['fin_height_mm']}mm")
    print(f"  Junction Temp: {perf['junction_temp_c']}°C")
    print(f"  Thermal R: {perf['thermal_resistance_k_per_w']:.4f} K/W")
    print(f"  Cost: ${result['data']['manufacturing_info']['cost_usd']:.2f}")
else:
    print(f"✗ Error: {result['error']}")
```

---

## ML Prediction Endpoint

**Fast inverse prediction: Predict geometry from thermal specifications using machine learning**

### Request

```
POST /predict-ml/
```

### Request Payload

```json
{
  "problem_specs": {
    "power_w": 5000,
    "efficiency": 0.92,
    "target_junction_temp_c": 85,
    "ambient_temp_c": 25,
    "air_velocity_mps": 2.0
  },
  "material": "AL6063",
  "constraints": {
    "max_fin_height_mm": 100,
    "max_base_thickness_mm": 30
  }
}
```

### Request Parameters

#### `problem_specs` (Required)

| Parameter                | Unit  | Type  | Description                  |
| ------------------------ | ----- | ----- | ---------------------------- |
| `power_w`                | Watts | float | Motor power dissipation      |
| `efficiency`             | %     | float | Motor efficiency (0-1)       |
| `target_junction_temp_c` | °C    | float | Desired junction temperature |
| `ambient_temp_c`         | °C    | float | Ambient temperature          |
| `air_velocity_mps`       | m/s   | float | Cooling air velocity         |

#### `material` (Required)

Material ID from `/materials/` endpoint

#### `constraints` (Optional)

Optional geometry constraints for the prediction

### Response

**Status:** 200 OK

```json
{
  "success": true,
  "data": {
    "predicted_geometry": {
      "fin_height_mm": 80,
      "fin_thickness_mm": 2.3,
      "fin_pitch_mm": 11,
      "base_thickness_mm": 18,
      "number_of_fins": 15,
      "confidence_percent": 92.3
    },
    "predicted_performance": {
      "estimated_thermal_resistance_k_per_w": 0.045,
      "expected_junction_temp_c": 86,
      "model_accuracy": 0.94
    }
  },
  "message": "ML prediction completed successfully"
}
```

### Response Fields

| Field                | Unit  | Description                                   |
| -------------------- | ----- | --------------------------------------------- |
| `predicted_geometry` | -     | Predicted heat sink dimensions                |
| `confidence_percent` | %     | Model confidence in prediction (0-100)        |
| `model_accuracy`     | ratio | Historical accuracy on similar problems (0-1) |

### Example cURL

```bash
curl -X POST http://localhost:8001/api/predict-ml/ \
  -H "Content-Type: application/json" \
  -d '{
    "problem_specs": {
      "power_w": 5000,
      "efficiency": 0.92,
      "target_junction_temp_c": 85,
      "ambient_temp_c": 25,
      "air_velocity_mps": 2.0
    },
    "material": "AL6063"
  }'
```

### Example Python

```python
import requests

response = requests.post(
    'http://localhost:8001/api/predict-ml/',
    json={
        "problem_specs": {
            "power_w": 5000,
            "efficiency": 0.92,
            "target_junction_temp_c": 85,
            "ambient_temp_c": 25,
            "air_velocity_mps": 2.0
        },
        "material": "AL6063"
    }
)

data = response.json()['data']
print(f"Predicted fins: {data['predicted_geometry']['number_of_fins']}")
print(f"Confidence: {data['predicted_geometry']['confidence_percent']}%")
```

---

## CFD Optimization Endpoint

**Advanced AI-CFD closed-loop optimization for high-precision designs**

### Request

```
POST /cfd-optimize/
```

### Request Payload

```json
{
  "problem_specs": {
    "power_w": 5000,
    "efficiency": 0.92,
    "target_junction_temp_c": 85,
    "ambient_temp_c": 25,
    "air_velocity_mps": 3.0
  },
  "material": "AL6063",
  "optimization_params": {
    "max_iterations": 20,
    "refinement_tolerance": 2.0,
    "timeout_seconds": 600,
    "cfd_mesh_quality": "medium"
  },
  "initial_geometry": {
    "fin_height_mm": 80,
    "fin_thickness_mm": 2.5,
    "fin_pitch_mm": 12,
    "base_thickness_mm": 20
  }
}
```

### Request Parameters

#### `problem_specs` (Required)

Same as ML Prediction endpoint.

#### `material` (Required)

Material ID from `/materials/` endpoint.

#### `optimization_params` (Optional)

| Parameter              | Unit    | Type   | Default  | Description                              |
| ---------------------- | ------- | ------ | -------- | ---------------------------------------- |
| `max_iterations`       | count   | int    | 15       | Maximum optimization iterations          |
| `refinement_tolerance` | K/W     | float  | 1.0      | Target improvement per iteration         |
| `timeout_seconds`      | seconds | int    | 600      | Maximum optimization time                |
| `cfd_mesh_quality`     | -       | string | "medium" | Mesh density: "coarse", "medium", "fine" |

#### `initial_geometry` (Optional)

Starting point for optimization. If omitted, ML prediction used.

### Response

**Status:** 200 OK

```json
{
  "success": true,
  "data": {
    "optimized_geometry": {
      "fin_height_mm": 82,
      "fin_thickness_mm": 2.4,
      "fin_pitch_mm": 11.5,
      "base_thickness_mm": 19,
      "number_of_fins": 15,
      "total_mass_g": 445
    },
    "performance_metrics": {
      "thermal_resistance_k_per_w": 0.041,
      "junction_temp_c": 84,
      "heat_dissipation_w": 4620,
      "pressure_drop_pa": 45,
      "flow_uniformity_percent": 94
    },
    "optimization_log": {
      "iterations_completed": 12,
      "convergence_time_minutes": 8.23,
      "improvement_percent": 6.8,
      "final_status": "converged"
    },
    "cfd_analysis": {
      "average_velocity_mps": 2.95,
      "max_velocity_mps": 4.2,
      "recirculation_zones": 2,
      "flow_separation": false
    }
  },
  "message": "CFD optimization completed successfully with 12 iterations"
}
```

### Response Fields

#### `optimized_geometry`

Refined heat sink dimensions after CFD iteration.

#### `performance_metrics`

| Field                        | Unit  | Description                                       |
| ---------------------------- | ----- | ------------------------------------------------- |
| `thermal_resistance_k_per_w` | K/W   | Final thermal resistance                          |
| `junction_temp_c`            | °C    | Resulting junction temperature                    |
| `heat_dissipation_w`         | Watts | Achievable heat removal                           |
| `pressure_drop_pa`           | Pa    | Air pressure drop across heat sink                |
| `flow_uniformity_percent`    | %     | How uniform air distribution is (higher = better) |

#### `optimization_log`

| Field                      | Description                                |
| -------------------------- | ------------------------------------------ |
| `iterations_completed`     | Number of CFD iterations performed         |
| `convergence_time_minutes` | Time to reach convergence                  |
| `improvement_percent`      | Percentage improvement from initial design |
| `final_status`             | "converged", "max_iterations", "timeout"   |

#### `cfd_analysis`

Detailed computational fluid dynamics results.

### Long-Running Operation Behavior

This endpoint performs iterative CFD analysis which can take several minutes:

- **Timeout**: 600 seconds (10 minutes) by default
- **Progress**: You can query the same endpoint repeatedly to check progress
- **Fallback**: If CFD times out, ML prediction result is returned

### Example cURL

```bash
curl -X POST http://localhost:8001/api/cfd-optimize/ \
  -H "Content-Type: application/json" \
  -d '{
    "problem_specs": {
      "power_w": 5000,
      "efficiency": 0.92,
      "target_junction_temp_c": 85,
      "ambient_temp_c": 25,
      "air_velocity_mps": 3.0
    },
    "material": "AL6063",
    "optimization_params": {
      "max_iterations": 20,
      "cfd_mesh_quality": "medium"
    }
  }'
```

### Example Python - With Timeout Handling

```python
import requests
import time

response = requests.post(
    'http://localhost:8001/api/cfd-optimize/',
    json={
        "problem_specs": {
            "power_w": 5000,
            "efficiency": 0.92,
            "target_junction_temp_c": 85,
            "ambient_temp_c": 25,
            "air_velocity_mps": 3.0
        },
        "material": "AL6063",
        "optimization_params": {
            "max_iterations": 20,
            "timeout_seconds": 600
        }
    },
    timeout=650  # Slightly longer than server timeout
)

result = response.json()

if result['success']:
    geom = result['data']['optimized_geometry']
    log = result['data']['optimization_log']

    print(f"✓ CFD Optimization Completed")
    print(f"  Status: {log['final_status']}")
    print(f"  Iterations: {log['iterations_completed']}")
    print(f"  Time: {log['convergence_time_minutes']:.1f} min")
    print(f"  Improvement: {log['improvement_percent']}%")
    print(f"  Thermal R: {result['data']['performance_metrics']['thermal_resistance_k_per_w']:.4f} K/W")
```

---

## Rate Limiting & Performance

- **Recommendation endpoint**: < 500ms response time
- **ML Prediction**: < 1s response time
- **CFD Optimization**: 5-15 minutes depending on complexity and settings

### Performance Notes

1. **CFD Memory Usage**: ~500MB-2GB depending on mesh quality
2. **Parallel Requests**: Safe for concurrent requests (thread-safe)
3. **Caching**: Results are not cached; each request is independent

---

## Implementation Examples

### Complete Workflow Example (Python)

```python
import requests
import json

BASE_URL = 'http://localhost:8001/api'

def get_materials():
    """Fetch available materials"""
    response = requests.get(f'{BASE_URL}/materials/')
    return response.json()['data']

def recommend_design(specs):
    """Get quick recommendation"""
    response = requests.post(f'{BASE_URL}/recommend/', json=specs)
    return response.json()

def predict_ml(specs):
    """Get ML-based prediction"""
    response = requests.post(f'{BASE_URL}/predict-ml/', json=specs)
    return response.json()

def optimize_cfd(specs):
    """Run full CFD optimization"""
    response = requests.post(f'{BASE_URL}/cfd-optimize/', json=specs, timeout=700)
    return response.json()

# Workflow
motor_specs = {
    "motor_specs": {
        "power_w": 5000,
        "efficiency": 0.92,
        "rpm": 3000,
        "surface_area_cm2": 150,
        "ambient_temp_c": 25
    },
    "environment": {
        "max_junction_temp_c": 120,
        "air_velocity_mps": 2.0,
        "humidity_percent": 60
    },
    "constraints": {
        "material": "AL6063",
        "max_fin_height_mm": 100,
        "max_base_thickness_mm": 30,
        "max_fin_pitch_mm": 15
    }
}

# Step 1: Quick recommendation
print("1. Getting quick recommendation...")
rec = recommend_design(motor_specs)
print(f"   Fins: {rec['data']['recommended_geometry']['number_of_fins']}")

# Step 2: ML prediction
print("2. Running ML prediction...")
ml_specs = {
    "problem_specs": {
        "power_w": motor_specs['motor_specs']['power_w'],
        "efficiency": motor_specs['motor_specs']['efficiency'],
        "target_junction_temp_c": motor_specs['environment']['max_junction_temp_c'],
        "ambient_temp_c": motor_specs['motor_specs']['ambient_temp_c'],
        "air_velocity_mps": motor_specs['environment']['air_velocity_mps']
    },
    "material": motor_specs['constraints']['material']
}
ml = predict_ml(ml_specs)
print(f"   Confidence: {ml['data']['predicted_geometry']['confidence_percent']}%")

# Step 3: CFD optimization for best result
print("3. Running CFD optimization (may take a few minutes)...")
cfd = optimize_cfd(ml_specs)
print(f"   Status: {cfd['data']['optimization_log']['final_status']}")
print(f"   Thermal R: {cfd['data']['performance_metrics']['thermal_resistance_k_per_w']:.4f} K/W")
```

---

## Troubleshooting

### Common Issues

| Issue                  | Solution                                                        |
| ---------------------- | --------------------------------------------------------------- |
| Connection refused     | Ensure Django server is running: `python start_django.py`       |
| Invalid material error | Check `/materials/` to get valid material IDs                   |
| CFD timeout            | Reduce `max_iterations` or lower `cfd_mesh_quality` to "coarse" |
| High junction temp     | Increase `air_velocity_mps` or higher `max_fin_height_mm`       |
| ML model not loaded    | Server may still be initializing, wait 5-10 seconds and retry   |

### Debug Mode

Enable detailed logging by checking Django server logs:

```bash
tail -f logs/django.log
```

---

## Support & Documentation

For more information, see:

- [Backend Code Documentation](./CODE_EXPLAINED.md)
- [ML Algorithms Guide](./ML_ALGORITHMS.md)
- [CFD Optimization Details](./AI_CFD_OPTIMIZATION_AGENT.md)
- [Materials Database](./MATERIALS_DATABASE.md)

**Version:** 1.0.0  
**Last Updated:** 2026-03-25
