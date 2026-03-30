from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.test import TestCase
from django.urls import reverse

from .models import DeliveryProfile


class DeliveryProfileAdminTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_superuser(
            username="admin_accounts",
            email="admin_accounts@example.com",
            password="Admin12345!",
        )
        self.customer = user_model.objects.create_user(
            username="customer1",
            password="Cust12345!",
        )
        self.client.force_login(self.admin_user)

        DeliveryProfile.objects.create(
            user=self.customer,
            full_name="Customer One",
            phone="09123456789",
            house_no="12",
            street="Main Street",
            barangay="Barangay 1",
            city="City A",
            province="Province A",
            is_default=True,
        )

    def test_deliveryprofile_admin_changelist_renders(self):
        response = self.client.get(reverse("admin:accounts_deliveryprofile_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_deliveryprofile_admin_changelist_handles_queryset_db_error(self):
        with patch(
            "django.contrib.admin.options.ModelAdmin.get_queryset",
            side_effect=DatabaseError("db temporary failure"),
        ):
            response = self.client.get(reverse("admin:accounts_deliveryprofile_changelist"))
        self.assertEqual(response.status_code, 200)
