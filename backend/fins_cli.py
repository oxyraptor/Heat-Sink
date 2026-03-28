#!/usr/bin/env python
"""
Fins Project - Interactive System Management CLI

Provides an interactive menu for managing the Fins heat sink optimization system:
- Start/stop Django server
- Run tests and health checks
- View documentation
- Manage database
- View logs
"""

import sys
import os
import subprocess
import platform
import time
import webbrowser
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fins_project.settings')

import django
django.setup()

from core.logger import FinsLogger, ColorCodes

# Initialize CLI logger
logger = FinsLogger("FINS_CLI", output_file="logs/cli.log")

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent.absolute()
PYTHON_CMD = sys.executable
API_BASE_URL = "http://127.0.0.1:8001/api"
DOCS_DIR = BASE_DIR.parent / "docs"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_banner():
    """Print application banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║               🌡️  FINS - Heat Sink Optimization System 🌡️                    ║
║                                                                               ║
║                    Interactive Management Console v1.0                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """
    print(f"{ColorCodes.BOLD}{ColorCodes.CYAN}{banner}{ColorCodes.ENDC}")


def print_menu():
    """Print main menu options"""
    menu = f"""
{ColorCodes.BOLD}════════════════════════════════════════════════════════════════{ColorCodes.ENDC}
                          MAIN MENU
{ColorCodes.BOLD}════════════════════════════════════════════════════════════════{ColorCodes.ENDC}

{ColorCodes.GREEN}Server Management:{ColorCodes.ENDC}
  1. Start Django Development Server
  2. Start Production Server (Gunicorn)
  3. Stop Server
  4. Check Server Status

{ColorCodes.GREEN}Testing & Verification:{ColorCodes.ENDC}
  5. Quick Health Check
    6. Verify Backend/API
  7. Run Full Test Suite
    8. Interactive Full Test CLI
    9. Interactive API Test CLI

{ColorCodes.GREEN}Documentation:{ColorCodes.ENDC}
  10. View API Documentation
  11. View Materials Database
  12. View CFD Documentation
  13. View Architecture Guide

{ColorCodes.GREEN}System Management:{ColorCodes.ENDC}
  14. View Recent Logs
  15. Clear Logs
  16. Database Operations
  17. Project Status

{ColorCodes.GREEN}Other:{ColorCodes.ENDC}
  18. Open Browser to API
  19. View Help
  0. Exit

{ColorCodes.BOLD}════════════════════════════════════════════════════════════════{ColorCodes.ENDC}
    """
    print(menu)


def print_help():
    """Print detailed help information"""
    help_text = f"""
{ColorCodes.BOLD}{ColorCodes.HEADER}FINS PROJECT - SYSTEM HELP{ColorCodes.ENDC}

{ColorCodes.BOLD}Overview:{ColorCodes.ENDC}
The Fins system is an advanced heat sink optimization platform that provides:
- Physics-based heat sink design (fast)
- ML-based geometry prediction (very fast)  
- AI-CFD closed-loop optimization (precise, slower)

{ColorCodes.BOLD}API Endpoints:{ColorCodes.ENDC}
  GET  /                  - System status check
  GET  /materials/        - List available materials
  POST /recommend/        - Quick heat sink recommendation
  POST /predict-ml/       - ML-based geometry prediction
  POST /cfd-optimize/     - Advanced CFD optimization

{ColorCodes.BOLD}Quick Start:{ColorCodes.ENDC}
  1. Select option "1" to start the development server
  2. Wait for "System ready on http://127.0.0.1:8001"
  3. Select option "5" to run a quick health check
  4. Select option "18" to open the API in your browser

{ColorCodes.BOLD}Testing:{ColorCodes.ENDC}
  - Quick Health Check:  Verifies system dependencies
  - API Tests:           Tests all 5 API endpoints
    - Full Suite:          Includes health, API, Django, integration tests
  - Takes 2-10 minutes depending on test type

{ColorCodes.BOLD}Documentation:{ColorCodes.ENDC}
  - API Reference:       Complete API documentation with examples
  - Materials Database:  Details on all 6 aluminum alloys
  - CFD Guide:           Information about optimization algorithm
  - Architecture:        System design and component overview

{ColorCodes.BOLD}Log Locations:{ColorCodes.ENDC}
  - API Requests:   logs/api.log
  - Django Output:  logs/django.log
  - Test Results:   logs/test_results.log
  - CLI Output:     logs/cli.log

{ColorCodes.BOLD}Performance Notes:{ColorCodes.ENDC}
  - Recommendation:  < 500ms
  - ML Prediction:   < 1s
  - CFD Optimization: 5-15 minutes (configurable)

{ColorCodes.BOLD}Troubleshooting:{ColorCodes.ENDC}
  - Server won't start: Check PORT 8001 is available
  - ML errors: Ensure ml_models/ directory has .pkl files
  - Test failures: Check logs/test_results.log for details

{ColorCodes.BOLD}Documentation Files:{ColorCodes.ENDC}
  - README.md                      - Project overview
    - docs/README.md                 - Documentation index
  - API_REFERENCE_DETAILED.md      - Full API documentation
  - MATERIALS_DATABASE.md          - Material specifications
  - CODE_EXPLAINED.md              - Code structure
  - ML_ALGORITHMS.md               - ML model details
  - AI_CFD_OPTIMIZATION_AGENT.md  - CFD algorithm details

Press ENTER to return to menu...
    """
    print(help_text)
    input()


