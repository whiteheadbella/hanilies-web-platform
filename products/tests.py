from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.test import TestCase
from django.urls import reverse

from .models import CakeCategory


class CakeAdminResilienceTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_superuser(
            username="admin_products",
            email="admin_products@example.com",
            password="Admin12345!",
        )
        self.client.force_login(self.admin_user)
        self.category = CakeCategory.objects.create(
            name="Classic",
            description="Classic cakes",
        )

    def test_cake_add_page_renders(self):
        response = self.client.get(reverse("admin:products_cake_add"))
        self.assertEqual(response.status_code, 200)

    def test_cake_add_page_handles_foreignkey_formfield_errors(self):
        with patch(
            "django.contrib.admin.options.ModelAdmin.formfield_for_foreignkey",
            side_effect=DatabaseError("db temporary failure"),
        ):
            response = self.client.get(reverse("admin:products_cake_add"))
        self.assertEqual(response.status_code, 200)

    def test_cake_add_page_handles_manytomany_formfield_errors(self):
        with patch(
            "django.contrib.admin.options.ModelAdmin.formfield_for_manytomany",
            side_effect=DatabaseError("db temporary failure"),
        ):
            response = self.client.get(reverse("admin:products_cake_add"))
        self.assertEqual(response.status_code, 200)
