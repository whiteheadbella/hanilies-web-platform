from django.db import migrations, models


def set_initial_hero_photo(apps, schema_editor):
    GalleryPhoto = apps.get_model("products", "GalleryPhoto")
    existing_hero = GalleryPhoto.objects.filter(is_hero=True).exists()
    if existing_hero:
        return

    first_photo = (
        GalleryPhoto.objects.filter(is_active=True)
        .exclude(image="")
        .exclude(image__isnull=True)
        .order_by("-created_at")
        .first()
    )
    if first_photo:
        first_photo.is_hero = True
        first_photo.save(update_fields=["is_hero"])


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0010_eventpackageitem_unit_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="galleryphoto",
            name="is_hero",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_initial_hero_photo,
                             migrations.RunPython.noop),
    ]