# ============================================================================
# SERVER MANAGEMENT FUNCTIONS
# ============================================================================

def start_dev_server():
    """Start Django development server"""
    logger.section("Starting Django Development Server")
    logger.info("Django server will start on http://127.0.0.1:8001/")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        cmd = [PYTHON_CMD, "start_django.py"]
        logger.start_operation("Django Dev Server", command=" ".join(cmd))
        subprocess.run(cmd, cwd=str(BASE_DIR))
    except KeyboardInterrupt:
        logger.warning("Server stopped by user")
    except Exception as e:
        logger.error("Failed to start server", exception=e)
    finally:
        print("\nReturning to menu...")
        time.sleep(2)


def start_production_server():
    """Start Gunicorn production server"""
    logger.section("Starting Gunicorn Production Server")
    
    try:
        host = input("Enter host (default 0.0.0.0): ") or "0.0.0.0"
        port = input("Enter port (default 8000): ") or "8000"
        workers = input("Enter number of workers (default 4): ") or "4"
        
        logger.info(f"Starting server on {host}:{port} with {workers} workers")
        cmd = [PYTHON_CMD, "start_production.py", host, port, workers]
        logger.start_operation("Gunicorn Server", host=host, port=port, workers=workers)
        subprocess.run(cmd, cwd=str(BASE_DIR))
    except KeyboardInterrupt:
        logger.warning("Server stopped by user")
    except Exception as e:
        logger.error("Failed to start production server", exception=e)
    finally:
        print("\nReturning to menu...")
        time.sleep(2)


def stop_server():
    """Stop running server"""
    logger.section("Stopping Server")
    
    try:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                          capture_output=True)
            logger.info("Sent kill signal to Python processes")
        else:
            subprocess.run(["pkill", "-f", "start_django.py"],
                          capture_output=True)
            logger.info("Sent kill signal to Django server")
        
        logger.success("Server stopped successfully")
        time.sleep(1)
    except Exception as e:
        logger.error("Failed to stop server", exception=e)
    finally:
        print("\nReturning to menu...")
        time.sleep(2)


