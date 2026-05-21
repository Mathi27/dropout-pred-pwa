from django.test import TestCase

from apps.users.models import User, UserRole
from apps.users.serializers import RegisterSerializer


class RegisterSerializerTests(TestCase):
    def test_valid_patient_payload(self):
        serializer = RegisterSerializer(
            data={
                "email": "patient@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "Pat",
                "last_name": "Ent",
                "phone": "9999999999",
                "role": UserRole.PATIENT,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.role, UserRole.PATIENT)
        self.assertTrue(user.check_password("SecurePass123!"))

    def test_password_errors_map_to_password_field(self):
        serializer = RegisterSerializer(
            data={
                "email": "weak@example.com",
                "password": "password",
                "password_confirm": "password",
                "role": UserRole.PATIENT,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)
        self.assertNotIn("non_field_errors", serializer.errors)

    def test_password_confirm_mismatch(self):
        serializer = RegisterSerializer(
            data={
                "email": "mismatch@example.com",
                "password": "SecurePass123!",
                "password_confirm": "Different123!",
                "role": UserRole.PATIENT,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    def test_admin_role_rejected(self):
        serializer = RegisterSerializer(
            data={
                "email": "admin@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "role": UserRole.ADMIN,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("role", serializer.errors)

    def test_email_normalized(self):
        serializer = RegisterSerializer(
            data={
                "email": "  MixedCase@Example.COM  ",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, "mixedcase@example.com")

    def test_duplicate_email(self):
        User.objects.create_user(
            email="exists@example.com",
            password="SecurePass123!",
            role=UserRole.PATIENT,
        )
        serializer = RegisterSerializer(
            data={
                "email": "exists@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
