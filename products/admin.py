from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.core.exceptions import FieldDoesNotExist
from django.db import DatabaseError
from django.db.utils import OperationalError, ProgrammingError

from .models import (
    AddOnCategory,
    AddOnItem,
    Cake,
    CakeCategory,
    EventCategory,
    EventPackage,
    EventPackageItem,
    GalleryPhoto,
    SeasonTag,
)


class SeasonTagSafeAdminMixin:
    """Hide season tag controls when related DB tables are not ready."""

    season_tag_field_name = "season_tags"

    def _model_schema_ready(self, model):
        try:
            model._default_manager.only("pk").exists()
            return True
        except (ProgrammingError, OperationalError, DatabaseError):
            return False

    def _season_tag_schema_ready(self):
        if not self._model_schema_ready(SeasonTag):
            return False

        try:
            season_tag_field = self.model._meta.get_field(self.season_tag_field_name)
        except FieldDoesNotExist:
            return False

        through_model = getattr(
            getattr(season_tag_field, "remote_field", None), "through", None
        )
        if through_model and not self._model_schema_ready(through_model):
            return False
        return True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        related_model = getattr(getattr(db_field, "remote_field", None), "model", None)
        if related_model and hasattr(formfield, "queryset"):
            if not self._model_schema_ready(related_model):
                formfield.queryset = related_model._default_manager.none()
        return formfield

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        formfield = super().formfield_for_manytomany(db_field, request, **kwargs)
        related_model = getattr(getattr(db_field, "remote_field", None), "model", None)
        if related_model and hasattr(formfield, "queryset"):
            if not self._model_schema_ready(related_model):
                formfield.queryset = related_model._default_manager.none()

        through_model = getattr(getattr(db_field, "remote_field", None), "through", None)
        if (
            through_model
            and related_model
            and hasattr(formfield, "queryset")
            and not self._model_schema_ready(through_model)
        ):
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
                item for item in filters if item != self.season_tag_field_name
            ]
        return tuple(filters)

    def get_filter_horizontal(self, request, obj=None):
        fields = list(getattr(self, "filter_horizontal", ()) or ())
        if not self._season_tag_schema_ready():
            fields = [item for item in fields if item != self.season_tag_field_name]
        return tuple(fields)


class SafeAdminFileWidget(AdminFileWidget):
    """Avoid rendering broken existing-file links in admin forms."""

    def is_initial(self, value):
        if not value:
            return False
        try:
            _ = value.url
        except Exception:
            return False
        return super().is_initial(value)


class SafeAdminMediaWidgetMixin:
    """Swap default admin file widgets with a safer widget."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if (
            formfield
            and getattr(formfield, "widget", None)
            and isinstance(formfield.widget, AdminFileWidget)
        ):
            widget_attrs = getattr(formfield.widget, "attrs", None)
            formfield.widget = SafeAdminFileWidget(attrs=widget_attrs)
        return formfield


@admin.register(SeasonTag)
class SeasonTagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(CakeCategory)
class CakeCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


@admin.register(Cake)
class CakeAdmin(
    SafeAdminMediaWidgetMixin,
    SeasonTagSafeAdminMixin,
    admin.ModelAdmin,
):
    list_display = ("id", "name", "category", "size", "flavor", "base_price")
    list_filter = ("category", "season_tags")
    search_fields = ("name", "flavor")
    filter_horizontal = ("season_tags",)  # Important for ManyToMany UI.


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


class EventPackageItemInline(admin.TabularInline):
    model = EventPackageItem
    extra = 0
    fields = ("item_group", "item_name", "quantity", "unit", "unit_price", "notes")


@admin.register(EventPackage)
class EventPackageAdmin(
    SafeAdminMediaWidgetMixin,
    SeasonTagSafeAdminMixin,
    admin.ModelAdmin,
):
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
class GalleryPhotoAdmin(SafeAdminMediaWidgetMixin, admin.ModelAdmin):
    list_display = ("id", "title", "uploaded_by", "is_active", "is_hero", "created_at")
    list_filter = ("is_active", "is_hero")
    search_fields = ("title",)


@admin.register(AddOnCategory)
class AddOnCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(AddOnItem)
class AddOnItemAdmin(SafeAdminMediaWidgetMixin, admin.ModelAdmin):
    list_display = ("id", "name", "category", "price")
    list_filter = ("category",)
    search_fields = ("name",)
