import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Success: Superuser created. Username: admin | Password: admin123")
    else:
        print("Superuser 'admin' already exists.")

if __name__ == '__main__':
    create_admin()
