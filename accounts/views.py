from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect, render

from audit.services import log_user_action

from .forms import CustomerRegisterForm, DeliveryProfileForm
from .models import DeliveryProfile
from .permissions import is_manager


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            log_user_action(user, "Logged in")
            if is_manager(user):
                return redirect("manager_dashboard")
            return redirect("customer_home")
    return render(request, "accounts/login.html", {"form": form})


def register_view(request):
    form = CustomerRegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        group, _ = Group.objects.get_or_create(name="Customer")
        user.groups.add(group)
        login(request, user)
        log_user_action(user, "Registered account")
        return redirect("customer_home")
    return render(request, "accounts/register.html", {"form": form})


def logout_view(request):
    log_user_action(request.user, "Logged out")
    logout(request)
    return redirect("customer_home")


@login_required
def accounts_dashboard(request):
    if not is_manager(request.user):
        return render(request, "access_denied.html")
    can_open_admin = request.user.is_superuser or request.user.is_staff
    return render(
        request,
        "accounts/dashboard_tabs.html",
        {"can_open_admin": can_open_admin},
    )


@login_required
def delivery_profiles(request):
    profiles = DeliveryProfile.objects.filter(user=request.user)
    return render(request, "accounts/delivery_profiles.html", {"profiles": profiles})


@login_required
def add_delivery_profile(request):
    form = DeliveryProfileForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        profile = form.save(commit=False)
        profile.user = request.user
        if profile.is_default:
            DeliveryProfile.objects.filter(user=request.user, is_default=True).update(is_default=False)
        profile.save()
        log_user_action(request.user, "Added delivery profile")
        return redirect("delivery_profiles")
    return render(request, "accounts/add_delivery_profile.html", {"form": form})


@login_required
def edit_delivery_profile(request, profile_id):
    profile = get_object_or_404(DeliveryProfile, id=profile_id, user=request.user)
    form = DeliveryProfileForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        profile = form.save(commit=False)
        profile.user = request.user
        if profile.is_default:
            DeliveryProfile.objects.filter(user=request.user, is_default=True).exclude(id=profile.id).update(is_default=False)
        profile.save()
        log_user_action(request.user, f"Updated delivery profile #{profile.id}")
        return redirect("delivery_profiles")
    return render(request, "accounts/add_delivery_profile.html", {"form": form})


@login_required
def delete_delivery_profile(request, profile_id):
    profile = get_object_or_404(DeliveryProfile, id=profile_id, user=request.user)
    if request.method == "POST":
        profile.delete()
        log_user_action(request.user, f"Deleted delivery profile #{profile_id}")
        return redirect("delivery_profiles")
    return render(request, "accounts/confirm_delete_delivery_profile.html", {"profile": profile})
