from .models import UserActionLog


def log_user_action(user, action):
    if user and getattr(user, "is_authenticated", False):
        UserActionLog.objects.create(user=user, action=action)
