#!/usr/bin/env python
"""
Quick setup script for the Heat Sink Optimization System
"""

import os
import subprocess
import sys

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")

def setup_backend():
    """Setup backend dependencies"""
    print_header("Setting up Backend (Django)")
    
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    requirements = os.path.join(backend_dir, 'requirements_django.txt')
    
    if not os.path.exists(requirements):
        print("❌ requirements_django.txt not found!")
        return False
    
    print("Installing Python dependencies...")
    result = subprocess.run([
        sys.executable, "-m", "pip", "install", "-r", requirements
    ])
    
    if result.returncode != 0:
        print("❌ Failed to install backend dependencies")
        return False
    
    print("✅ Backend dependencies installed")
    
    # Run migrations
    print("\nRunning database migrations...")
    os.chdir(backend_dir)
    result = subprocess.run([sys.executable, "manage.py", "migrate"])
    
    if result.returncode != 0:
        print("❌ Failed to run migrations")
        return False
    
    print("✅ Database migrations complete")
    return True

def setup_frontend():
    """Setup frontend dependencies"""
    print_header("Setting up Frontend (React + TypeScript)")
    
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    
    if not os.path.exists(os.path.join(frontend_dir, 'package.json')):
        print("❌ package.json not found!")
        return False
    
    print("Installing Node.js dependencies...")
    os.chdir(frontend_dir)
    result = subprocess.run(["npm", "install"])
    
    if result.returncode != 0:
        print("❌ Failed to install frontend dependencies")
        return False
    
    print("✅ Frontend dependencies installed")
    return True

def main():
    """Main setup process"""
    print_header("Heat Sink Optimization System - Setup")
    
    # Change to project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Setup backend
    if not setup_backend():
        print("\n❌ Backend setup failed!")
        return 1
    
    # Setup frontend
    if not setup_frontend():
        print("\n❌ Frontend setup failed!")
        return 1
    
    # Success message
    print_header("✅ Setup Complete!")
    print("To run the application:\n")
    print("Backend (Django):")
    print("  cd backend")
    print("  python start_django.py\n")
    print("Frontend (React):")
    print("  cd frontend")
    print("  npm run dev\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
