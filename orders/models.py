from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from products.models import AddOnItem, Cake, EventPackage
from customization.models import Customization


class Order(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)

    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='PENDING')
    last_customer_activity = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id}"


class OrderDetail(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    cake = models.ForeignKey(
        Cake, on_delete=models.SET_NULL, null=True, blank=True)
    package = models.ForeignKey(
        EventPackage, on_delete=models.SET_NULL, null=True, blank=True)
    customization = models.ForeignKey(
        Customization, on_delete=models.SET_NULL, null=True, blank=True)
    package_inclusion_snapshot = models.JSONField(default=list, blank=True)

    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.order.id} Item"


class Booking(models.Model):

    order = models.OneToOneField(Order, on_delete=models.CASCADE)

    event_date = models.DateField()
    event_time = models.TimeField()
    venue = models.CharField(max_length=200)
    status = models.CharField(max_length=50)

    # ✅ Delivery Snapshot (VERY IMPORTANT)
    delivery_full_name = models.CharField(max_length=100)
    delivery_phone = models.CharField(max_length=20)
    delivery_address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        min_allowed = timezone.localdate() + timedelta(days=3)
        if self.event_date and self.event_date < min_allowed:
            raise ValidationError(
                {"event_date": "Event date must be at least 3 days from today."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking for Order #{self.order.id}"


class CartItem(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cart_items")
    cake = models.ForeignKey(
        Cake, on_delete=models.SET_NULL, null=True, blank=True)
    package = models.ForeignKey(
        EventPackage, on_delete=models.SET_NULL, null=True, blank=True)
    customization = models.ForeignKey(
        Customization, on_delete=models.SET_NULL, null=True, blank=True)
    package_add_ons = models.ManyToManyField(
        AddOnItem, blank=True, related_name="cart_items")
    package_inclusion_snapshot = models.JSONField(default=list, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"CartItem #{self.id} ({self.customer.username})"
