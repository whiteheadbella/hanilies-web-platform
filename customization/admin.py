from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from .models import Customization


class SafeAdminFileWidget(AdminFileWidget):
    """Avoid crashing admin pages when an existing file URL is unavailable."""

    def is_initial(self, value):
        if not value:
            return False
        try:
            _ = value.url
        except Exception:
            return False
        return super().is_initial(value)


@admin.register(Customization)
class CustomizationAdmin(admin.ModelAdmin):
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