def check_server_status():
    """Check if server is running"""
    logger.section("Checking Server Status")
    
    try:
        import requests
        response = requests.get(API_BASE_URL, timeout=2)
        logger.success("Server is RUNNING and responding")
        logger.info(f"API Base URL: {API_BASE_URL}")
        
        # Try to get status
        try:
            status = requests.get(f"{API_BASE_URL}/").json()
            logger.info(f"System Status: {status.get('status', 'Unknown')}")
        except:
            pass
            
    except Exception as e:
        logger.error("Server is NOT RUNNING", exception=e)
        logger.info("Start the server with option 1 or 2")
    
    print("\nPress ENTER to continue...")
    input()


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def run_quick_health_check():
    """Run quick health check"""
    logger.section("Running Quick Health Check")
    
    try:
        cmd = [PYTHON_CMD, "verify_and_test_system.py", "--quick"]
        subprocess.run(cmd, cwd=str(BASE_DIR))
    except Exception as e:
        logger.error("Health check failed", exception=e)
    finally:
        print("\nPress ENTER to continue...")
        input()


def run_api_tests():
    """Run API endpoint tests"""
    logger.section("Running API Endpoint Tests")
    
    try:
        cmd = [PYTHON_CMD, "verify_api_backend.py"]
        subprocess.run(cmd, cwd=str(BASE_DIR))
    except Exception as e:
        logger.error("API tests failed", exception=e)
    finally:
        print("\nPress ENTER to continue...")
        input()


def run_full_tests():
    """Run full test suite"""
    logger.section("Running Full Test Suite")
    logger.warning("This may take 5-10 minutes. Continue? (y/n): ", end="")
    
    if input().lower() == 'y':
        try:
            cmd = [PYTHON_CMD, "verify_and_test_system.py"]
            subprocess.run(cmd, cwd=str(BASE_DIR))
        except Exception as e:
            logger.error("Full test suite failed", exception=e)
    else:
        logger.info("Test suite cancelled")
    
    print("\nPress ENTER to continue...")
    input()


def run_interactive_full_tests():
    """Launch interactive full-system test CLI"""
    logger.section("Launching Interactive Full Test CLI")

    try:
        cmd = [PYTHON_CMD, "interactive_full_test_cli.py"]
        subprocess.run(cmd, cwd=str(BASE_DIR))
    except Exception as e:
        logger.error("Interactive full test CLI failed", exception=e)
    finally:
        print("\nPress ENTER to continue...")
        input()


def run_interactive_api_tests():
    """Launch interactive API test CLI"""
    logger.section("Launching Interactive API Test CLI")

    try:
        cmd = [PYTHON_CMD, "interactive_api_test_cli.py"]
        subprocess.run(cmd, cwd=str(BASE_DIR))
    except Exception as e:
        logger.error("Interactive API test CLI failed", exception=e)
    finally:
        print("\nPress ENTER to continue...")
        input()


# ============================================================================
# DOCUMENTATION FUNCTIONS
# ============================================================================

def view_api_docs():
    """View API documentation"""
    logger.section("API Documentation")
    doc_file = DOCS_DIR / "API_REFERENCE_DETAILED.md"
    
    if doc_file.exists():
        logger.info(f"Opening: {doc_file}")
        try:
            # Try to open with default viewer
            if platform.system() == "Windows":
                os.startfile(str(doc_file))
            else:
                subprocess.run(["open" if platform.system() == "Darwin" else "xdg-open",
                              str(doc_file)])
            logger.success("Documentation opened")
        except:
            # Fallback: display first part
            with open(doc_file, 'r') as f:
                content = f.read(2000)
                print(f"\n{ColorCodes.BOLD}{content}...{ColorCodes.ENDC}\n")
    else:
        logger.warning(f"Documentation not found: {doc_file}")
    
    print("\nPress ENTER to continue...")
    input()


def view_materials_db():
    """View materials database documentation"""
    logger.section("Materials Database")
    doc_file = DOCS_DIR / "MATERIALS_DATABASE.md"
    
    if doc_file.exists():
        logger.success(f"Opening: {doc_file}")
        try:
            if platform.system() == "Windows":
                os.startfile(str(doc_file))
            else:
                subprocess.run(["open" if platform.system() == "Darwin" else "xdg-open",
                              str(doc_file)])
        except:
            with open(doc_file, 'r') as f:
                content = f.read(2000)
                print(f"\n{ColorCodes.BOLD}{content}...{ColorCodes.ENDC}\n")
    else:
        logger.warning(f"Documentation not found: {doc_file}")
    
    print("\nPress ENTER to continue...")
    input()


