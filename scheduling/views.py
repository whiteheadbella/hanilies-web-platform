from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import is_manager
from audit.services import log_user_action

from .forms import ScheduleForm
from .models import Schedule


@login_required
def schedule_list(request):
    if not is_manager(request.user):
        return render(request, "access_denied.html")

    form = ScheduleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        schedule = form.save()
        schedule.booking.status = "SCHEDULED"
        schedule.booking.save(update_fields=["status"])
        log_user_action(request.user, f"Created schedule for booking #{schedule.booking.id}")
        messages.success(request, "Schedule created.")
        return redirect("schedule_list")

    schedules = Schedule.objects.select_related("booking", "staff").order_by("date", "time")
    return render(request, "scheduling/schedule_list.html", {"form": form, "schedules": schedules})


@login_required
def schedule_delete(request, schedule_id):
    if not is_manager(request.user):
        return render(request, "access_denied.html")
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if request.method == "POST":
        schedule.delete()
        log_user_action(request.user, f"Deleted schedule #{schedule_id}")
        messages.success(request, "Schedule deleted.")
        return redirect("schedule_list")
    return render(request, "scheduling/confirm_delete_schedule.html", {"schedule": schedule})
