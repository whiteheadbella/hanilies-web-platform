from django.contrib import admin
from .models import DeliveryProfile

# Register your models here.
admin.site.site_header ="Hanilies Cakeshoppe Administration"
admin.site.site_title = "Hanilies Cakeshoppe Admin"
admin.site.index_title ="Welcome to Hanilies Cakeshoppe Management System"
admin.site.register(DeliveryProfile)