def view_cfd_docs():
    """View CFD documentation"""
    logger.section("CFD Optimization Details")
    doc_file = DOCS_DIR / "AI_CFD_OPTIMIZATION_AGENT.md"
    
    if doc_file.exists():
        logger.success(f"Opening: {doc_file}")
        try:
            if platform.system() == "Windows":
                os.startfile(str(doc_file))
            else:
                subprocess.run(["open" if platform.system() == "Darwin" else "xdg-open",
                              str(doc_file)])
        except:
            with open(doc_file, 'r') as f:
                content = f.read(2000)
                print(f"\n{ColorCodes.BOLD}{content}...{ColorCodes.ENDC}\n")
    else:
        logger.warning(f"Documentation not found: {doc_file}")
    
    print("\nPress ENTER to continue...")
    input()


def view_architecture():
    """View architecture guide"""
    logger.section("Architecture Guide")
    doc_file = DOCS_DIR / "README.md"
    
    if doc_file.exists():
        logger.success(f"Opening: {doc_file}")
        try:
            if platform.system() == "Windows":
                os.startfile(str(doc_file))
            else:
                subprocess.run(["open" if platform.system() == "Darwin" else "xdg-open",
                              str(doc_file)])
        except:
            with open(doc_file, 'r') as f:
                content = f.read(2000)
                print(f"\n{ColorCodes.BOLD}{content}...{ColorCodes.ENDC}\n")
    else:
        logger.warning(f"Documentation not found: {doc_file}")
    
    print("\nPress ENTER to continue...")
    input()


# ============================================================================
# SYSTEM MANAGEMENT FUNCTIONS
# ============================================================================

def view_recent_logs():
    """View recent log entries"""
    logger.section("Recent Log Entries")
    
    log_dir = BASE_DIR / "logs"
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        if not log_files:
            logger.info("No log files found")
        else:
            logger.info(f"Found {len(log_files)} log files:")
            for lf in log_files[:5]:
                print(f"  - {lf.name}")
                
                # Show last 5 lines
                try:
                    with open(lf, 'r') as f:
                        lines = f.readlines()[-5:]
                        for line in lines:
                            print(f"    {line.rstrip()}")
                except:
                    pass
    else:
        logger.warning("Logs directory does not exist")
    
    print("\nPress ENTER to continue...")
    input()


def clear_logs():
    """Clear log files"""
    logger.section("Clear Logs")
    logger.warning("Are you sure? This will delete all log files. (y/n): ", end="")
    
    if input().lower() == 'y':
        log_dir = BASE_DIR / "logs"
        if log_dir.exists():
            import glob
            for lf in glob.glob(str(log_dir / "*.log")):
                try:
                    os.remove(lf)
                    logger.success(f"Deleted: {lf}")
                except Exception as e:
                    logger.error(f"Failed to delete {lf}", exception=e)
        else:
            logger.info("Logs directory does not exist")
    else:
        logger.info("Clear logs cancelled")
    
    print("\nPress ENTER to continue...")
    input()


def database_operations():
    """Database management menu"""
    logger.section("Database Operations")
    
    db_menu = f"""
{ColorCodes.BOLD}Database Operations:{ColorCodes.ENDC}
  1. Run migrations
  2. Create superuser
  3. Show database info
  4. Back to main menu
    
Enter choice: """
    
    choice = input(db_menu).strip()
    
    try:
        if choice == '1':
            logger.info("Running database migrations...")
            subprocess.run([PYTHON_CMD, "manage.py", "migrate"],
                         cwd=str(BASE_DIR))
            logger.success("Migrations completed")
        elif choice == '2':
            logger.info("Creating superuser...")
            subprocess.run([PYTHON_CMD, "manage.py", "createsuperuser"],
                         cwd=str(BASE_DIR))
            logger.success("Superuser created")
        elif choice == '3':
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    logger.success("Database tables:")
                    for table in tables:
                        print(f"  - {table[0]}")
            except Exception as e:
                logger.error("Could not retrieve database info", exception=e)
    except Exception as e:
        logger.error("Database operation failed", exception=e)
    
    print("\nReturning to menu...")
    time.sleep(1)


