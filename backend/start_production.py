"""
Production WSGI server starter using Gunicorn
"""

import subprocess
import sys

def start_production_server(host='0.0.0.0', port=8000, workers=4):
    """
    Start production server with Gunicorn
    
    Args:
        host: Server host (default: 0.0.0.0)
        port: Server port (default: 8000)
        workers: Number of worker processes (default: 4)
    """
    print("=" * 60)
    print("Starting Production Server (Gunicorn)")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Workers: {workers}")
    print()
    print("To install Gunicorn: pip install gunicorn")
    print()
    
    try:
        subprocess.run([
            sys.executable, "-m", "gunicorn",
            "fins_project.wsgi:application",
            "--bind", f"{host}:{port}",
            "--workers", str(workers),
            "--timeout", "60",
            "--access-logfile", "-",
            "--error-logfile", "-"
        ])
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure Gunicorn is installed:")
        print("  pip install gunicorn")

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Start production server')
    parser.add_argument('--host', default='0.0.0.0', help='Server host')
    parser.add_argument('--port', type=int, default=8000, help='Server port')
    parser.add_argument('--workers', type=int, default=4, help='Number of workers')
    
    args = parser.parse_args()
    start_production_server(args.host, args.port, args.workers)
