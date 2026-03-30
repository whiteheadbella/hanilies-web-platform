from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.db.utils import OperationalError, ProgrammingError
from .models import DeliveryProfile

# Register your models here.
admin.site.site_header = "Hanilies Cakeshoppe Administration"
admin.site.site_title = "Hanilies Cakeshoppe Admin"
admin.site.index_title = "Welcome to Hanilies Cakeshoppe Management System"


class SafeQueryAdminMixin:
    """Prevent admin pages from crashing when DB relations are temporarily broken."""

    def get_queryset(self, request):
        try:
            return super().get_queryset(request)
        except Exception:
            return self.model._default_manager.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        related_model = getattr(getattr(db_field, "remote_field", None), "model", None)
        try:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        except Exception:
            if related_model:
                kwargs.setdefault("queryset", related_model._default_manager.none())
            try:
                return db_field.formfield(**kwargs)
            except Exception:
                return None


@admin.register(DeliveryProfile)
class DeliveryProfileAdmin(SafeQueryAdminMixin, admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "city", "is_default", "created_at")
    list_filter = ("is_default", "city", "province")
    search_fields = ("full_name", "phone", "city", "user__username")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            user_model = get_user_model()
            kwargs.setdefault("queryset", user_model.objects.order_by("username"))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SafeGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("permissions",)

    def _permissions_schema_ready(self):
        try:
            Permission.objects.only("id").exists()
            return True
        except (ProgrammingError, OperationalError, DatabaseError):
            return False

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        if "permissions" in form.base_fields and not self._permissions_schema_ready():
            form.base_fields.pop("permissions", None)
        return form

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if self._permissions_schema_ready():
            return fieldsets
        sanitized = []
        for title, options in fieldsets:
            fields = options.get("fields", ())
            filtered_fields = tuple(
                field for field in fields if field != "permissions")
            new_options = dict(options)
            new_options["fields"] = filtered_fields
            sanitized.append((title, new_options))
        return sanitized


try:
    admin.site.unregister(Group)
except NotRegistered:
    pass

admin.site.register(Group, SafeGroupAdmin)
