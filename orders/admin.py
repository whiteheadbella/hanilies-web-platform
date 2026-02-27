from django.contrib import admin
from .models import Booking, CartItem, Order, OrderDetail

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Booking)
admin.site.register(CartItem)
