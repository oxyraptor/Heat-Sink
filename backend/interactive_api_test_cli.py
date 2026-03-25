#!/usr/bin/env python
"""
Interactive API Test CLI.

Provides a guided interface to:
- Run standard backend API verification
- Test a single endpoint with custom payload (inline JSON or file)
- Validate standard endpoint responses with existing validators
"""

import json
import sys
from pathlib import Path

import requests

import verify_and_test_system as test_engine


ENDPOINT_MAP = {
    "1": ("GET", "/"),
    "2": ("GET", "/materials/"),
    "3": ("POST", "/recommend/"),
    "4": ("POST", "/predict-ml/"),
    "5": ("POST", "/cfd-optimize/"),
}


def prompt_base_url() -> str:
    default = "http://127.0.0.1:8001/api"
    value = input(f"API base URL [{default}]: ").strip()
    return value or default


def load_payload() -> dict:
    source = input("Payload source: 1) inline JSON 2) file path [1]: ").strip() or "1"
    if source == "2":
        file_path = input("Enter JSON file path: ").strip()
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    raw = input("Enter JSON payload: ").strip()
    if not raw:
        return {}
    return json.loads(raw)


def validate_known_endpoint(path: str, data: dict) -> tuple[bool, list[str]]:
    if path == "/":
        return test_engine.ResponseValidator.validate_status_response(data)
    if path == "/materials/":
        return test_engine.ResponseValidator.validate_materials_response(data)
    if path == "/recommend/":
        return test_engine.ResponseValidator.validate_recommendation_response(data)
    if path == "/predict-ml/":
        return test_engine.ResponseValidator.validate_ml_prediction_response(data)
    if path == "/cfd-optimize/":
        return test_engine.ResponseValidator.validate_cfd_response(data)
    return True, []


def run_custom_request(base_url: str):
    print("\nEndpoint options:")
    print("  1) GET /")
    print("  2) GET /materials/")
    print("  3) POST /recommend/")
    print("  4) POST /predict-ml/")
    print("  5) POST /cfd-optimize/")
    print("  6) Custom method/path")

    choice = input("Select endpoint: ").strip()

    if choice in ENDPOINT_MAP:
        method, path = ENDPOINT_MAP[choice]
    else:
        method = input("HTTP method (GET/POST/PUT/DELETE): ").strip().upper() or "GET"
        path = input("Path (example /materials/): ").strip() or "/"

    payload = None
    if method in {"POST", "PUT", "PATCH"}:
        try:
            payload = load_payload()
        except Exception as exc:
            print(f"Invalid payload: {exc}")
            return

    url = f"{base_url.rstrip('/')}" + (path if path.startswith("/") else f"/{path}")
    timeout = input("Timeout seconds [30]: ").strip()
    timeout_value = int(timeout) if timeout else 30

    print(f"\nRequest: {method} {url}")
    response = requests.request(method, url, json=payload, timeout=timeout_value)
    print(f"Status: {response.status_code}")

    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type.lower():
        data = response.json()
        print("Response JSON:")
        print(json.dumps(data, indent=2)[:4000])

        valid, errors = validate_known_endpoint(path, data)
        if valid:
            print("Validation: PASS")
        else:
            print("Validation: FAIL")
            for err in errors:
                print(f"  - {err}")
    else:
        print("Response Text:")
        print(response.text[:2000])


def main() -> int:
    print("=" * 68)
    print("FINS INTERACTIVE API TEST CLI")
    print("=" * 68)

    base_url = prompt_base_url()
    test_engine.configure_base_url(base_url)

    while True:
        print("\nChoose an option:")
        print("  1) Run standard API verification suite")
        print("  2) Run custom API request")
        print("  3) Change API base URL")
        print("  0) Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            ok = test_engine.run_api_tests_only()
            print("\nResult:", "PASS" if ok else "FAIL")
        elif choice == "2":
            run_custom_request(base_url)
        elif choice == "3":
            base_url = prompt_base_url()
            test_engine.configure_base_url(base_url)
        elif choice == "0":
            print("Exiting interactive API test CLI")
            return 0
        else:
            print("Invalid option. Choose 0, 1, 2, or 3.")


if __name__ == "__main__":
    sys.exit(main())
