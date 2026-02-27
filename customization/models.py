from django.db import models
from products.models import Cake, AddOnItem

class Customization(models.Model):
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)

    SIZE_CHOICES = [
        ("SMALL", "Small"),
        ("MEDIUM", "Medium"),
        ("LARGE", "Large"),
    ]

    LAYER_CHOICES = [
        ("1", "1 Layer"),
        ("2", "2 Layers"),
        ("3", "3 Layers"),
    ]

    size = models.CharField(max_length=50, choices=SIZE_CHOICES)
    layers = models.CharField(max_length=10, choices=LAYER_CHOICES, default="1")

    quantity = models.PositiveIntegerField(default=1)  # NEW

    flavor = models.CharField(max_length=50)
    theme = models.CharField(max_length=100)
    message = models.TextField()

    # Proper relational design (VERY IMPORTANT)
    add_ons = models.ManyToManyField(AddOnItem, blank=True)

    reference_image = models.ImageField(
        upload_to="customizations/",
        blank=True,
        null=True
    )

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customization for {self.cake.name}"