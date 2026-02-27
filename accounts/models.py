from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class DeliveryProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="delivery_profiles")

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    house_no = models.CharField(max_length=50)
    street = models.CharField(max_length=150)
    barangay = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    province = models.CharField(max_length=150)

    landmark = models.CharField(max_length=200, blank=True)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        # ✅ Enforce single default per user (application level)
        if self.is_default:
            DeliveryProfile.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)

        super().save(*args, **kwargs)

    # ✅ DATABASE-LEVEL ENFORCEMENT (Enterprise-grade)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(is_default=True),
                name="unique_default_per_user"
            )
        ]

    def __str__(self):
        return f"{self.full_name} - {self.city}"