from django.contrib import admin
from django.db import DatabaseError
from django.db.utils import OperationalError, ProgrammingError
from .models import (
    SeasonTag,
    CakeCategory,
    Cake,
    EventCategory,
    EventPackage,
    EventPackageItem,
    GalleryPhoto,
    AddOnCategory,
    AddOnItem
)


class SeasonTagSafeAdminMixin:
    season_tag_field_name = "season_tags"

    def _model_schema_ready(self, model):
        try:
            model._default_manager.only("pk").exists()
            return True
        except (ProgrammingError, OperationalError, DatabaseError):
            return False

    def _season_tag_schema_ready(self):
        return self._model_schema_ready(SeasonTag)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        related_model = getattr(
            getattr(db_field, "remote_field", None), "model", None)
        if related_model and hasattr(formfield, "queryset"):
            if not self._model_schema_ready(related_model):
                formfield.queryset = related_model._default_manager.none()
        return formfield

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        formfield = super().formfield_for_manytomany(db_field, request, **kwargs)
        related_model = getattr(
            getattr(db_field, "remote_field", None), "model", None)
        if related_model and hasattr(formfield, "queryset"):
            if not self._model_schema_ready(related_model):
                formfield.queryset = related_model._default_manager.none()
        return formfield

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        if (
            self.season_tag_field_name in form.base_fields
            and not self._season_tag_schema_ready()
        ):
            form.base_fields.pop(self.season_tag_field_name, None)
        return form

    def get_list_filter(self, request):
        filters = list(super().get_list_filter(request))
        if not self._season_tag_schema_ready():
            filters = [
                item
                for item in filters
                if item != self.season_tag_field_name
            ]
        return tuple(filters)


# -------------------------
# SEASON TAG ADMIN
# -------------------------
@admin.register(SeasonTag)
class SeasonTagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# -------------------------
# CAKE CATEGORY ADMIN
# -------------------------
@admin.register(CakeCategory)
class CakeCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


# -------------------------
# CAKE ADMIN
# -------------------------
@admin.register(Cake)
class CakeAdmin(SeasonTagSafeAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "category", "size", "flavor", "base_price")
    list_filter = ("category", "season_tags")
    search_fields = ("name", "flavor")
    filter_horizontal = ("season_tags",)  # ⭐ Important for ManyToMany UI


# -------------------------
# EVENT CATEGORY ADMIN
# -------------------------
@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


# -------------------------
# EVENT PACKAGE ADMIN
# -------------------------
class EventPackageItemInline(admin.TabularInline):
    model = EventPackageItem
    extra = 0
    fields = ("item_group", "item_name", "quantity",
              "unit", "unit_price", "notes")


@admin.register(EventPackage)
class EventPackageAdmin(SeasonTagSafeAdminMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "category",
        "package_set",
        "package_number",
        "name",
        "base_price",
        "is_active",
    )
    list_filter = ("category", "package_set", "is_active", "season_tags")
    search_fields = ("name", "theme_style", "description", "inclusions")
    filter_horizontal = ("season_tags",)
    inlines = [EventPackageItemInline]
    readonly_fields = ()


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "uploaded_by",
                    "is_active", "is_hero", "created_at")
    list_filter = ("is_active", "is_hero")
    search_fields = ("title",)


# -------------------------
# ADD-ON CATEGORY ADMIN
# -------------------------
@admin.register(AddOnCategory)
class AddOnCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# -------------------------
# ADD-ON ITEM ADMIN
# -------------------------
@admin.register(AddOnItem)
class AddOnItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price")
    list_filter = ("category",)
    search_fields = ("name",)
