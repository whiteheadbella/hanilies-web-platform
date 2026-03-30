from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Cake, CakeCategory

from .models import Customization


class CustomizationAdminTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Admin12345!",
        )
        self.client.force_login(self.admin_user)

        self.category = CakeCategory.objects.create(
            name="Birthday",
            description="Birthday cakes",
        )
        self.cake = Cake.objects.create(
            category=self.category,
            name="Sample Cake",
            size="MEDIUM",
            flavor="Chocolate",
            base_price=1200,
            image="cakes/sample.jpg",
        )

    def test_admin_change_page_handles_broken_reference_image_url(self):
        customization = Customization.objects.create(
            cake=self.cake,
            size="SMALL",
            layers="1",
            quantity=1,
            flavor="Vanilla",
            theme="Minimal",
            message="Happy Birthday",
            price=1500,
            reference_image="customizations/missing.jpg",
        )

        change_url = reverse(
            "admin:customization_customization_change",
            args=[customization.pk],
        )

        storage = customization.reference_image.storage
        with patch.object(storage, "url", side_effect=Exception("storage unavailable")):
            response = self.client.get(change_url)

        self.assertEqual(response.status_code, 200)
