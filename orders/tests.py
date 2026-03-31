from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import DeliveryProfile
from products.models import EventCategory, EventPackage

from .models import Booking, CartItem


class CheckoutFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="customer1",
            email="customer1@example.com",
            password="pass12345",
        )
        self.category = EventCategory.objects.create(name="Birthday")
        self.package = EventPackage.objects.create(
            category=self.category,
            package_set="General Set",
            package_number=1,
            name="Birthday Basic",
            theme_style="Pastel",
            description="Basic package",
            base_price=Decimal("1500.00"),
            is_active=True,
        )

    def _create_profile(self, **overrides):
        data = {
            "user": self.user,
            "full_name": "Juan Dela Cruz",
            "phone": "09170000000",
            "house_no": "12",
            "street": "Mabini St",
            "barangay": "San Isidro",
            "city": "Pasig",
            "province": "Metro Manila",
            "landmark": "Near church",
            "is_default": False,
        }
        data.update(overrides)
        return DeliveryProfile.objects.create(**data)

    def test_checkout_prefills_event_date_from_package_inquiry(self):
        self.client.force_login(self.user)
        self._create_profile(is_default=True)
        CartItem.objects.create(
            customer=self.user,
            package=self.package,
            quantity=1,
            unit_price=self.package.base_price,
        )

        target_date = timezone.localdate() + timedelta(days=10)
        session = self.client.session
        session["event_package_inquiry"] = {
            "name": "Juan Dela Cruz",
            "email": "customer1@example.com",
            "phone": "09170000000",
            "celebration_type": "Birthday",
            "celebration_date": target_date.isoformat(),
        }
        session.save()

        response = self.client.get(reverse("checkout_cart"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["booking_prefilled"])
        self.assertEqual(
            response.context["form"].initial.get("event_date"),
            target_date.isoformat(),
        )

    def test_checkout_prefills_delivery_address_from_saved_profile(self):
        self.client.force_login(self.user)
        self._create_profile(
            house_no="12",
            street="Mabini St",
            barangay="San Isidro",
            city="Pasig",
            province="Metro Manila",
            is_default=True,
        )
        CartItem.objects.create(
            customer=self.user,
            package=self.package,
            quantity=1,
            unit_price=self.package.base_price,
        )

        response = self.client.get(reverse("checkout_cart"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].delivery_address_autofilled)
        self.assertEqual(
            response.context["form"].initial.get("delivery_address"),
            "12, Mabini St, San Isidro, Pasig, Metro Manila",
        )

    def test_checkout_uses_manual_delivery_address_with_saved_contact_snapshot(self):
        self.client.force_login(self.user)
        self._create_profile(
            full_name="Maria Santos",
            phone="09171112222",
            house_no="88",
            street="Rizal Ave",
            barangay="Poblacion",
            city="Marikina",
            province="Metro Manila",
            landmark="City Hall",
            is_default=True,
        )
        CartItem.objects.create(
            customer=self.user,
            package=self.package,
            quantity=1,
            unit_price=self.package.base_price,
        )

        event_date = timezone.localdate() + timedelta(days=7)
        response = self.client.post(
            reverse("checkout_cart"),
            {
                "event_date": event_date.isoformat(),
                "event_time": "13:30",
                "venue": "Client Venue",
                "delivery_address": "Unit 5, Sunset Homes, Marikina, Metro Manila",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        booking = Booking.objects.select_related("order").latest("id")
        self.assertEqual(booking.delivery_full_name, "Maria Santos")
        self.assertEqual(booking.delivery_phone, "09171112222")
        self.assertEqual(
            booking.delivery_address,
            "Unit 5, Sunset Homes, Marikina, Metro Manila",
        )
