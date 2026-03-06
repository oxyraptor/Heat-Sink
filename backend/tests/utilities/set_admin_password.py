"""
Admin user password management utility
"""

import os
import sys
import django

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fins_project.settings')
django.setup()

from django.contrib.auth import get_user_model


def set_admin_password(username='admin', password='admin123'):
    """Set or reset admin user password"""
    User = get_user_model()
    
    try:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"✓ Password set successfully")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        return True
    except User.DoesNotExist:
        print(f"✗ User '{username}' not found")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    print("Admin Password Management Utility")
    print("=" * 60)
    set_admin_password()
    print("=" * 60)
