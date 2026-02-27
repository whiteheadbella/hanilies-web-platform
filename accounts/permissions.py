from django.core.exceptions import PermissionDenied


def is_manager(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name="Manager").exists())


def is_customer(user):
    return user.is_authenticated and user.groups.filter(name="Customer").exists()


def require_manager(user):
    if not is_manager(user):
        raise PermissionDenied("Manager access required.")
