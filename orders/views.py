from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.permissions import is_manager
from audit.services import log_user_action
from notifications.models import CustomerNotification
from notifications.services import notify_order_update
from payments.models import Payment
from products.models import EventPackage
from scheduling.models import Schedule

from .forms import BookingForm
from .models import Booking, CartItem, Order, OrderDetail
from .services import auto_cancel_stale_orders


@login_required
def checkout_from_customization(request, customization_id):
    from customization.models import Customization

    customization = get_object_or_404(Customization, id=customization_id)

    form = BookingForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        profile = form.cleaned_data["delivery_profile"]
        order = Order.objects.create(
            customer=request.user,
            total_amount=Decimal(customization.price),
            status="PENDING",
            last_customer_activity=timezone.now(),
        )

        OrderDetail.objects.create(
            order=order,
            customization=customization,
            quantity=customization.quantity,
            price=Decimal(customization.price),
        )

        booking = form.save(commit=False)
        booking.order = order
        booking.status = "PENDING"
        booking.delivery_full_name = profile.full_name
        booking.delivery_phone = profile.phone
        booking.delivery_address = (
            f"{profile.house_no}, {profile.street}, {profile.barangay}, "
            f"{profile.city}, {profile.province}"
        )
        booking.save()

        log_user_action(
            request.user, f"Created order #{order.id} from customization")
        messages.success(
            request, f"Order #{order.id} created. Please proceed to payment.")
        return redirect("payment_create", booking_id=booking.id)

    return render(
        request,
        "orders/checkout.html",
        {"form": form, "customization": customization},
    )


def _cart_total(items):
    return sum((item.unit_price * item.quantity for item in items), Decimal("0.00"))


@login_required
def add_package_to_cart(request, package_id):
    package = get_object_or_404(EventPackage, id=package_id, is_active=True)

    if request.method == "POST":
        try:
            quantity = max(1, int(request.POST.get("quantity", "1")))
        except ValueError:
            quantity = 1

        selected_item_ids = request.POST.getlist("selected_items")
        selected_items = package.items.filter(id__in=selected_item_ids)
        if not selected_item_ids:
            selected_items = package.items.all()

        inclusion_snapshot = []
        inclusion_extra_total = Decimal("0.00")
        for package_item in selected_items:
            default_qty = package_item.quantity or 1
            qty_raw = request.POST.get(
                f"inclusion_qty_{package_item.id}", str(default_qty))
            try:
                inclusion_qty = max(1, int(qty_raw))
            except ValueError:
                inclusion_qty = default_qty

            item_unit_price = Decimal(package_item.unit_price or 0)
            item_line_total = item_unit_price * inclusion_qty
            inclusion_extra_total += item_line_total

            inclusion_snapshot.append(
                {
                    "item_id": package_item.id,
                    "item_name": package_item.item_name,
                    "item_group": package_item.item_group,
                    "unit": package_item.unit,
                    "quantity": inclusion_qty,
                    "unit_price": str(item_unit_price),
                    "line_total": str(item_line_total),
                }
            )

        unit_price = Decimal(package.base_price) + inclusion_extra_total

        item = CartItem.objects.create(
            customer=request.user,
            package=package,
            quantity=quantity,
            unit_price=unit_price,
            package_inclusion_snapshot=inclusion_snapshot,
        )

        log_user_action(request.user, f"Added package #{package.id} to cart")
        messages.success(request, f"{package.name} added to cart.")

        if request.POST.get("submit_action") == "order_now":
            return redirect("checkout_cart")

        next_url = request.POST.get("next") or request.GET.get("next")
        if next_url:
            return redirect(next_url)
        return redirect("cart_view")

    item = CartItem.objects.filter(
        customer=request.user, package=package, customization__isnull=True, cake__isnull=True
    ).first()
    if item:
        item.quantity = F("quantity") + 1
        item.save(update_fields=["quantity"])
        item.refresh_from_db()
    else:
        item = CartItem.objects.create(
            customer=request.user,
            package=package,
            quantity=1,
            unit_price=package.base_price,
        )
    log_user_action(request.user, f"Added package #{package.id} to cart")
    messages.success(request, f"{package.name} added to cart.")
    next_url = request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("cart_view")


@login_required
def add_customization_to_cart(request, customization_id):
    from customization.models import Customization

    customization = get_object_or_404(Customization, id=customization_id)
    item = CartItem.objects.filter(
        customer=request.user, customization=customization).first()
    if item:
        messages.info(request, "This customization is already in your cart.")
    else:
        CartItem.objects.create(
            customer=request.user,
            customization=customization,
            quantity=1,
            unit_price=customization.price,
        )
        messages.success(request, "Customization added to cart.")
    return redirect("cart_view")


@login_required
def cart_view(request):
    items = CartItem.objects.filter(customer=request.user).select_related(
        "package", "customization", "customization__cake", "cake"
    ).prefetch_related("package__items", "customization__add_ons", "package_add_ons")
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        action = request.POST.get("action")
        item = get_object_or_404(CartItem, id=item_id, customer=request.user)
        if action == "delete":
            item.delete()
            messages.success(request, "Item removed from cart.")
        elif action == "update":
            try:
                qty = max(1, int(request.POST.get("quantity", "1")))
            except ValueError:
                qty = 1
            item.quantity = qty
            item.save(update_fields=["quantity"])
            messages.success(request, "Cart updated.")
        return redirect("cart_view")

    total = _cart_total(items)
    return render(request, "orders/cart.html", {"items": items, "total": total})


