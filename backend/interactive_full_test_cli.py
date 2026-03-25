#!/usr/bin/env python
"""
Interactive Full-System Test CLI.

Provides a guided CLI for:
- Quick health checks
- Full suite execution
- Base URL selection
"""

import sys

import verify_and_test_system as test_engine


def prompt_base_url() -> str:
    default = "http://127.0.0.1:8001/api"
    value = input(f"API base URL [{default}]: ").strip()
    return value or default


def main() -> int:
    print("=" * 68)
    print("FINS INTERACTIVE FULL TEST CLI")
    print("=" * 68)

    base_url = prompt_base_url()
    test_engine.configure_base_url(base_url)

    while True:
        print("\nChoose an option:")
        print("  1) Quick health check")
        print("  2) Full test suite (health + API + Django + integration)")
        print("  3) Change API base URL")
        print("  0) Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            ok = test_engine.run_health_check_only()
            print("\nResult:", "PASS" if ok else "FAIL")
        elif choice == "2":
            ok = test_engine.run_full_test_suite()
            print("\nResult:", "PASS" if ok else "FAIL")
        elif choice == "3":
            base_url = prompt_base_url()
            test_engine.configure_base_url(base_url)
        elif choice == "0":
            print("Exiting interactive full test CLI")
            return 0
        else:
            print("Invalid option. Choose 0, 1, 2, or 3.")


if __name__ == "__main__":
    sys.exit(main())
