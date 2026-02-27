from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from audit.services import log_user_action
from notifications.services import notify_order_update
from orders.models import Booking

from .forms import PaymentForm
from .models import Payment


@login_required
def create_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.order.customer != request.user:
        return render(request, "access_denied.html")
    if booking.order.status != "PENDING":
        messages.info(request, "This order is no longer pending payment.")
        return redirect("my_orders")

    form = PaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        payment = form.save(commit=False)
        payment.booking = booking
        payment.amount = booking.order.total_amount
        payment.payment_status = "PAID"
        payment.date_paid = timezone.now()
        payment.save()

        booking.order.status = "CONFIRMED"
        booking.order.save(update_fields=["status"])
        booking.status = "CONFIRMED"
        booking.save(update_fields=["status"])

        log_user_action(request.user, f"Paid order #{booking.order.id}")
        notify_order_update(
            user=request.user,
            order=booking.order,
            message=f"Payment received for Order #{booking.order.id}. Status is now CONFIRMED.",
        )
        if request.session.get("checkout_confirmed_booking_id") == booking.id:
            request.session.pop("checkout_confirmed_booking_id", None)
        messages.success(request, "Payment successful.")
        return redirect("my_orders")

    return render(request, "payments/create_payment.html", {"form": form, "booking": booking})


@login_required
def my_payments(request):
    payments = Payment.objects.select_related("booking", "booking__order").filter(
        booking__order__customer=request.user
    )
    return render(request, "payments/my_payments.html", {"payments": payments})
