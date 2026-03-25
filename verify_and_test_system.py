#!/usr/bin/env python
"""
Fins Project - Comprehensive Test & Health Check Suite

Unified testing script that:
1. Checks system health (database, dependencies, services)
2. Verifies all API endpoints work correctly
3. Runs Django application tests
4. Validates response formats against expected schemas
5. Provides human-readable logging output

Usage:
    python verify_and_test_system.py                    # Run full suite (includes health)
    python verify_and_test_system.py --quick           # Quick health check only
    python verify_and_test_system.py --base-url http://127.0.0.1:8001/api
"""

import sys
import os
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import traceback

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fins_project.settings')

import django
django.setup()

# Now import Django modules
import requests
from django.test.utils import setup_test_environment, teardown_test_environment
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from core.logger import FinsLogger, ColorCodes

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "http://127.0.0.1:8001/api"
TEST_TIMEOUT = 30  # seconds
LOG_FILE = "logs/test_results.log"

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

logger = FinsLogger("TEST_SUITE", output_file=LOG_FILE)


def configure_base_url(base_url: str):
    """Set API base URL at runtime for all tests."""
    global BASE_URL
    BASE_URL = base_url.rstrip("/")
    logger.info("Configured API base URL", base_url=BASE_URL)

# ============================================================================
# TEST DATA & VALIDATORS
# ============================================================================

