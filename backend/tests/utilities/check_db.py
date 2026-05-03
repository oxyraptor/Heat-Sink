"""
Database inspection utility
Displays all tables and their structure in the Django database
"""

import os
import sys
import django
import sqlite3

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fins_project.settings')
django.setup()

from django.conf import settings


def inspect_database():
    """Inspect database tables and structure"""
    db_path = settings.DATABASES['default']['NAME']
    
    if not os.path.exists(db_path):
        print(f"✗ Database not found: {db_path}")
        return
    
    print(f"Database: {db_path}")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\nTables ({len(tables)}):")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  ✓ {table:<40} ({count} rows)")
    
    conn.close()


if __name__ == "__main__":
    print("Database Inspection Utility")
    print("=" * 60)
    inspect_database()
    print("=" * 60)
