from django.urls import path
from . import views

urlpatterns = [
    path("", views.accounts_hub, name="accounts_home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("navigation-map/", views.navigation_map, name="navigation_map"),
    path("my-account/", views.my_account_dashboard, name="my_account"),
    path("dashboard/", views.accounts_dashboard, name="accounts_dashboard"),
    path("staff/create/", views.create_staff_account,
         name="create_staff_account"),
    path("delivery-profiles/", views.delivery_profiles, name="delivery_profiles"),
    path("add-delivery-profile/", views.add_delivery_profile,
         name="add_delivery_profile"),
    path("delivery-profiles/<int:profile_id>/edit/",
         views.edit_delivery_profile, name="edit_delivery_profile"),
    path("delivery-profiles/<int:profile_id>/delete/",
         views.delete_delivery_profile, name="delete_delivery_profile"),
]
