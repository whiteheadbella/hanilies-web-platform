from pathlib import Path

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from customization.models import Customization
from products.models import AddOnItem, Cake, EventPackage, GalleryPhoto


class Command(BaseCommand):
    help = "Upload existing local media files to Cloudinary and update DB paths."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be migrated without writing changes.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if not getattr(settings, "USE_CLOUDINARY_MEDIA", False):
            raise CommandError(
                "Cloudinary media is not enabled. Set CLOUDINARY_CLOUD_NAME, "
                "CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET first."
            )

        targets = [
            (AddOnItem, "image"),
            (Cake, "image"),
            (EventPackage, "image"),
            (GalleryPhoto, "image"),
            (Customization, "reference_image"),
        ]

        scanned = 0
        migrated = 0
        missing = 0
        failed = 0

        self.stdout.write(self.style.NOTICE(
            "Starting media migration to Cloudinary..."))
        if dry_run:
            self.stdout.write(self.style.WARNING(
                "Dry-run mode enabled. No DB writes will be made."))

        for model, field_name in targets:
            queryset = model.objects.exclude(
                **{field_name: ""}).filter(**{f"{field_name}__isnull": False})
            total = queryset.count()
            if total == 0:
                continue

            self.stdout.write(
                f"Processing {model.__name__}.{field_name} ({total} records)")

            for obj in queryset.iterator():
                scanned += 1
                file_field = getattr(obj, field_name)

                if not file_field or not file_field.name:
                    continue

                try:
                    source_path = Path(settings.MEDIA_ROOT) / file_field.name
                    if not source_path.exists() or not source_path.is_file():
                        missing += 1
                        continue

                    if dry_run:
                        migrated += 1
                        continue

                    with source_path.open("rb") as source:
                        new_name = default_storage.save(
                            file_field.name, File(source))

                    if new_name != file_field.name:
                        setattr(obj, field_name, new_name)

                    with transaction.atomic():
                        obj.save(update_fields=[field_name])

                    migrated += 1
                except Exception as exc:
                    failed += 1
                    self.stderr.write(
                        self.style.ERROR(
                            f"Failed {model.__name__}(id={obj.pk}) {field_name}: {exc}"
                        )
                    )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Migration scan complete."))
        self.stdout.write(f"Scanned: {scanned}")
        self.stdout.write(f"Migrated: {migrated}")
        self.stdout.write(f"Missing source files: {missing}")
        self.stdout.write(f"Failed: {failed}")

        if missing > 0:
            self.stdout.write(
                self.style.WARNING(
                    "Some DB records point to files not found under MEDIA_ROOT. "
                    "Re-upload those images manually."
                )
            )