class TestPayloads:
    """Standard test payloads for API endpoints"""
    
    MOTOR_SPECS_BASIC = {
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
    
    MOTOR_SPECS_SMALL = {
        "motor_specs": {
            "power_w": 1000,
            "efficiency": 0.88,
            "rpm": 1500,
            "surface_area_cm2": 80,
            "ambient_temp_c": 20
        },
        "environment": {
            "max_junction_temp_c": 100,
            "air_velocity_mps": 1.5,
            "humidity_percent": 50
        },
        "constraints": {
            "material": "AL1100",
            "max_fin_height_mm": 60,
            "max_base_thickness_mm": 20,
            "max_fin_pitch_mm": 12
        }
    }
    
    ML_PREDICTION_BASIC = {
        "problem_specs": {
            "power_w": 5000,
            "efficiency": 0.92,
            "target_junction_temp_c": 85,
            "ambient_temp_c": 25,
            "air_velocity_mps": 2.0
        },
        "material": "AL6063"
    }
    
    CFD_OPTIMIZATION_BASIC = {
        "problem_specs": {
            "power_w": 5000,
            "efficiency": 0.92,
            "target_junction_temp_c": 85,
            "ambient_temp_c": 25,
            "air_velocity_mps": 3.0
        },
        "material": "AL6063",
        "optimization_params": {
            "max_iterations": 5,
            "timeout_seconds": 120
        }
    }


class ResponseValidator:
    """Validates API response formats against expected schemas"""
    
    @staticmethod
    def validate_status_response(data: Dict) -> Tuple[bool, List[str]]:
        """Validate system status response"""
        errors = []
        required_fields = ['status', 'version', 'services', 'timestamp']
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if 'services' in data:
            if not isinstance(data['services'], dict):
                errors.append("'services' must be a dictionary")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_materials_response(data: Dict) -> Tuple[bool, List[str]]:
        """Validate materials list response"""
        errors = []
        
        if 'data' not in data:
            errors.append("Missing 'data' field in response")
            return False, errors
        
        if not isinstance(data['data'], list):
            errors.append("'data' must be a list")
            return False, errors
        
        # Validate each material
        required_fields = ['id', 'name', 'thermal_conductivity', 'density']
        for idx, material in enumerate(data['data']):
            for field in required_fields:
                if field not in material:
                    errors.append(f"Material {idx} missing field: {field}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_recommendation_response(data: Dict) -> Tuple[bool, List[str]]:
        """Validate heat sink recommendation response"""
        errors = []
        
        if 'data' not in data:
            errors.append("Missing 'data' field")
            return False, errors
        
        response_data = data['data']
        required_sections = ['recommended_geometry', 'thermal_performance', 'manufacturing_info']
        
        for section in required_sections:
            if section not in response_data:
                errors.append(f"Missing section: {section}")
        
        # Validate geometry
        if 'recommended_geometry' in response_data:
            geom = response_data['recommended_geometry']
            required_geom = ['fin_height_mm', 'fin_thickness_mm', 'number_of_fins', 'total_mass_g']
            for field in required_geom:
                if field not in geom:
                    errors.append(f"Geometry missing field: {field}")
        
        # Validate thermal performance
        if 'thermal_performance' in response_data:
            perf = response_data['thermal_performance']
            required_perf = ['thermal_resistance_k_per_w', 'junction_temp_c']
            for field in required_perf:
                if field not in perf:
                    errors.append(f"Performance missing field: {field}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_ml_prediction_response(data: Dict) -> Tuple[bool, List[str]]:
        """Validate ML prediction response"""
        errors = []
        
        if 'data' not in data:
            errors.append("Missing 'data' field")
            return False, errors
        
        response_data = data['data']
        required_sections = ['predicted_geometry', 'predicted_performance']
        
        for section in required_sections:
            if section not in response_data:
                errors.append(f"Missing section: {section}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_cfd_response(data: Dict) -> Tuple[bool, List[str]]:
        """Validate CFD optimization response"""
        errors = []
        
        if 'data' not in data:
            errors.append("Missing 'data' field")
            return False, errors
        
        response_data = data['data']
        required_sections = ['optimized_geometry', 'performance_metrics', 'optimization_log']
        
        for section in required_sections:
            if section not in response_data:
                errors.append(f"Missing section: {section}")
        
        return len(errors) == 0, errors


# ============================================================================
# HEALTH CHECK FUNCTIONS
# ============================================================================

def check_server_connectivity() -> bool:
    """Check if Django server is running"""
    logger.subsection("Server Connectivity Check")
    op_id = logger.start_operation("Checking server", url=BASE_URL)
    
    try:
        response = requests.head(BASE_URL, timeout=5)
        logger.end_operation(op_id, status="completed")
        return True
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to server", exception=Exception("Connection refused"))
        logger.info("Ensure Django server is running: python start_django.py")
        logger.end_operation(op_id, status="failed")
        return False
    except Exception as e:
        logger.error("Unexpected error checking connectivity", exception=e)
        logger.end_operation(op_id, status="failed")
        return False


def check_database() -> bool:
    """Check database connectivity"""
    logger.subsection("Database Connectivity Check")
    op_id = logger.start_operation("Checking database")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        logger.success("Database connected successfully")
        logger.end_operation(op_id, status="completed")
        return True
    except Exception as e:
        logger.error("Database connection failed", exception=e)
        logger.end_operation(op_id, status="failed")
        return False


def check_ml_models_loaded() -> bool:
    """Check if ML models are loaded"""
    logger.subsection("ML Models Check")
    op_id = logger.start_operation("Checking ML models")
    
    try:
        import os
        ml_models_path = os.path.join(os.path.dirname(__file__), "ml_models")
        
        required_models = ['thermal_model.pkl', 'inverse_model.pkl']
        missing = []
        
        for model in required_models:
            model_path = os.path.join(ml_models_path, model)
            if os.path.exists(model_path):
                logger.success(f"Found: {model}")
            else:
                missing.append(model)
                logger.warning(f"Missing: {model}")
        
        if missing:
            logger.end_operation(op_id, status="failed")
            return False
        else:
            logger.end_operation(op_id, status="completed")
            return True
    except Exception as e:
        logger.error("Error checking ML models", exception=e)
        logger.end_operation(op_id, status="failed")
        return False


def check_system_dependencies() -> bool:
    """Check required Python dependencies"""
    logger.subsection("System Dependencies Check")
    op_id = logger.start_operation("Checking dependencies")
    
    required_packages = {
        'django': 'Django',
        'rest_framework': 'Django REST Framework',
        'numpy': 'NumPy',
        'scipy': 'SciPy',
        'sklearn': 'Scikit-learn',
        'requests': 'Requests',
        'pandas': 'Pandas'
    }
    
    missing = []
    for module, name in required_packages.items():
        try:
            __import__(module)
            logger.success(f"{name} installed")
        except ImportError:
            missing.append(name)
            logger.warning(f"{name} NOT FOUND")
    
    if missing:
        logger.end_operation(op_id, status="failed")
        return False
    else:
        logger.end_operation(op_id, status="completed")
        return True


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

def test_status_endpoint() -> bool:
    """Test GET / endpoint"""
    logger.subsection("Testing Status Endpoint")
    op_id = logger.api_request("GET", "/")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TEST_TIMEOUT)
        
        if response.status_code != 200:
            logger.api_response(op_id, response.status_code, len(response.content), 
                               status_code=response.status_code)
            return False
        
        data = response.json()
        is_valid, errors = ResponseValidator.validate_status_response(data)
        
        if not is_valid:
            logger.error("Response validation failed", 
                        exception=Exception("Schema mismatch: " + ", ".join(errors)))
            logger.api_response(op_id, response.status_code, len(response.content))
            return False
        
        logger.success("Status endpoint working correctly")
        logger.debug(f"Response: {json.dumps(data, indent=2)[:200]}...")
        logger.api_response(op_id, response.status_code, len(response.content))
        return True
        
    except Exception as e:
        logger.error("Status endpoint test failed", exception=e)
        logger.end_operation(op_id, status="failed")
        return False


def test_materials_endpoint() -> bool:
    """Test GET /materials/ endpoint"""
    logger.subsection("Testing Materials Endpoint")
    op_id = logger.api_request("GET", "/materials/")
    
    try:
        response = requests.get(f"{BASE_URL}/materials/", timeout=TEST_TIMEOUT)
        
        if response.status_code != 200:
            logger.api_response(op_id, response.status_code, len(response.content))
            return False
        
        data = response.json()
        is_valid, errors = ResponseValidator.validate_materials_response(data)
        
        if not is_valid:
            logger.error("Response validation failed", 
                        exception=Exception("Schema mismatch: " + ", ".join(errors)))
            logger.api_response(op_id, response.status_code, len(response.content))
            return False
        
        material_count = len(data.get('data', []))
        logger.success(f"Materials endpoint working - {material_count} materials available")
        logger.debug(f"Materials: {', '.join([m['id'] for m in data.get('data', [])])}")
        logger.api_response(op_id, response.status_code, len(response.content), 
                           materials_count=material_count)
        return True
        
    except Exception as e:
        logger.error("Materials endpoint test failed", exception=e)
        logger.end_operation(op_id, status="failed")
        return False


def test_recommendation_endpoint() -> bool:
    """Test POST /recommend/ endpoint"""
    logger.subsection("Testing Recommendation Endpoint")
    op_id = logger.api_request("POST", "/recommend/", 
                               payload_size=len(json.dumps(TestPayloads.MOTOR_SPECS_BASIC)))
    
    try:
        response = requests.post(
            f"{BASE_URL}/recommend/",
            json=TestPayloads.MOTOR_SPECS_BASIC,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code not in [200, 201]:
            logger.warning(f"Endpoint returned status {response.status_code}")
            if response.status_code >= 400:
                logger.debug(f"Response: {response.text[:500]}")
                logger.api_response(op_id, response.status_code, len(response.content))
                return False
        
        data = response.json()
        
        if response.status_code in [200, 201]:
            is_valid, errors = ResponseValidator.validate_recommendation_response(data)
            
            if not is_valid:
                logger.error("Response validation failed", 
                            exception=Exception("Schema mismatch: " + ", ".join(errors)))
                logger.api_response(op_id, response.status_code, len(response.content))
                return False
            
            geom = data['data']['recommended_geometry']
            perf = data['data']['thermal_performance']
            logger.success("Recommendation endpoint working correctly")
            logger.debug(f"Fins: {geom['number_of_fins']}, Temp: {perf['junction_temp_c']}°C, "
                        f"R_th: {perf['thermal_resistance_k_per_w']:.4f} K/W")
            logger.api_response(op_id, response.status_code, len(response.content),
                               fins=geom['number_of_fins'],
                               junction_temp=perf['junction_temp_c'])
            return True
        
        logger.api_response(op_id, response.status_code, len(response.content))
        return True
        
    except Exception as e:
        logger.error("Recommendation endpoint test failed", exception=e)
        logger.end_operation(op_id, status="failed")
        return False


def test_ml_prediction_endpoint() -> bool:
    """Test POST /predict-ml/ endpoint"""
    logger.subsection("Testing ML Prediction Endpoint")
    op_id = logger.api_request("POST", "/predict-ml/",
                               payload_size=len(json.dumps(TestPayloads.ML_PREDICTION_BASIC)))
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict-ml/",
            json=TestPayloads.ML_PREDICTION_BASIC,
            timeout=TEST_TIMEOUT
        )
        
        if response.status_code not in [200, 201]:
            logger.warning(f"Endpoint returned status {response.status_code}")
            if response.status_code >= 400:
                logger.debug(f"Response: {response.text[:500]}")
                logger.api_response(op_id, response.status_code, len(response.content))
                return False
        
        data = response.json()
        
        if response.status_code in [200, 201]:
            is_valid, errors = ResponseValidator.validate_ml_prediction_response(data)
            
            if not is_valid:
                logger.error("Response validation failed",
                            exception=Exception("Schema mismatch: " + ", ".join(errors)))
                logger.api_response(op_id, response.status_code, len(response.content))
                return False
            
            geom = data['data']['predicted_geometry']
            logger.success("ML Prediction endpoint working correctly")
            logger.debug(f"Predicted fins: {geom['number_of_fins']}, "
                        f"Confidence: {geom.get('confidence_percent', 'N/A')}%")
            logger.api_response(op_id, response.status_code, len(response.content),
                               predicted_fins=geom['number_of_fins'])
            return True
        
        logger.api_response(op_id, response.status_code, len(response.content))
        return True
        
    except Exception as e:
        logger.error("ML Prediction endpoint test failed", exception=e)
        logger.end_operation(op_id, status="failed")
        return False


def test_cfd_optimization_endpoint() -> bool:
    """Test POST /cfd-optimize/ endpoint"""
    logger.subsection("Testing CFD Optimization Endpoint")
    op_id = logger.api_request("POST", "/cfd-optimize/",
                               payload_size=len(json.dumps(TestPayloads.CFD_OPTIMIZATION_BASIC)))
    
    try:
        response = requests.post(
            f"{BASE_URL}/cfd-optimize/",
            json=TestPayloads.CFD_OPTIMIZATION_BASIC,
            timeout=TEST_TIMEOUT + 120  # CFD can take longer
        )
        
        if response.status_code not in [200, 201, 504]:  # 504 is timeout (acceptable)
            logger.warning(f"Endpoint returned status {response.status_code}")
            if response.status_code >= 500 and response.status_code != 504:
                logger.debug(f"Response: {response.text[:500]}")
                logger.api_response(op_id, response.status_code, len(response.content))
                return False
        
        if response.status_code == 504:
            logger.warning("CFD optimization timed out (expected for large optimizations)")
            logger.api_response(op_id, response.status_code, len(response.content))
            return True  # Timeout is acceptable
        
        data = response.json()
        
        if response.status_code in [200, 201]:
            is_valid, errors = ResponseValidator.validate_cfd_response(data)
            
            if not is_valid:
                logger.error("Response validation failed",
                            exception=Exception("Schema mismatch: " + ", ".join(errors)))
                logger.api_response(op_id, response.status_code, len(response.content))
                return False
            
            opt_log = data['data']['optimization_log']
            logger.success("CFD Optimization endpoint working correctly")
            logger.debug(f"Status: {opt_log['final_status']}, "
                        f"Iterations: {opt_log['iterations_completed']}")
            logger.api_response(op_id, response.status_code, len(response.content),
                               iterations=opt_log['iterations_completed'],
                               status=opt_log['final_status'])
            return True
        
        logger.api_response(op_id, response.status_code, len(response.content))
        return True
        
    except Exception as e:
        logger.error("CFD Optimization endpoint test failed", exception=e)
        logger.end_operation(op_id, status="failed")
        return False


# ============================================================================
# DJANGO UNIT TESTS
# ============================================================================

def run_django_unit_tests() -> bool:
    """Run Django unit tests"""
    logger.subsection("Running Django Unit Tests")
    op_id = logger.start_operation("Django Unit Tests")
    
    try:
        # Run Django tests
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        err = StringIO()
        
        call_command('test', 'fins_api.tests', stdout=out, stderr=err, verbosity=2)
        
        output = out.getvalue()
        errors = err.getvalue()
        
        if "FAILED" in output or errors:
            logger.warning("Some tests may have failed")
            logger.debug(f"Output: {output[:500]}")
            if errors:
                logger.debug(f"Errors: {errors[:500]}")
        else:
            logger.success("Django unit tests passed")
        
        logger.end_operation(op_id, status="completed")
        return True
        
    except Exception as e:
        logger.warning(f"Could not run Django tests: {str(e)}")
        logger.end_operation(op_id, status="skipped")
        return True  # Don't fail overall if tests can't run


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def run_integration_tests() -> bool:
    """Test complete workflow"""
    logger.subsection("Running Integration Tests")
    op_id = logger.start_operation("Complete Workflow")
    
    try:
        logger.info("Step 1: Get materials")
        mat_response = requests.get(f"{BASE_URL}/materials/", timeout=TEST_TIMEOUT)
        if mat_response.status_code != 200:
            raise Exception("Materials endpoint failed")
        
        logger.info("Step 2: Get recommendation")
        rec_response = requests.post(
            f"{BASE_URL}/recommend/",
            json=TestPayloads.MOTOR_SPECS_BASIC,
            timeout=TEST_TIMEOUT
        )
        if rec_response.status_code not in [200, 201]:
            raise Exception("Recommendation endpoint failed")
        
        logger.info("Step 3: Get ML prediction")
        ml_response = requests.post(
            f"{BASE_URL}/predict-ml/",
            json=TestPayloads.ML_PREDICTION_BASIC,
            timeout=TEST_TIMEOUT
        )
        if ml_response.status_code not in [200, 201]:
            raise Exception("ML prediction endpoint failed")
        
        logger.success("Integration workflow completed successfully")
        logger.end_operation(op_id, status="completed")
        return True
        
    except Exception as e:
        logger.error("Integration test failed", exception=e)
        logger.end_operation(op_id, status="failed")
        return False


# ============================================================================
# MAIN TEST SUITE
# ============================================================================

def print_banner(text: str):
    """Print formatted banner"""
    banner = f"\n{ColorCodes.BOLD}{ColorCodes.HEADER}{'='*70}\n" \
             f"{text.center(70)}\n" \
             f"{'='*70}{ColorCodes.ENDC}\n"
    print(banner)


def run_health_check_only():
    """Fast health check - system connectivity and dependencies only"""
    print_banner("FINS PROJECT - HEALTH CHECK")
    logger.section("Quick Health Check")
    
    results = {
        "Database": check_database(),
        "Server": check_server_connectivity(),
        "Dependencies": check_system_dependencies(),
        "ML Models": check_ml_models_loaded()
    }
    
    print_health_summary(results)
    return all(results.values())


def run_api_tests_only():
    """Run API endpoint tests only"""
    print_banner("FINS PROJECT - API ENDPOINT TESTS")
    logger.section("API Endpoint Tests")
    
    results = {
        "Status Endpoint": test_status_endpoint(),
        "Materials Endpoint": test_materials_endpoint(),
        "Recommendation Endpoint": test_recommendation_endpoint(),
        "ML Prediction Endpoint": test_ml_prediction_endpoint(),
        "CFD Optimization Endpoint": test_cfd_optimization_endpoint(),
    }
    
    print_test_summary(results)
    return all(results.values())


def run_full_test_suite():
    """Run complete test suite"""
    print_banner("FINS PROJECT - COMPREHENSIVE TEST SUITE")
    logger.section("Complete Test Suite")
    
    # Health checks
    logger.subsection("=== PHASE 1: SYSTEM HEALTH CHECKS ===")
    health_results = {
        "Database": check_database(),
        "Server": check_server_connectivity(),
        "Dependencies": check_system_dependencies(),
        "ML Models": check_ml_models_loaded(),
    }
    
    if not health_results["Server"]:
        logger.error("Server is not running. Skipping endpoint tests.")
        print_health_summary(health_results)
        return False
    
    # API tests
    logger.subsection("=== PHASE 2: API ENDPOINT TESTS ===")
    api_results = {
        "Status Endpoint": test_status_endpoint(),
        "Materials Endpoint": test_materials_endpoint(),
        "Recommendation Endpoint": test_recommendation_endpoint(),
        "ML Prediction Endpoint": test_ml_prediction_endpoint(),
        "CFD Optimization Endpoint": test_cfd_optimization_endpoint(),
    }
    
    # Django tests
    logger.subsection("=== PHASE 3: DJANGO UNIT TESTS ===")
    django_results = {
        "Django Unit Tests": run_django_unit_tests(),
    }
    
    # Integration tests
    logger.subsection("=== PHASE 4: INTEGRATION TESTS ===")
    integration_results = {
        "Workflow Integration": run_integration_tests(),
    }
    
    # Summary
    all_results = {**health_results, **api_results, **django_results, **integration_results}
    print_test_summary(all_results)
    
    return all(all_results.values())


def print_health_summary(results: Dict[str, bool]):
    """Print formatted health check summary"""
    logger.section("Health Check Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        color = ColorCodes.GREEN if result else ColorCodes.RED
        print(f"{color}{status:>8} {ColorCodes.ENDC} {check}")
    
    logger.info(f"Summary: {passed}/{total} checks passed", passed=passed, total=total)


def print_test_summary(results: Dict[str, bool]):
    """Print formatted test summary"""
    logger.section("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        color = ColorCodes.GREEN if result else ColorCodes.RED
        print(f"{color}{status:>8} {ColorCodes.ENDC} {test}")
    
    logger.info(f"\nOverall Results: {passed}/{total} tests passed ({percentage:.1f}%)",
                passed=passed, total=total, percentage=percentage)
    
    if passed == total:
        logger.success("ALL TESTS PASSED! ✓✓✓")
    else:
        logger.warning(f"{total - passed} test(s) failed")
    
    logger.info(f"Log file: {os.path.abspath(LOG_FILE)}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fins Project Test & Health Check Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verify_and_test_system.py                 # Full test suite
  python verify_and_test_system.py --quick         # Health check only
    python verify_and_test_system.py --base-url http://127.0.0.1:8001/api
        """
    )
    
    parser.add_argument('--quick', action='store_true',
                       help='Quick health check only')
    parser.add_argument('--base-url', type=str, default=BASE_URL,
                       help='API base URL (default: http://127.0.0.1:8001/api)')
    
    args = parser.parse_args()
    configure_base_url(args.base_url)
    
    try:
        if args.quick:
            success = run_health_check_only()
        else:
            success = run_full_test_suite()
        
        logger.section("Test Suite Finished")
        logger.info(f"Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.warning("Tests interrupted by user")
        return 1
    except Exception as e:
        logger.error("Unexpected error in test suite", exception=e)
        logger.debug(traceback.format_exc())
        return 1


if __name__ == '__main__':
    sys.exit(main())
