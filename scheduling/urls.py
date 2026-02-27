from django.urls import path

from .views import schedule_delete, schedule_list

urlpatterns = [
    path("", schedule_list, name="schedule_list"),
    path("<int:schedule_id>/delete/", schedule_delete, name="schedule_delete"),
]
