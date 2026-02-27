from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import EventCategory, EventPackage


def infer_category_name(package):
    text = f"{package.package_set} {package.name}".lower()
    if "christening" in text:
        return "Christening"
    if "wedding" in text:
        return "Wedding"
    if "sweet corner" in text:
        return "Sweet Corner"
    if "birthday" in text:
        return "Birthday"
    return "Uncategorized"


class Command(BaseCommand):
    help = "One-time cleanup: permanently assign event package categories and deactivate duplicate records."

    @transaction.atomic
    def handle(self, *args, **options):
        category_cache = {c.name: c for c in EventCategory.objects.all()}

        def get_category(name):
            if name in category_cache:
                return category_cache[name]
            category = EventCategory.objects.create(name=name, description=f"Auto-assigned category: {name}")
            category_cache[name] = category
            return category

        # 1) Permanently assign categories where missing/misaligned.
        assigned_count = 0
        packages = list(EventPackage.objects.select_related("category").all().order_by("-id"))
        for package in packages:
            inferred_name = infer_category_name(package)
            inferred_category = get_category(inferred_name)
            current_name = package.category.name if package.category else None
            if current_name != inferred_name:
                package.category = inferred_category
                package.save(update_fields=["category"])
                assigned_count += 1

        # 2) Deactivate duplicates within the same logical package key.
        # Keep the most recent (highest id) active.
        duplicate_groups = defaultdict(list)
        refreshed = list(EventPackage.objects.select_related("category").all().order_by("-id"))
        for package in refreshed:
            number_or_name = package.package_number if package.package_number is not None else package.name
            key = (package.category.name if package.category else "Uncategorized", package.package_set, number_or_name)
            duplicate_groups[key].append(package)

        deactivated_count = 0
        for key, rows in duplicate_groups.items():
            if len(rows) <= 1:
                continue
            keeper = rows[0]  # newest due -id ordering
            if not keeper.is_active:
                keeper.is_active = True
                keeper.save(update_fields=["is_active"])
            for dup in rows[1:]:
                if dup.is_active:
                    dup.is_active = False
                    dup.save(update_fields=["is_active"])
                    deactivated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Cleanup done. Categories assigned/updated: {assigned_count}. Duplicates deactivated: {deactivated_count}."
            )
        )
