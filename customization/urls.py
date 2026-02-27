from django.urls import path
from .views import customize_cake, remove_addon_item

urlpatterns = [
    path("customize/", customize_cake, name="customize_cake"),
    path("customize/addons/<int:addon_id>/remove/",
         remove_addon_item, name="customization_remove_addon"),
]
