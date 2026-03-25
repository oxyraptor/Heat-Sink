#!/usr/bin/env python
"""
Fins Project - Backend/API Verification Runner

Dedicated API verification script.

Usage:
    python verify_api_backend.py
    python verify_api_backend.py --base-url http://127.0.0.1:8001/api
"""

import argparse
import sys

import verify_and_test_system as test_engine


def main() -> int:
    parser = argparse.ArgumentParser(description="Run API verification tests only")
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://127.0.0.1:8001/api",
        help="API base URL (default: http://127.0.0.1:8001/api)",
    )
    args = parser.parse_args()

    test_engine.configure_base_url(args.base_url)
    success = test_engine.run_api_tests_only()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
