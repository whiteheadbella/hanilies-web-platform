from django.db import models
from django.utils import timezone
from orders.models import Booking


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=50, default="PENDING")
    date_paid = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Payment for Order #{self.booking.order.id}"