def project_status():
    """Show comprehensive project status"""
    logger.section("Project Status")
    
    logger.info("Checking project components...")
    
    # Check directories
    checks = {
        "Backend": BASE_DIR / "fins_api" / "views.py",
        "Frontend": BASE_DIR.parent / "ui" / "src" / "App.tsx",
        "ML Models": BASE_DIR / "ml_models" / "thermal_model.pkl",
        "Documentation": DOCS_DIR / "README_DJANGO.md",
        "Tests": BASE_DIR / "tests" / "conftest.py",
        "Logs": BASE_DIR / "logs",
    }
    
    for component, path in checks.items():
        if path.exists():
            logger.success(f"{component}: ✓ Ready")
        else:
            logger.warning(f"{component}: ✗ Not found ({path})")
    
    # Check web server
    logger.info("\nChecking if API is running...")
    try:
        import requests
        response = requests.get(API_BASE_URL, timeout=2)
        logger.success("API Server: ✓ Running")
    except:
        logger.warning("API Server: ✗ Not running (start with option 1)")
    
    print("\nPress ENTER to continue...")
    input()


# ============================================================================
# BROWSER FUNCTIONS
# ============================================================================

def open_api_in_browser():
    """Open API documentation in browser"""
    logger.section("Opening API in Browser")
    
    logger.info(f"Opening {API_BASE_URL}...")
    print(f"\n{ColorCodes.GREEN}Opening in browser...{ColorCodes.ENDC}\n")
    
    try:
        webbrowser.open(API_BASE_URL)
        logger.success("Browser opened successfully")
        time.sleep(2)
    except Exception as e:
        logger.error("Could not open browser", exception=e)
        logger.info(f"Please manually visit: {API_BASE_URL}")
        time.sleep(3)


# ============================================================================
# MAIN MENU LOOP
# ============================================================================

def main_loop():
    """Main interactive menu loop"""
    while True:
        try:
            print("\033c" if platform.system() != "Windows" else "cls")  # Clear screen
            print_banner()
            print_menu()
            
            choice = input(f"\n{ColorCodes.BOLD}Enter your choice (0-19): {ColorCodes.ENDC}").strip()
            
            if choice == '0':
                logger.section("Exiting Fins Management Console")
                logger.info("Goodbye!")
                print(f"\n{ColorCodes.GREEN}Thank you for using Fins!{ColorCodes.ENDC}\n")
                break
            
            elif choice == '1':
                start_dev_server()
            elif choice == '2':
                start_production_server()
            elif choice == '3':
                stop_server()
            elif choice == '4':
                check_server_status()
            
            elif choice == '5':
                run_quick_health_check()
            elif choice == '6':
                run_api_tests()
            elif choice == '7':
                run_full_tests()
            elif choice == '8':
                run_interactive_full_tests()
            elif choice == '9':
                run_interactive_api_tests()
            
            elif choice == '10':
                view_api_docs()
            elif choice == '11':
                view_materials_db()
            elif choice == '12':
                view_cfd_docs()
            elif choice == '13':
                view_architecture()
            
            elif choice == '14':
                view_recent_logs()
            elif choice == '15':
                clear_logs()
            elif choice == '16':
                database_operations()
            elif choice == '17':
                project_status()
            
            elif choice == '18':
                open_api_in_browser()
            elif choice == '19':
                print_help()
            
            else:
                logger.warning("Invalid choice. Please select 0-19")
                time.sleep(2)
        
        except KeyboardInterrupt:
            logger.warning("\nInterrupted by user")
            break
        except Exception as e:
            logger.error("Menu error", exception=e)
            time.sleep(2)


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    try:
        main_loop()
    except Exception as e:
        logger.error("Fatal error in CLI", exception=e)
        sys.exit(1)


if __name__ == "__main__":
    main()
