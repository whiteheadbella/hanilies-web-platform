from django.db import models
from django.contrib.auth.models import User


class UserActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_useractionlogs')
    action = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} @ {self.timestamp}"


class CustomerNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_notifications")
    order_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=120)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"
