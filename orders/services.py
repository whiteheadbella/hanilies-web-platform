from datetime import timedelta

from django.utils import timezone

from audit.services import log_user_action
from notifications.services import notify_order_update

from .models import Order


AUTO_CANCEL_HOURS = 8


def auto_cancel_stale_orders():
    cutoff = timezone.now() - timedelta(hours=AUTO_CANCEL_HOURS)
    stale_orders = Order.objects.filter(status="PENDING", last_customer_activity__lt=cutoff)
    count = 0
    for order in stale_orders:
        order.status = "CANCELLED"
        order.cancelled_at = timezone.now()
        order.save(update_fields=["status", "cancelled_at"])
        log_user_action(order.customer, f"Order #{order.id} auto-cancelled after {AUTO_CANCEL_HOURS} hours inactivity")
        notify_order_update(
            user=order.customer,
            order=order,
            message=f"Order #{order.id} was automatically cancelled after {AUTO_CANCEL_HOURS} hours of inactivity.",
        )
        count += 1
    return count
