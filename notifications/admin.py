from django.contrib import admin

from .models import CustomerNotification, UserActionLog

admin.site.register(UserActionLog)
admin.site.register(CustomerNotification)
