from .permissions import is_manager


def role_flags(request):
    user = getattr(request, "user", None)
    is_manager_user = False
    unread_notifications_count = 0

    if user and user.is_authenticated:
        try:
            is_manager_user = is_manager(user)
        except Exception:
            is_manager_user = bool(
                getattr(user, "is_superuser", False)
                or getattr(user, "is_staff", False)
            )

        try:
            from notifications.models import CustomerNotification

            unread_notifications_count = CustomerNotification.objects.filter(
                user=user,
                is_read=False,
            ).count()
        except Exception:
            unread_notifications_count = 0

    return {
        "is_manager_user": is_manager_user,
        "unread_notifications_count": unread_notifications_count,
    }
