from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.test import TestCase
from django.urls import reverse

from .models import CustomerNotification


class CustomerNotificationAdminTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_superuser(
            username="admin_notifications",
            email="admin_notifications@example.com",
            password="Admin12345!",
        )
        self.customer = user_model.objects.create_user(
            username="customer_notif",
            password="Cust12345!",
        )
        self.client.force_login(self.admin_user)

        CustomerNotification.objects.create(
            user=self.customer,
            order_id=1,
            title="Order Update",
            message="Your order is being processed.",
            is_read=False,
        )

    def test_customernotification_admin_changelist_renders(self):
        response = self.client.get(
            reverse("admin:notifications_customernotification_changelist")
        )
        self.assertEqual(response.status_code, 200)

    def test_customernotification_admin_changelist_handles_queryset_db_error(self):
        with patch(
            "django.contrib.admin.options.ModelAdmin.get_queryset",
            side_effect=DatabaseError("db temporary failure"),
        ):
            response = self.client.get(
                reverse("admin:notifications_customernotification_changelist")
            )
        self.assertEqual(response.status_code, 200)
