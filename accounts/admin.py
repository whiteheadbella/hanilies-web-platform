from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.models import Group, Permission
from django.db import DatabaseError
from django.db.utils import OperationalError, ProgrammingError
from .models import DeliveryProfile

# Register your models here.
admin.site.site_header = "Hanilies Cakeshoppe Administration"
admin.site.site_title = "Hanilies Cakeshoppe Admin"
admin.site.index_title = "Welcome to Hanilies Cakeshoppe Management System"
admin.site.register(DeliveryProfile)


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
