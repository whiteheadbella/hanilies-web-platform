from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import CustomerNotification


@login_required
def my_notifications(request):
    notifications = CustomerNotification.objects.filter(user=request.user)
    CustomerNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, "notifications/my_notifications.html", {"notifications": notifications})
