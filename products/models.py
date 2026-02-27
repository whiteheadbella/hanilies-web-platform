from django.contrib.auth.models import User
from django.db import models

# -------------------------
# SEASON TAGS
# -------------------------


class SeasonTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# -------------------------
# ADD-ON MODULES
# -------------------------
class AddOnCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AddOnItem(models.Model):
    category = models.ForeignKey(AddOnCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(
        upload_to="addons/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.category.name} - {self.name}"


# -------------------------
# CAKE MODULES
# -------------------------
class CakeCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Cake(models.Model):
    category = models.ForeignKey(CakeCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    flavor = models.CharField(max_length=50)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='cakes/')

    season_tags = models.ManyToManyField(SeasonTag, blank=True)

    def __str__(self):
        return self.name


# -------------------------
# EVENT PACKAGES
# -------------------------
class EventCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class EventPackage(models.Model):
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="packages",
    )
    package_set = models.CharField(max_length=100, default="General Set")
    package_number = models.PositiveIntegerField(null=True, blank=True)
    name = models.CharField(max_length=100)
    theme_style = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(
        upload_to="event_packages/", blank=True, null=True)
    inclusions = models.TextField(blank=True)
    duration_hours = models.CharField(max_length=100, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    season_tags = models.ManyToManyField(SeasonTag, blank=True)

    class Meta:
        ordering = ["category__name", "package_set", "package_number", "name"]

    def __str__(self):
        if self.package_number:
            return f"{self.package_set} - Package {self.package_number}"
        return self.name


class EventPackageItem(models.Model):
    package = models.ForeignKey(
        EventPackage,
        on_delete=models.CASCADE,
        related_name="items",
    )
    item_group = models.CharField(max_length=100, default="General")
    item_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["item_group", "item_name"]

    def __str__(self):
        if self.quantity:
            suffix = f" {self.unit}".strip()
            return f"{self.item_name} ({self.quantity}{suffix})"
        return self.item_name


class GalleryPhoto(models.Model):
    title = models.CharField(max_length=120)
    image = models.ImageField(upload_to="gallery/", blank=True, null=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_hero = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_hero:
            type(self).objects.filter(is_hero=True).exclude(
                pk=self.pk).update(is_hero=False)

    def __str__(self):
        return self.title
