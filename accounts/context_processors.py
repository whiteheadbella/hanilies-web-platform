from .permissions import is_manager


def role_flags(request):
    user = getattr(request, "user", None)
    return {
        "is_manager_user": is_manager(user) if user else False,
    }
