from django.conf import settings
from django.core.mail import send_mail

from .models import CustomerNotification


def notify_order_update(user, order, message):
    title = f"Order #{order.id} Update"
    CustomerNotification.objects.create(
        user=user,
        order_id=order.id,
        title=title,
        message=message,
    )

    if user.email:
        send_mail(
            subject=title,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@hanilies.local"),
            recipient_list=[user.email],
            fail_silently=True,
        )
