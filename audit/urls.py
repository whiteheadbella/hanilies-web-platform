from django.urls import path

from .views import audit_logs, delete_audit_log

urlpatterns = [
    path("", audit_logs, name="audit_logs"),
    path("delete/<int:log_id>/", delete_audit_log, name="delete_audit_log"),
]
