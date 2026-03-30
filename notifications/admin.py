from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import CustomerNotification, UserActionLog


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


@admin.register(UserActionLog)
class UserActionLogAdmin(SafeQueryAdminMixin, admin.ModelAdmin):
    list_display = ("id", "user", "action", "timestamp")
    search_fields = ("user__username", "action")
    list_filter = ("timestamp",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            user_model = get_user_model()
            kwargs.setdefault("queryset", user_model.objects.order_by("username"))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(CustomerNotification)
class CustomerNotificationAdmin(SafeQueryAdminMixin, admin.ModelAdmin):
    list_display = ("id", "user", "title", "order_id", "is_read", "created_at")
    search_fields = ("user__username", "title", "message", "order_id")
    list_filter = ("is_read", "created_at")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            user_model = get_user_model()
            kwargs.setdefault("queryset", user_model.objects.order_by("username"))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
