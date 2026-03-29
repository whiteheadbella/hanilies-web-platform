from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import is_manager

from .models import UserActionLog
from .services import log_user_action


@login_required
def audit_logs(request):
    if not is_manager(request.user):
        return render(request, "access_denied.html")
    logs = UserActionLog.objects.select_related(
        "user").order_by("-timestamp")[:300]
    return render(request, "audit/logs.html", {"logs": logs})


@login_required
def delete_audit_log(request, log_id):
    if not is_manager(request.user):
        return render(request, "access_denied.html")
    if request.method != "POST":
        return redirect("audit_logs")

    log = get_object_or_404(UserActionLog, id=log_id)
    deleted_summary = f"{log.user.username}: {log.action}"
    log.delete()

    log_user_action(
        request.user,
        f"Deleted audit log #{log_id} ({deleted_summary})",
    )
    messages.success(request, "Audit log deleted.")
    return redirect("audit_logs")
