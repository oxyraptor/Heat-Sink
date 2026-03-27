"""
Pytest configuration and Django setup for all tests.
This module ensures Django is properly initialized before any tests run.
"""

import os
import sys
import django

# Add parent directory to path to allow imports of fins_api, core, etc.
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fins_project.settings')
django.setup()
