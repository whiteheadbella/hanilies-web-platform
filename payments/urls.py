from django.urls import path

from .views import create_payment, my_payments

urlpatterns = [
    path("", my_payments, name="my_payments"),
    path("create/<int:booking_id>/", create_payment, name="payment_create"),
]
