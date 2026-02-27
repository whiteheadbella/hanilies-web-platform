from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.accounts_dashboard, name="accounts_dashboard"),
    path("delivery-profiles/", views.delivery_profiles, name="delivery_profiles"),
    path("add-delivery-profile/", views.add_delivery_profile, name="add_delivery_profile"),
    path("delivery-profiles/<int:profile_id>/edit/", views.edit_delivery_profile, name="edit_delivery_profile"),
    path("delivery-profiles/<int:profile_id>/delete/", views.delete_delivery_profile, name="delete_delivery_profile"),
]
