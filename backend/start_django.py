#!/usr/bin/env python
"""
Quick start script for Django API server
"""

import subprocess
import sys
import os


def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")
    try:
        import django
        import rest_framework
        import corsheaders
        print("✓ All dependencies installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependencies: {e}")
        print("\nInstalling dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "Django", "djangorestframework", "django-cors-headers"
        ])
        return True


def run_migrations():
    """Run Django migrations"""
    print("\nRunning migrations...")
    result = subprocess.run([
        sys.executable, "manage.py", "migrate"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Migrations completed")
    else:
        print(f"✗ Migration failed: {result.stderr}")
        return False
    return True


def start_server(port=8001):
    """Start Django development server"""
    print(f"\nStarting Django server on port {port}...")
    print(f"API will be available at: http://127.0.0.1:{port}/")
    print("\nEndpoints:")
    print(f"  - GET  http://127.0.0.1:{port}/")
    print(f"  - GET  http://127.0.0.1:{port}/materials/")
    print(f"  - POST http://127.0.0.1:{port}/recommend/")
    print(f"  - POST http://127.0.0.1:{port}/predict-ml/")
    print("\nPress Ctrl+C to stop the server\n")
    
    subprocess.run([
        sys.executable, "manage.py", "runserver", str(port)
    ])


if __name__ == "__main__":
    print("=" * 60)
    print("Heat Sink Optimization API - Django Server")
    print("=" * 60)
    
    # Change to Fins directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check and install dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    # Start server
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    start_server(port)
