from django.db import models
from django.contrib.auth.models import User

class UserActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_useractionlogs')
    action = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} @ {self.timestamp}"