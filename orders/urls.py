from django.urls import path

from .views import (
    add_customization_to_cart,
    add_package_to_cart,
    cart_view,
    checkout_cart,
    checkout_from_customization,
    manager_dashboard,
    my_orders,
    order_now_package,
    update_order_status,
)

urlpatterns = [
    path("", my_orders, name="my_orders"),
    path("cart/", cart_view, name="cart_view"),
    path("cart/add/package/<int:package_id>/", add_package_to_cart, name="add_package_to_cart"),
    path("cart/add/customization/<int:customization_id>/", add_customization_to_cart, name="add_customization_to_cart"),
    path("cart/checkout/", checkout_cart, name="checkout_cart"),
    path("order-now/package/<int:package_id>/", order_now_package, name="order_now_package"),
    path("checkout/<int:customization_id>/", checkout_from_customization, name="checkout_from_customization"),
    path("dashboard/", manager_dashboard, name="orders_dashboard"),
    path("status/<int:order_id>/<str:status>/", update_order_status, name="update_order_status"),
]