@login_required
def checkout_cart(request):
    confirmed_booking_id = request.session.get("checkout_confirmed_booking_id")
    confirmed_booking = None
    if confirmed_booking_id:
        confirmed_booking = Booking.objects.select_related("order").filter(
            id=confirmed_booking_id,
            order__customer=request.user,
            order__status="PENDING",
        ).first()
        if not confirmed_booking:
            request.session.pop("checkout_confirmed_booking_id", None)

    items = list(
        CartItem.objects.filter(customer=request.user)
        .select_related("package", "customization", "customization__cake", "cake")
        .prefetch_related("package__items", "customization__add_ons", "package_add_ons")
    )

    if items and confirmed_booking:
        request.session.pop("checkout_confirmed_booking_id", None)
        confirmed_booking = None

    if not items and not confirmed_booking:
        messages.info(request, "Your cart is empty.")
        return redirect("cart_view")

    form = BookingForm(request.POST or None, user=request.user)
    total = _cart_total(items)
    if request.method == "POST":
        if confirmed_booking:
            messages.info(
                request, "Order already confirmed. Click Pay Now to continue.")
            return redirect("checkout_cart")

        if form.is_valid():
            profile = form.cleaned_data["delivery_profile"]
            order = Order.objects.create(
                customer=request.user,
                total_amount=total,
                status="PENDING",
                last_customer_activity=timezone.now(),
            )

            for item in items:
                OrderDetail.objects.create(
                    order=order,
                    cake=item.cake,
                    package=item.package,
                    customization=item.customization,
                    quantity=item.quantity,
                    price=item.unit_price,
                    package_inclusion_snapshot=item.package_inclusion_snapshot or [],
                )

            booking = form.save(commit=False)
            booking.order = order
            booking.status = "PENDING"
            booking.delivery_full_name = profile.full_name
            booking.delivery_phone = profile.phone
            booking.delivery_address = (
                f"{profile.house_no}, {profile.street}, {profile.barangay}, {profile.city}, {profile.province}"
            )
            booking.save()

            CartItem.objects.filter(customer=request.user).delete()
            request.session["checkout_confirmed_booking_id"] = booking.id
            log_user_action(
                request.user, f"Checked out cart to order #{order.id}")
            messages.success(
                request, f"Order #{order.id} confirmed. Click Pay Now to continue.")
            return redirect("checkout_cart")

    return render(
        request,
        "orders/checkout_cart.html",
        {
            "form": form,
            "items": items,
            "total": total,
            "confirmed_booking": confirmed_booking,
        },
    )


@login_required
def order_now_package(request, package_id):
    package = get_object_or_404(EventPackage, id=package_id, is_active=True)
    CartItem.objects.filter(customer=request.user).delete()
    CartItem.objects.create(customer=request.user, package=package,
                            quantity=1, unit_price=package.base_price)
    messages.success(request, f"{package.name} ready for checkout.")
    return redirect("checkout_cart")


@login_required
def my_orders(request):
    auto_cancel_stale_orders()
    orders = Order.objects.filter(
        customer=request.user).order_by("-created_at")
    Order.objects.filter(customer=request.user).update(
        last_customer_activity=timezone.now())
    return render(request, "orders/my_orders.html", {"orders": orders})


@login_required
def manager_dashboard(request):
    auto_cancel_stale_orders()
    if not is_manager(request.user):
        return render(request, "access_denied.html")

    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status="PENDING").count()
    confirmed_orders = Order.objects.filter(status="CONFIRMED").count()
    completed_orders = Order.objects.filter(status="COMPLETED").count()
    cancelled_orders = Order.objects.filter(status="CANCELLED").count()

    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status="PENDING").count()
    schedules_count = Schedule.objects.count()
    payments_count = Payment.objects.count()
    notifications_count = CustomerNotification.objects.count()

    recent_orders = Order.objects.select_related(
        "customer").order_by("-created_at")[:10]
    context = {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "confirmed_orders": confirmed_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "schedules_count": schedules_count,
        "payments_count": payments_count,
        "notifications_count": notifications_count,
        "recent_orders": recent_orders,
    }
    return render(request, "manager/dashboard.html", context)


@login_required
def update_order_status(request, order_id, status):
    if not is_manager(request.user):
        return render(request, "access_denied.html")
    order = get_object_or_404(Order, id=order_id)
    valid_status = {choice[0] for choice in Order.STATUS_CHOICES}
    if status not in valid_status:
        messages.error(request, "Invalid order status.")
        return redirect("manager_dashboard")
    order.status = status
    if status == "CANCELLED":
        order.cancelled_at = timezone.now()
    order.save(update_fields=["status", "cancelled_at"]
               if status == "CANCELLED" else ["status"])
    notify_order_update(user=order.customer, order=order,
                        message=f"Order #{order.id} status updated to {status}.")
    log_user_action(
        request.user, f"Updated order #{order.id} status to {status}")
    messages.success(request, f"Order #{order.id} updated to {status}.")
    return redirect("manager_dashboard")
