from .permissions import is_manager


def role_flags(request):
    user = getattr(request, "user", None)
    unread_notifications_count = 0
    if user and user.is_authenticated:
        from notifications.models import CustomerNotification

        unread_notifications_count = CustomerNotification.objects.filter(
            user=user,
            is_read=False,
        ).count()

    return {
        "is_manager_user": is_manager(user) if user else False,
        "unread_notifications_count": unread_notifications_count,
    }
