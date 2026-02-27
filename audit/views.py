from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.permissions import is_manager

from .models import UserActionLog


@login_required
def audit_logs(request):
    if not is_manager(request.user):
        return render(request, "access_denied.html")
    logs = UserActionLog.objects.select_related("user").order_by("-timestamp")[:300]
    return render(request, "audit/logs.html", {"logs": logs})
