from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from audit.services import log_user_action

from .forms import CustomerRegisterForm, DeliveryProfileForm, StaffCreateForm
from .models import DeliveryProfile
from .permissions import is_manager


def _get_safe_next_url(request):
    next_url = (request.POST.get("next") or request.GET.get("next") or "").strip()
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return ""


def login_view(request):
    next_url = _get_safe_next_url(request)
    if request.user.is_authenticated:
        if next_url:
            return redirect(next_url)
        if is_manager(request.user):
            return redirect("manager_dashboard")
        return redirect("customer_home")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            log_user_action(user, "Logged in")
            if next_url:
                return redirect(next_url)
            if is_manager(user):
                return redirect("manager_dashboard")
            return redirect("customer_home")
    return render(request, "accounts/login.html", {"form": form, "next": next_url})


def register_view(request):
    form = CustomerRegisterForm(request.POST or None)
    next_url = _get_safe_next_url(request)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        group, _ = Group.objects.get_or_create(name="Customer")
        user.groups.add(group)
        login(request, user)
        log_user_action(user, "Registered account")
        if next_url:
            return redirect(next_url)
        return redirect("customer_home")
    return render(request, "accounts/register.html", {"form": form, "next": next_url})


def logout_view(request):
    log_user_action(request.user, "Logged out")
    logout(request)
    return redirect("customer_home")


@login_required
def accounts_hub(request):
    if is_manager(request.user):
        return redirect("accounts_dashboard")
    return redirect("my_account")


@login_required
def navigation_map(request):
    return render(
        request,
        "accounts/navigation_map.html",
        {"is_manager": is_manager(request.user)},
    )


@login_required
def my_account_dashboard(request):
    profile_count = DeliveryProfile.objects.filter(user=request.user).count()
    return render(
        request,
        "accounts/my_account.html",
        {"profile_count": profile_count},
    )


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
def create_staff_account(request):
    if not is_manager(request.user):
        return render(request, "access_denied.html")

    form = StaffCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.is_staff = True
        user.is_superuser = False
        user.save()

        manager_group, _ = Group.objects.get_or_create(name="Manager")
        user.groups.add(manager_group)

        log_user_action(
            request.user,
            f"Created staff account: {user.username}",
        )
        messages.success(
            request,
            f"Staff account '{user.username}' created successfully.",
        )
        return redirect("create_staff_account")

    recent_staff = (
        Group.objects.get_or_create(name="Manager")[0]
        .user_set.filter(is_staff=True)
        .order_by("-date_joined")[:10]
    )

    search_query = (request.GET.get("q") or "").strip()
    customer_results = []
    if search_query:
        customer_results = (
            Group.objects.get_or_create(name="Customer")[0]
            .user_set.filter(
                Q(username__icontains=search_query)
                | Q(email__icontains=search_query)
            )
            .order_by("username")[:25]
        )

    return render(
        request,
        "accounts/create_staff_account.html",
        {
            "form": form,
            "recent_staff": recent_staff,
            "search_query": search_query,
            "customer_results": customer_results,
        },
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
            DeliveryProfile.objects.filter(
                user=request.user, is_default=True).update(is_default=False)
        profile.save()
        log_user_action(request.user, "Added delivery profile")
        return redirect("delivery_profiles")
    return render(request, "accounts/add_delivery_profile.html", {"form": form})


@login_required
def edit_delivery_profile(request, profile_id):
    profile = get_object_or_404(
        DeliveryProfile, id=profile_id, user=request.user)
    form = DeliveryProfileForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        profile = form.save(commit=False)
        profile.user = request.user
        if profile.is_default:
            DeliveryProfile.objects.filter(user=request.user, is_default=True).exclude(
                id=profile.id).update(is_default=False)
        profile.save()
        log_user_action(
            request.user, f"Updated delivery profile #{profile.id}")
        return redirect("delivery_profiles")
    return render(request, "accounts/add_delivery_profile.html", {"form": form})


@login_required
def delete_delivery_profile(request, profile_id):
    profile = get_object_or_404(
        DeliveryProfile, id=profile_id, user=request.user)
    if request.method == "POST":
        profile.delete()
        log_user_action(
            request.user, f"Deleted delivery profile #{profile_id}")
        return redirect("delivery_profiles")
    return render(request, "accounts/confirm_delete_delivery_profile.html", {"profile": profile})
