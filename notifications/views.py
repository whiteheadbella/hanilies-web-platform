from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import render
from django.utils.http import url_has_allowed_host_and_scheme

from .models import CustomerNotification


@login_required
def my_notifications(request):
    notifications = CustomerNotification.objects.filter(user=request.user)
    CustomerNotification.objects.filter(
        user=request.user, is_read=False).update(is_read=True)

    fallback_url = reverse("accounts_home")
    candidate_url = request.GET.get(
        "next") or request.META.get("HTTP_REFERER", "")
    if candidate_url and url_has_allowed_host_and_scheme(
        candidate_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        back_url = candidate_url
    else:
        back_url = fallback_url

    return render(
        request,
        "notifications/my_notifications.html",
        {
            "notifications": notifications,
            "back_url": back_url,
        },
    )
