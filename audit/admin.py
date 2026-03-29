from django.contrib import admin
from .models import UserActionLog


@admin.register(UserActionLog)
class UserActionLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'action')
    ordering = ('-timestamp',)
