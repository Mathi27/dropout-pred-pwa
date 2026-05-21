import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.users.models import User, UserRole
from rest_framework.test import APIClient

client = APIClient()

# Create a receptionist user
user, created = User.objects.get_or_create(email="receptionist@test.com", defaults={"role": UserRole.RECEPTIONIST, "first_name": "Test", "last_name": "Receptionist"})
if created:
    user.set_password("password123")
    user.save()

# Try logging in
response = client.post("/api/v1/auth/login/", {"email": "receptionist@test.com", "password": "password123"})
print("Status Code:", response.status_code)
print("Response Body:", response.json())
