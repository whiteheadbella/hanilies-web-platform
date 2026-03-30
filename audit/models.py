from django.db import models
from django.contrib.auth.models import User


class UserActionLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='audit_useractionlogs')
    action = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_label = f"User #{self.user_id}" if self.user_id else "Unknown User"
        return f"{user_label} - {self.action} @ {self.timestamp}"
